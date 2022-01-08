#!/usr/bin/env bash

# this is executed inside both the lms and studio docker containers.

source /edx/app/edxapp/venvs/edxapp/bin/activate
cd /edx/app/edxapp/edx-platform/src
pip install ./remoxblock
