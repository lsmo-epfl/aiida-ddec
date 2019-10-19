#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Test/example for the DdecCp2kChargesWorkChain"""

from __future__ import print_function
from __future__ import absolute_import

import click
import ase.build

from aiida.engine import run
from aiida.orm import Code, Dict
from aiida.plugins import DataFactory, WorkflowFactory

Cp2kDdecWorkChain = WorkflowFactory('ddec.cp2k_ddec')  # pylint: disable=invalid-name
StructureData = DataFactory('structure')  # pylint: disable=invalid-name


@click.command('cli')
@click.argument('cp2k_code_string')
@click.argument('ddec_code_string')
@click.argument('ddec_atdens_path')
def main(cp2k_code_string, ddec_code_string, ddec_atdens_path):
    """Example usage:
    ATDENS_PATH='/home/daniele/Programs/aiida-database/data/chargemol_09_26_2017/atomic_densities/'
    verdi run run_cp2k_ddec_h2o.py cp2k-5.1@localhost ddec@localhost $ATDENS_PATH
    """
    print('Testing CP2K ENERGY calculation + DDEC on H2O...')

    cp2k_code = Code.get_from_string(cp2k_code_string)
    ddec_code = Code.get_from_string(ddec_code_string)

    atoms = ase.build.molecule('H2O')
    atoms.center(vacuum=2.0)
    structure = StructureData(ase=atoms)

    cp2k_options = {
        'resources': {
            'num_machines': 1
        },
        'max_wallclock_seconds': 10 * 60,
        'withmpi': True,
    }

    ddec_options = {
        'resources': {
            'num_machines': 1
        },
        'max_wallclock_seconds': 10 * 60,
        'withmpi': False,
    }

    cp2k_params = Dict(
        dict={
            'FORCE_EVAL': {
                'METHOD': 'Quickstep',
                'DFT': {
                    'BASIS_SET_FILE_NAME': 'BASIS_MOLOPT',
                    'QS': {
                        'EPS_DEFAULT': 1.0e-12,
                        'WF_INTERPOLATION': 'ps',
                        'EXTRAPOLATION_ORDER': 3,
                    },
                    'MGRID': {
                        'NGRIDS': 4,
                        'CUTOFF': 280,
                        'REL_CUTOFF': 30,
                    },
                    'XC': {
                        'XC_FUNCTIONAL': {
                            '_': 'LDA',
                        },
                    },
                    'POISSON': {
                        'PERIODIC': 'none',
                        'PSOLVER': 'MT',
                    },
                },
                'SUBSYS': {
                    'KIND': [
                        {
                            '_': 'O',
                            'BASIS_SET': 'DZVP-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-LDA-q6'
                        },
                        {
                            '_': 'H',
                            'BASIS_SET': 'DZVP-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-LDA-q1'
                        },
                    ],
                },
            }
        }
    )

    ddec_params = Dict(
        dict={
            'net charge': 0.0,
            'charge type': 'DDEC6',
            'periodicity along A, B, and C vectors': [True, True, True],
            'compute BOs': False,
            'atomic densities directory complete path': ddec_atdens_path,
            'input filename': 'valence_density',
        }
    )

    inputs = {
        'metadata': {
            'label': 'test-h2o'
        },
        'cp2k_base': {
            'cp2k': {
                'structure': structure,
                'parameters': cp2k_params,
                'code': cp2k_code,
                'metadata': {
                    'options': cp2k_options,
                }
            }
        },
        'ddec': {
            'parameters': ddec_params,
            'code': ddec_code,
            'metadata': {
                'options': ddec_options,
            }
        }
    }

    run(Cp2kDdecWorkChain, **inputs)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
