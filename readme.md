

# Work in progress!

remoxblock is an xblock that fetches serialized student answers from a
remote host and grades it against staff defined answers on the edx
platform.


# Installation.

There will be more details soon, but development is
currently taking place on the docker based
[devstack](https://github.com/openedx/devstack) install of openedx.

The makefile can deploy to the lms and studio containers by running 

`$ make deploy-local-docker`

currently, however the 

```Make
docker exec -it $(LMS) pip install $(DOCKER_XBLOCK_PATH)/$(XBLOCK)
```

command is not putting the xblock in the correct location, probably
because `docker exec` isn't activating the venv.

