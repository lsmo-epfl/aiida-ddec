#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example calculation on Cu-MOF-74"""
from __future__ import print_function
from __future__ import absolute_import
import click
from aiida.orm.utils import load_node
from aiida.engine import submit
from aiida.orm import Code, Dict
from aiida_ddec.calculations import DdecCalculation

input_dict = {  # pylint: disable=invalid-name
    'net charge': 0.0,
    'charge type': 'DDEC6',
    'periodicity along A, B, and C vectors': [True, True, True],
    'compute BOs': False,
    'atomic densities directory complete path': '/home/yakutovi/chargemol_09_26_2017/atomic_densities/',
    'input filename': 'valence_density',
    'number of core electrons': [
        '1  0',
        '2  0',
        '3  0',
        '4  0',
        '5  2',
        '6  2',
        '7  2',
        '8  2',
        '9  2',
        '10 2',
        '11 2',
        '12 2',
        '13 10',
        '14 10',
        '15 10',
        '16 10',
        '17 10',
        '18 10',
        '19 10',
        '20 10',
        '21 10',
        '22 10',
        '23 10',
        '24 10',
        '25 10',
        '26 10',
        '27 10',
        '28 10',
        '29 18',
        '30 18',
        '35 28',
        '53 46',
    ],
}

options = { # pylint: disable=invalid-name
    'resources': {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    },
    'max_wallclock_seconds': 1 * 30 * 60,  # 30 min
    'withmpi': False,
}


@click.command('cli')
@click.argument('codename')
@click.argument('cp2k_calculation_pk')
@click.option('--run', is_flag=True, help='Actually submit calculation')
def main(codename, cp2k_calculation_pk, run):
    """Command line interface for testing and submitting calculations.

    Usage: verdi run cli.py CODENAME CP2K_CALCULATION
    """
    code = Code.get_from_string(codename)
    # input parameters
    parameters = Dict(dict=input_dict)
    cp2k_calc = load_node(int(cp2k_calculation_pk))

    inputs = {
        'parameters': parameters,
        'charge_density_folder': cp2k_calc.outputs.remote_folder,
        'code': code,
        'metadata': {
            'options': options,
        }
    }

    if run:
        submit(DdecCalculation, **inputs)
        print('submitted calculation')
    else:
        inputs['metadata']['dry_run'] = True
        inputs['metadata']['store_provenance'] = False
        submit(DdecCalculation, **inputs)
        print('submission test successful')
        print("In order to actually submit, add '--run'")


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
