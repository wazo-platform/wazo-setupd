.PHONY: test-setup test egg-info pull-images setupd

test-setup: egg-info pull-images setupd

test:
	pytest -x

egg-info:
	cd .. && python setup.py egg_info

pull-images:
	docker pull swaggerapi/swagger-validator
	docker pull wazopbx/wait
	docker pull wazopbx/xivo-auth-mock
	docker pull wazopbx/xivo-confd-mock

setupd:
	docker pull python:3.5.3
	docker build -t wazopbx/wazo-setupd ..
	$(MAKE) setupd-test

setupd-test: egg-info
	docker build --no-cache -t wazo-setupd-test -f Dockerfile ..
