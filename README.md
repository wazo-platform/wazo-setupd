# wazo-setupd

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-setupd)](https://jenkins.wazo.community/job/wazo-setupd)

A micro service to initialize a [Wazo](http://wazo.community) Engine.


## Docker

The official docker image for this service is `wazoplatform/wazo-setupd`.


### Getting the image

To download the latest image from the docker hub

```sh
docker pull wazoplatform/wazo-setupd
```


### Running wazo-setupd

```sh
docker run wazoplatform/wazo-setupd
```

### Building the image

Building the docker image:

```sh
docker build -t wazoplatform/wazo-setupd .
```
