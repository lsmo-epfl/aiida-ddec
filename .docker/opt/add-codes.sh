#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

# Debugging
set -x

# Environment
export SHELL=/bin/bash

# Install the ddec and cp2k codes
DDEC_FOLDER=/home/aiida/code/aiida-ddec

verdi code show ddec@localhost || verdi code setup --config ${DDEC_FOLDER}/.docker/ddec-code.yml --non-interactive
verdi code show cp2k@localhost || verdi code setup --config ${DDEC_FOLDER}/.docker/cp2k-code.yml --non-interactive
