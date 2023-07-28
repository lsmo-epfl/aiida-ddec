"""
For pytest
initialise a test database and profile
"""
from __future__ import absolute_import

import os
from pathlib import Path

import pytest

from aiida_ddec.calculations import DENSITY_DIR_EXTRA, DENSITY_DIR_SYMLINK

EXAMPLES_DATA_DIR = Path(__file__).resolve().parent / "examples" / "data"
DATA_DIR = Path(__file__).resolve().parent / "tests" / "data"


@pytest.fixture(scope="function", autouse=True)
def clear_database_auto(clear_database):  # pylint: disable=unused-argument
    """Automatically clear database in between tests."""


@pytest.fixture(scope="function")
def ddec_code(mock_code_factory):
    """Create mocked "DDEC" code."""
    code = mock_code_factory(
        label="chargemol-09_26_2017",
        data_dir_abspath=DATA_DIR,
        entry_point="ddec",
        # files *not* to copy into the data directory
        ignore_paths=("_aiidasubmit.sh", "*.cube", DENSITY_DIR_SYMLINK),
    )

    # Set atomic density directory extra on code
    density_dir = os.environ.get(DENSITY_DIR_EXTRA)
    if not density_dir:
        density_dir = EXAMPLES_DATA_DIR / "ddec" / "atomic_densities"
    code.set_extra(DENSITY_DIR_EXTRA, str(density_dir))

    return code


@pytest.fixture(scope="function")
def cp2k_code(mock_code_factory):
    """Create mocked "cp2k" code."""
    return mock_code_factory(
        label="cp2k-7.1",
        data_dir_abspath=DATA_DIR,
        entry_point="cp2k",
        # files *not* to copy into the data directory
        ignore_paths=(
            "_aiidasubmit.sh",
            "BASIS_MOLOPT",
            "GTH_POTENTIALS",
            "dftd3.dat",
            "*.bak*",
            "*.wfn",
        ),
    )
