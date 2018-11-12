The RESTful API is implemented using python webframework Flask. This API has three resources implemented namely 

```
GET /getRecentItem
GET /getBrandsCount
GET /getItemsbyColor
```

The input parameters are provided using Query String parameters which meands the requests for three APIs should be in the following format:

`GET http://<endpoint>/getRecentItem?date=<yyyy-mm-dd>`

`GET http://<endpoint>/getBrandsCount?date=<yyyy-mm-dd>`

`GET http://<endpoint>/getRecentItem?color=<color>`

The API program covers cases of user errors such as missing parmeters, wrong format input, key out of range.

Ideally, this Docker container that packages flask application can be run on Kubernetes but for the sake of simplicity the continer is being run on  single EC2 instance of type `t2.micro` using Amazon Linux AMI.

The Docker image for this application is pulled from my public DockerHub account

**$** `docker pull bhargavpss/madstreetden:prod`

**$** `docker run -dit -p 80:5000 --restart=on-failure bhargavpss/madstreetden:prod`

This Instance can be put under a LoadBalancer or AutoScalingGroup for fault-tolerance, service-discovery and SSL purposes.

