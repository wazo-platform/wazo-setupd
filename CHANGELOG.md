# Changelog

## 22.01

* New read only parameters have been added to the `/status` API:

  * `master_tenant`

* The following route has been restricted to the master tenant:

  * `/config`

## 20.09

* Deprecate SSL configuration

## 20.04

* The following fields have been added to the `/1.0/setup` body

  - engine_rtp_icesupport
  - engine_rtp_stunaddr


## 20.02

* The following fields have been added to the `/1.0/setup` body

  - engine_instance_uuid


## 19.05

* The following fields have been remove from the `/1.0/setup` body

  - engine_entity_name
  - engine_number_start
  - engine_number_end


## 18.14

* New endpoints:
  - POST /1.0/setup

## 18.13

* New endpoints:
  - GET /1.0/api/api.yml
  - GET /1.0/config
  - GET /1.0/status
