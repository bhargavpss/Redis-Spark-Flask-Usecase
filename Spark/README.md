The following are the transformations we need to do before insertion of data:

- Retrieve only columns with names id, brand, color and dateAdded
- Remove rows with null values
- Remove duplicates

All of the above are implemented using pysprark.sql methods 

`data = data.select('id','brand','colors','dateAdded').dropna().dropDuplicates().orderBy(data.dateAdded)`

