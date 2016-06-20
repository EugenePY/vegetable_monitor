<<<<<<< HEAD
# My Second Bluemix Program.

##### *This module trying to deploy a web crawler to Bluemix.

The crawler is written in Python. So the runtime Python(or Pypy) ver 2.7 is required.

There are two ways to do this.

1. Writing a dockerfile(Docker). 
2. Writing a Python buildpack.(Cloud Foundary) add Conda instead pip.
3. Openstack.

In the repo we use the second method.

We demo above approach to deploy a simple PTT web crawler on IBM Bluemix and dump the 
document on the Cloundant NoSQL database.

Bluemix is using Cloud Foundary, Docker conatainer, and Openstack to deploy
your local application to the Bluemix Cloud.

Since Cloud Foundary providing a very usful command line tool, we can easily 
deploy the application with your terminal command line.

#### Pre-requirement
Please install the following tool to finish the tutorial.

* [Cloud Foundary command line interface](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html)
* [IBM Bluemix container Cloud Foundary command line plug-in](https://console.ng.bluemix.net/docs/containers/container_cli_cfic.html) 
* [Docker](https://docs.docker.com/mac)

#### Tutorial

###### Deploy a web crawler program via deault Python Buildpack 

In here we use a the sample git repository from IBM.

clone the repo first.
```bash
git clone https://hub.jazz.net/git/rugeneibm/crawler-database 
```
The basic idea of deploying the app on Bluemix is using the buildpack to setup 
your runtime enviorment and run the application. 

The structure of the repo is very simple. The repo contains {hello.py, 
Profile, manifest.yml, requirements.txt}

What these file do is, 
	procfile is inital the app
	manifest.yml is describing the container's information which containing the 
	application.
	requirements.txt is containing the application dependency.

we can simily deploy the application by following commnad.
```bash
cf login [-a API_URL] [-u USERNAME] [-p PASSWORD] [-o ORG] [-s SPACE]
./deploy.sh
```
###### Deploy connect to a service with python application

We now demo how to create a Cloudant Non-SQL service bind to a simlple python program.
The program creates a data and sent the data to the Database through http request. 

###### create a testing env..
since it is quite slow for debuging when you need to recompile the application. 

###### Deploy a docker image 

We pull a Hadoop docker image and push to the Bluemix.
**TODO**

###### Deploy a docker cluster via Docker Swarm
**TODO**

###### Example: Distributed Tensorflow with Bluemix
**TODO**

###### Hybrid Cloud GPU cluster
**TODO**

###### Bluemix From Platform as a Service to Infrastructure as a Service.
**TODO**

=======
This README.md file is displayed on your project page. You should edit this 
file to describe your project, including instructions for building and 
running the project, pointers to the license under which you are making the 
project available, and anything else you think would be useful for others to
know.

We have created an empty license.txt file for you. Well, actually, it says,
"<Replace this text with the license you've chosen for your project.>" We 
recommend you edit this and include text for license terms under which you're
making your code available. A good resource for open source licenses is the 
[Open Source Initiative](http://opensource.org/).

Be sure to update your project's profile with a short description and 
eye-catching graphic.

Finally, consider defining some sprints and work items in Track & Plan to give 
interested developers a sense of your cadence and upcoming enhancements.
>>>>>>> bluemix/master
