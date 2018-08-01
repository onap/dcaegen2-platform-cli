# Vagrant for DCAE runtime

This project provides component developers the means to stand up their own local DCAE runtime environment to do local onboarding through the dcae-cli.  [Vagrant](https://www.vagrantup.com/) is the technology used and is required to the provided Vagrantfile.

## Pre-req

1. Install Docker
2. Install Vagrant
3. Install VirtualBox
4. Add the following to your `/etc/hosts` (or equivalent):

```
127.0.0.1 vagrant-dcae
```

## Run

Clone the [dcaegen2.platform.cli](https://gerrit.onap.org/r/#/admin/projects/dcaegen2/platform/cli) project.

```
cd vagrant
vagrant up
```

Open the following [Consul link](http://vagrant-dcae:8500/ui) to verify that Consul is running and review the listed services by clicking on each:

* [`config_binding_service`](http://vagrant-dcae:8500/ui/#/vagrant-dcae/services/config_binding_service)
* [`onboardingdb`](http://vagrant-dcae:8500/ui/#/vagrant-dcae/services/onboardingdb)

NOTE: The vagrant DCAE runtime requires several ports on the host machine.  See the [Vagrantfile](Vagrantfile) for all the lines that contain `forwarded_port`.

## Post run

Post run involves setting up the dcae-cli to work with the newly instantiated local DCAE runtime environment.

### Install

First install [dcae-cli](https://pypi.org/project/onap-dcae-cli/).

Even if you have already installed dcae-cli before, please take the time now to upgrade:

```
pip install --upgrade onap-dcae-cli
```

### Configure

Type the following command and you will be taken through a series of prompts to configure dcae-cli.  For the most part, use the responses shown below except for the *user id*:

```
$ dcae_cli --reinit
Warning! Reinitializing your dcae-cli configuration
Please enter the remote server url: https://git.onap.org/dcaegen2/platform/cli/plain
Could not download initial configuration from remote server. Attempt manually setting up? [y/N]: y
Please enter your user id: <your user id>
Now we need to set up access to the onboarding catalog
Please enter the onboarding catalog hostname: vagrant-dcae
Please enter the onboarding catalog user: postgres
Please enter the onboarding catalog password: onap123
Could not download initial profiles from remote server. Set empty default? [y/N]: y
Reinitialize done
```

#### Profile

Next you will need to setup your default profile.

Running the following, you should see the following:

```
$ dcae_cli profiles show default
{
    "cdap_broker": "cdap_broker",
    "config_binding_service": "config_binding_service",
    "consul_host": "",
    "docker_host": ""
}
```

You need to set `consul_host` and `docker_host` by running the following:

```
$ dcae_cli profiles set default consul_host vagrant-dcae
$ dcae_cli profiles set default docker_host vagrant-dcae:2376
```

Repeating `dcae_cli profiles show default` should show those parameters now filled.

### Run

You must point your Docker client to the Docker engine running in the VirtualBox instance by doing the following:

```
export DOCKER_HOST="tcp://vagrant-dcae:2376"
```

You must have this environment variable set everytime before you run the dcae-cli.

## TODO

* There is a known issue where Consul does not recover after doing a `vagrant reload`.  It get
