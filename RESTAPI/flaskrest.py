from flask import Flask
from flask import request
from flask import jsonify
from redis.exceptions import WatchError
import redis

hostname = 'madstreetden-001.a1hyc5.0001.use1.cache.amazonaws.com'
port = 6379

r = redis.Redis(host=hostname, port=port)

app = Flask(__name__)

@app.route("/getRecentItem")
def getRecentItem():
	
	a = request.args
	if 'date' not in a: 
		return jsonify({"body":"Missing required parameters: date","HTTP_Status": "404_BAD_REQUEST"})
	elif len(a['date']) != 10 or a['date'][4] != '-' or a['date'][7] != '-':
		return jsonify({"body":"date should be in yyyy-mm-dd format","HTTP_Status": "404_BAD_REQUEST"})
	else:
		date = a.get('date')

        pipe = r.pipeline(transaction=True)

        while 1:
                try:
                        pipe.watch('{}:id:latest'.format(date),'{}:brand:latest'.format(date),'{}:color:latest'.format(date))
                        pipe.multi()
                        pipe.lrange('{}:id:latest'.format(date),0,0)
                        pipe.lrange('{}:brand:latest'.format(date),0,0)
                        pipe.lrange('{}:color:latest'.format(date),0,0)

                        value = pipe.execute() # Enforcing Transactional Updates
                        break
                except WatchError:
                        continue
	
	
	for i in range(0,len(value)):
		if value[i] == []:
			return jsonify({"body":"key not found with given date:{}".format(date),"HTTP_Status":"404_BAD_REQUEST"})
        
	result = {}
        result['id'] = value[0][0]
        result['brand'] = value[1][0]
        result['color'] = value[2][0]

        return jsonify({"body":result, "HTTP_Status": "200_OK"})

@app.route("/getBrandsCount")
def getBrandsCount():
	a = request.args
	if 'date' not in a:
		return jsonify({"body":"Missing required parameters: date","HTTP_Status": "404_BAD_REQUEST"})
        elif len(a['date']) != 10 or a['date'][4] != '-' or a['date'][7] != '-':
                return jsonify({"body":"date should be in yyyy-mm-dd format","HTTP_Status": "404_BAD_REQUEST"})
        else:
                date = a.get('date')

	pipe = r.pipeline(transaction=True)
	while 1:
		try:
			pipe.watch('{}:brandcount'.format(date))
			pipe.multi()		
			pipe.zrange('{}:brandcount'.format(date),0,-1,desc=True,withscores=True)
	
			value = pipe.execute()	# Enforcing Transactional Updates
			break
		except WatchError:
			continue
			
	for i in range(0,len(value)):
                if value[i] == []:
                        return jsonify({"body":"key not found with given date:{}".format(date),"HTTP_Status": "400_BAD_REQUEST"})

	result = []
	for i in value[0]:
			entry = {}
			entry['brand'] = i[0]
			entry['count'] = i[1]
			result.append(entry)

	return jsonify({"body":result, "HTTP_Status": "200_OK"})

@app.route("/getItemsbyColor")
def getItemsbyColor():
	a = request.args
	if 'color' not in a:
		return jsonify({"body":"Missing Required Parameters: color", "HTTP_Status": "400_BAD_REQUEST"})
	else:
		color = a.get('color')

	pipe = r.pipeline(transaction=True)
	while 1:
		try:
			
			pipe.watch('{}:id:latest10'.format(color),'{}:brand:latest10'.format(color),'{}:color:latest10'.format(color),'{}:dateAdded:latest10'.format(color))
			pipe.multi()
			pipe.lrange('{}:id:latest10'.format(color),0,9)
			pipe.lrange('{}:brand:latest10'.format(color),0,9)
			pipe.lrange('{}:color:latest10'.format(color),0,9)
			pipe.lrange('{}:dateAdded:latest10'.format(color),0,9)

			value = pipe.execute() # Enforcing Transactional Updates
			break
		except WatchError:
			continue
			
	for i in range(0,len(value)): # Key is not found if value has empty lists
                if value[i] == []:
                        return jsonify({"body":"key not found with given color:{}".format(color), "HTTP_Status": "400_BAD_REQUEST"})

	result = []
	
	for i in range(0,len(value[0])):
			entry = {}
			entry['id'] = value[0][i]
			entry['brand'] = value[1][i]
			entry['color'] = value[2][i]
			entry['dateAdded'] = value[3][i]
			result.append(entry)
	return jsonify({"body":result, "HTTP_Status": "200_OK"})

if __name__ == "__main__":
	app.run(host='0.0.0.0')
