from pyspark.sql import SQLContext
from pyspark import SparkContext
import redis
from redis.exceptions import WatchError

hostname = 'madstreetden-001.a1hyc5.0001.use1.cache.amazonaws.com'
port = 6379

r = redis.Redis(host=hostname, port=port)
pipe = r.pipeline(transaction=True)

sc = SparkContext()
sqlContext = SQLContext(sc)

data = sqlContext.read.format('csv').options(header='true', inferSchema='false').load('/home/ec2-user/shoesdata.csv')

data = data.select('id','brand','colors','dateAdded').dropna().dropDuplicates().orderBy(data.dateAdded)

for row in data.collect():

	(brand, color, dateAdded,date) = (row['brand'], row['colors'],row['dateAdded'],row['dateAdded'].split('T')[0])

	head = ['id', 'brand', 'color', 'dateAdded'] # CSV Header

	L = [] 
	
	for i in head[0:3]:
        	L.append('{}:{}:latest'.format(date, i))
	
	for i in head:
	        L.append('{}:{}:latest10'.format(color,i))

        L.append('{}:brandcount'.format(date)) # List of keys to be watched

        while 1:
                try:
                        pipe.watch(*L)         # Enforcing Atomic Transaction

                        pipe.multi()           # Start the Transaction
			"""
                        for i in head[0:3]:
                                pipe.lpush('{}:{}:latest'.format(date, i),row[head.index(i)])
                                pipe.ltrim('{}:{}:latest'.format(date, i),0,0)
			"""
			hashinput = { 'id' : row[0], 'brand' : row[1], 'color' : row[2] }
			pipe.hmset('{}:latest'.format(date), hashinput)
                        for i in head:
                                pipe.lpush('{}:{}:latest10'.format(color,i),row[head.index(i)])
                                pipe.ltrim('{}:{}:latest10'.format(color,i),0,9)

                        pipe.zincrby('{}:brandcount'.format(date), brand, amount=1)

                        value = pipe.execute()  # End of Transaction

                        break

                except WatchError:
                        continue	

print 'Latest insertion response: \n {}'.format(value)

