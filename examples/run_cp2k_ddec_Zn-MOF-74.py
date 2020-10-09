#!/usr/bin/env python  # pylint: disable=invalid-name
""" Test/example for the DdecCp2kChargesWorkChain"""
from __future__ import absolute_import
from __future__ import print_function
import os
import ase.io
import click

from aiida.engine import run
from aiida.orm import Code, Dict
from aiida.plugins import DataFactory, WorkflowFactory

Cp2kDdecWorkChain = WorkflowFactory('ddec.cp2k_ddec')
StructureData = DataFactory('structure')


@click.command('cli')
@click.argument('cp2k_code_string')
@click.argument('ddec_code_string')
@click.argument('ddec_atdens_path')
def main(cp2k_code_string, ddec_code_string, ddec_atdens_path):
    """Example usage:
    ATDENS_PATH='/home/daniele/Programs/aiida-database/data/chargemol_09_26_2017/atomic_densities/'
    verdi run run_cp2k_ddec_MOF-74.py cp2k@localhost ddec@localhost $ATDENS_PATH
    """
    print('Testing CP2K ENERGY calculation + DDEC on H2O...')

    cp2k_code = Code.get_from_string(cp2k_code_string)
    ddec_code = Code.get_from_string(ddec_code_string)

    thisdir = os.path.dirname(os.path.abspath(__file__))
    structure = StructureData(ase=ase.io.read(os.path.join(thisdir, 'data/Zn-MOF-74.cif')))

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
                    'MGRID': {
                        'NGRIDS': 4,
                        'CUTOFF': 280,
                        'REL_CUTOFF': 30,
                    },
                    'SCF': {
                        'MAX_SCF': 3,  # limited for testing purpose
                    },
                    'XC': {
                        'XC_FUNCTIONAL': {
                            '_': 'PBE',
                        },
                    },
                },
                'SUBSYS': {
                    'KIND': [
                        {
                            '_': 'H',
                            'BASIS_SET': 'SZV-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-PBE'
                        },
                        {
                            '_': 'C',
                            'BASIS_SET': 'SZV-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-PBE'
                        },
                        {
                            '_': 'O',
                            'BASIS_SET': 'SZV-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-PBE'
                        },
                        {
                            '_': 'Zn',
                            'BASIS_SET': 'SZV-MOLOPT-SR-GTH',
                            'POTENTIAL': 'GTH-PBE'
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
            'label': 'test-MOF-74'
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
