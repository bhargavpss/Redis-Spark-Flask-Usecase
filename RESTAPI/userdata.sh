#!/bin/bash

{

yum install docker -y

service docker start

docker run -dit -p 80:5000 --restart=on-failure bhargavpss/madstreetden:prod

} | tee /tmp/userdata.log

