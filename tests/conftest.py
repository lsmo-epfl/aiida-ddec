# -*- coding: utf-8 -*-
"""
For pytest
initialise a test database and profile
"""
from __future__ import absolute_import
import tempfile
import shutil
import os
import pytest
from aiida.manage.fixtures import fixture_manager
import aiida_ddec.tests as dt


def get_backend_str():
    """ Return database backend string.
    Reads from 'TEST_AIIDA_BACKEND' environment variable.
    Defaults to django backend.
    """
    from aiida.backends.profile import BACKEND_DJANGO, BACKEND_SQLA
    backend_env = os.environ.get('TEST_AIIDA_BACKEND', BACKEND_DJANGO)
    if backend_env in (BACKEND_DJANGO, BACKEND_SQLA):
        return backend_env

    raise ValueError("Unknown backend '{}' read from TEST_AIIDA_BACKEND environment variable".format(backend_env))


@pytest.fixture(scope='session')
def aiida_profile():
    """setup a test profile for the duration of the tests"""
    with fixture_manager() as fixture_mgr:
        yield fixture_mgr


@pytest.fixture(scope='function')
def clear_database(aiida_profile):  # pylint: disable=redefined-outer-name
    """clear the database after each test"""
    yield
    aiida_profile.reset_db()


@pytest.fixture(scope='function')
def new_workdir():
    """get a new temporary folder to use as the computer's workdir"""
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture(scope='function')
def basic_options_cp2k():
    """
    set some default options
    """
    default_cp2k_options = {  # pylint: disable=invalid-name
        'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1},
        'max_wallclock_seconds': 3 * 60 * 60,
        'withmpi': False,
    }
    return default_cp2k_options


@pytest.fixture(scope='function')
def ddec_code(aiida_profile):  # pylint: disable=unused-argument, redefined-outer-name
    return dt.get_code(entry_point='ddec')


@pytest.fixture(scope='function')
def cp2k_code(aiida_profile):  # pylint: disable=unused-argument, redefined-outer-name
    return dt.get_code(entry_point='cp2k')


@pytest.fixture(scope='function')
def basic_options_ddec():
    """
    set some default options
    """
    default_ddec_options = {  # pylint: disable=invalid-name
        'resources': {'num_machines': 1, 'num_mpiprocs_per_machine': 1},
        'max_wallclock_seconds': 3 * 60 * 60,
        'withmpi': False,
    }
    return default_ddec_options
