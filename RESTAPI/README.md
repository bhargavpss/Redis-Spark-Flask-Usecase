Ideally, this Docker container that packages flask application can be run on Kubernetes but for the sake of simplicity the continer is being run on  single EC2 instance of type `t2.micro` using Amazon Linux AMI.

The Docker image for this application is pulled from my public DockerHub account

**$** `docker pull bhargavpss/madstreetden:prod`

**$** `docker run -dit -p 80:5000 --restart=on-failure bhargavpss/madstreetden:prod`

This Instance can be put under a LoadBalancer or AutoScalingGroup for fault-tolerance, service-discovery and SSL purposes.

