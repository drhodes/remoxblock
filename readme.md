
# Work in progress!

remoxblock is an xblock that fetches serialized student answers from a
remote host and grades it against staff defined answers on the edx
platform.


# Installation.

There will be more details soon, but development is
currently taking place on the docker based
[devstack](https://github.com/openedx/devstack) install of openedx.

The makefile can deploy the xblock to the the lms and studio
containers by running

`$ make deploy-local-docker`

