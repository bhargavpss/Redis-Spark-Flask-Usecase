Redis is implemented using a managed service AWS ElasticCache Redis. For the sake of simplicity, a single node implementation of Redis is choosen.

We have three API requests accessing the data stored in Redis namely `/getRecentItem`, `/getBrandsCount` and `/getItemsbyColor`. The keys and the data types are designed strictly to store only the data that is acccessed by the queries.

## Key Design

The data is already sorted in ascending order by the 'dateAdded' column as you cn see in the SampleDataAfterTransformation.csv (Recent entries in the end)

The dateAdded colum is in the format `yyyy-mm-ddThh:mm:ssZ` but the API requests are only performing queries based on Date `yyyy-mm-dd`. So, the original `dateAdded` column is only used for sorting the data and not included in ny of the key names.

### /getRecentItem
```
Input: Date
Output: id, color, brand
```
We can make use of hashes for this scenario. We can have one key of type hash for every date. Every new insertion of data into Redis will oveewrite the values of the fields `'id', 'brand', 'color'` in the hash.

To write values of multiple keys at once, we can use `HMSET` command

```
>>> hmset mykey field1 value1 field2 value2
```

The hash would have key name in the following format:
`<date>:latest`

Example keys: 
```
2017-03-28:latest
2016-04-09:latest
```

### /getItembyColor
```
Input: Color
Output: (id, color, brand, DateAdded) for latest 10 items of the given color
```
Lists(LinkedLists) in redis are popular data types to store the latest items. In this scenario, to get the 10 latest items for a given color we can implement capped lists. Capped lists can be implemented by using LPUSH and LTRIM commands are used together

In this case, we can use capped lists of length 10 to store the latest 10 items for a particular color. 

```
>>> lpush mykey value
>>> ltrim mykey 0 9
```

This way of implementing capped lists ensure that the list always has only one element which has to be the most recently updated one.

For our scenario, we can use three capped lists for a color with each one of them storing the values of id, brand and dateAdded. Every time a new insertion occurs, the old values in these lists are replaced by the most recent items. 

The lists would have key names in the following format:
 `<color>:<column_name>:latest10`
 
 Example keys: 
```
Red:id:latest10
Red:brand:latest10
Red:DateAdded:latest10
```
### /getBrandsCount
```
Input: Date
Output: Count of each brand for a given day in descending order
```

This case perfectly fits the usage patterns of SortedSets in Redis. Each element in the SortedSets have a score associated with it which can be incremented atomically using ZINCRBY command. 

In this scenario the element can be the name of the brand with count as their associated scores. These SortedSets can configured to be returned in descending order using following command:

`zrange mykey 0 -1` or 
`zrevrange mykey 0 -1`



The key name for these SortedSets are in the following format
`<date>:brandcount`

Example key: `2017-03-28:brandcount`


There we have 5 keys in total that are updated upon insertion of every item namely,
`<date>:latest`,
`<date>:brandcount`,
`<date>:id:latest10`,
`<date>:brand:latest10`,
`<date>:dateAdded:latest10`,

With this design, we ensure that data is not redundantly stored in the database that is not used by the queries. But one potential drawback for this design is that there is no enforcement of transactional consistency from the database side. 

But Redis has very good features in its client libraries and CLI untilies to ensure atomic transactions. In our usecase, we leveraged pipeline() and watch() functions of python's redis module to ensure consistency atomicity of the transactions reliably.










