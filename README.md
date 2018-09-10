# HLF config generator

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

This generator allows to easily experiment with different
configurations of Hyperledger Fabric.
It allows to specifiy the number of organization, peer per organization,
orderer instances and fabric-cli instances.

It will generate config files and scripts that can be
directly used to easily generate a working setup of
Hyperledger Fabric on docker with

* one channel per organization
* one global channel shared across all organizations

It also deploys kafka (with zookeeper) for the ordering service.

# Usage

Make sure to have a recent version of the following tools installed:

* docker
* docker-compose
* python3
* virtualenv

```bash
git clone https://github.com/kudelskisecurity/hlf-cfg-gen.git && cd hlf-cfg-gen
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
./hlf-gen.py --help
```

Ensure that the current user is able to use docker by adding it
to the docker group
```bash
$ sudo usermod -aG docker $(whoami)
```

Retrieve HLF bootstrap script.
This will download all needed docker images as well as the different
binaries needed by HLF
```bash
# for example getting the HLF bootstrap script for version 1.1
$ wget https://raw.githubusercontent.com/hyperledger/fabric/release-1.1/scripts/bootstrap.sh
$ chmod +x bootstrap.sh
$ ./bootstrap.sh

# default configs provided by the bootstrap script can be safely removed
$ rm -rf config
```

Make sure the binaries installed by the bootstrap script are in your path
```bash
$ export PATH="`pwd`/bin/:${PATH}"
```

Also ensure no firewall rules are blocking the ports used
by the different components of HLF.

Generate all the configs
```bash
$ ./hlf-gen.py gen
$ cd configs
```

Generate HLF crypto configs and channels blocks
```bash
$ ./generate.sh
```

Then start the different containers
```bash
$ ./start.sh
```

Ensure no container has failed
```bash
$ docker ps --filter status=exited
```

And initiate the different channels with
```bash
$ ./channels.sh
```

That's it, your blockchain is up!

List for example the different channels (adapt if you use a different domain than `example.com`):
```bash
$ docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org1.example.com/msp peer0.org1.example.com peer channel list
Channels peers has joined:
org1chan
commonchannel
```

For more peer commands see <https://hyperledger-fabric.readthedocs.io/en/release-1.1/peer-commands.html>.

HLF network can be stopped using the `stop.sh` script
```bash
$ ./stop.sh
```

# Cleaning

The following commands will clean all containers, volumes and networks
in docker, use with care
```bash
$ docker stop `docker ps -a | awk '{if (NR!=1) {print $1}}'`
$ docker rm `docker ps -a | awk '{if (NR!=1) {print $1}}'`
$ docker volume rm `docker volume ls | awk '{if (NR!=1) {print $2}}'`
$ docker network rm `docker network ls | awk '{if (NR!=1) {print $2}}'`
```

# References

* https://hyperledger-fabric.readthedocs.io

# Contributing

Feel free to open an issue or do a PR.

# License and Copyright

Copyright(c) 2018 Nagravision SA.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
