#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

# Run precommit
pre-commit run --all-files || ( git status --short ; git diff ; exit 1 )

# Run pytest
pytest

# run single calculation tests

#  run workflows

# if all tests ran successfully
echo "All tests have passed :-)"
