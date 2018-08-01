# ============LICENSE_START=======================================================
# org.onap.dcae
# ================================================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END=========================================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.

#!/usr/bin/env bash

# abort on error
set -e

# Update and upgrade apt packages
apt-get update
apt-get upgrade -y

# Hostname vagrant-dcae will be used to refer to this vagrant machine. This is
# important for certificates.
echo '127.0.0.1 vagrant-dcae' >>/etc/hosts

# Generate self-signed certs for docker registry
mkdir /certs
openssl req \
  -newkey rsa:4096 -nodes -sha256 -keyout /certs/domain.key \
  -x509 -days 365 -out /certs/domain.crt \
  -subj "/C=US/ST=New York/L=New York/O=ONAP/CN=vagrant-dcae"

# Install and setup docker
apt-get install -y -q docker.io docker-compose
echo 'DOCKER_OPTS="--raw-logs -H tcp://0.0.0.0:2376 -H unix:///var/run/docker.sock"' >>/etc/default/docker
systemctl restart docker

export MYIP=$(ip address show enp0s3 | grep 'inet ' | sed -e 's/^.*inet //' -e 's/\/.*$//' | tr -d '\n')
cd /srv/dcae-onboarding

docker-compose up -d
# REVIEW: There seems to be a race condition where registrator must fully
# come up before the config binding service should start. Put in a arbitrary
# sleep then restarting containers as a work around.
sleep 10
docker restart config_binding_service
docker restart onboardingdb
