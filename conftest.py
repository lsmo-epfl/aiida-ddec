"""
For pytest
initialise a test database and profile
"""
from __future__ import absolute_import
import pytest
from tests import DATA_DIR

pytest_plugins = ['aiida.manage.tests.pytest_fixtures', 'aiida_testing.mock_code']  # pylint: disable=invalid-name


@pytest.fixture(scope='function', autouse=True)
def clear_database_auto(clear_database):  # pylint: disable=unused-argument
    """Automatically clear database in between tests."""


@pytest.fixture(scope='function')
def ddec_code(mock_code_factory):
    """Create mocked "zeo++" code."""
    return mock_code_factory(
        label='chargemol-09_26_2017',
        data_dir_abspath=DATA_DIR,
        entry_point='ddec',
        # files *not* to copy into the data directory
        ignore_paths=('_aiidasubmit.sh', 'UFF.rad')
    )


@pytest.fixture(scope='function')
def cp2k_code(mock_code_factory):
    """Create mocked "cp2k" code."""
    return mock_code_factory(
        label='cp2k-7.1',
        data_dir_abspath=DATA_DIR,
        entry_point='cp2k',
        # files *not* to copy into the data directory
        ignore_paths=('_aiidasubmit.sh', 'BASIS_MOLOPT', 'GTH_POTENTIALS', 'dftd3.dat', '*.bak*')
    )


@pytest.fixture(scope='function')
def basic_options():
    """Return basic calculation options."""
    options = {
        'max_wallclock_seconds': 120,
    }
    return options
