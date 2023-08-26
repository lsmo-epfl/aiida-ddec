#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

# Debugging
set -x

# Environment
export SHELL=/bin/bash

# Install the AiiDA codes.
verdi code show cp2k@localhost || \
    verdi code create core.code.installed -n --config /opt/aiida-ddec/.docker/cp2k@localhost.yml
verdi code show ddec@localhost || \
    verdi code create core.code.installed -n --config /opt/aiida-ddec/.docker/ddec@localhost.yml

verdi run /opt/aiida-ddec/.docker/add_ddec_extra.py
