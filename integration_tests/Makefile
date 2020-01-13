test-setup: egg-info setupd setupd-test deployd webhookd

test:
	pytest -x

egg-info:
	cd .. && python setup.py egg_info

setupd:
	docker build -t wazopbx/wazo-setupd ..

setupd-test: egg-info
	docker build --no-cache -t wazo-setupd-test -f Dockerfile-setupd ..

deployd:
	docker build -t wazopbx/wazo-deployd-mock -f docker/wazo-deployd-mock/Dockerfile docker/wazo-deployd-mock

webhookd:
	docker build -t wazopbx/wazo-webhookd-mock -f docker/wazo-webhookd-mock/Dockerfile docker/wazo-webhookd-mock

.PHONY: test-setup test egg-info setupd setupd-test deployd webhookd
