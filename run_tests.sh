#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

# Run precommit
pre-commit run --all-files || ( git status --short ; git diff ; exit 1 )

# Run pytest
# pytest

# run workflows
verdi run examples/run_cp2k_ddec_h2o.py cp2k@localhost ddec@localhost  ~/code/chargemol_09_26_2017/atomic_densities/
verdi run examples/run_cp2k_ddec_Zn-MOF-74.py cp2k@localhost ddec@localhost  ~/code/chargemol_09_26_2017/atomic_densities/

# if all tests ran successfully
echo "All tests have passed :-)"
