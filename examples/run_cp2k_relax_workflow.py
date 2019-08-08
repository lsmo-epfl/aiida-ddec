#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Test/Example for the DdecCp2kChargesWorkChain"""
from __future__ import print_function
from __future__ import absolute_import
import click

from ase.io import read
from aiida.engine import submit
from aiida.orm import Code, Dict
from aiida.plugins import DataFactory
from aiida_ddec.workflows.cp2k_relax_charges import DdecCp2kRelaxChargesWorkChain

StructureData = DataFactory('structure')  # pylint: disable=invalid-name
atoms = read('Cu-MOF-74.cif')  # pylint: disable=invalid-name

structure = StructureData(ase=atoms)  # pylint: disable=invalid-name
structure.store()

cp2k_options = {  # pylint: disable=invalid-name
    'resources': {'num_machines': 1},
    'max_wallclock_seconds': 1 * 60 * 60,
}

ddec_options = {  # pylint: disable=invalid-name
    'resources': {'num_machines': 1},
    'max_wallclock_seconds': 1 * 60 * 60,
    'withmpi': False,
}

parameters = Dict(dict={  # pylint: disable=invalid-name
    'FORCE_EVAL': {
        'DFT': {
            'MGRID': {
                'CUTOFF': 280,
                'REL_CUTOFF': 30,
            }
        }
    }
})


@click.command('cli')
@click.argument('cp2k_code_string')
@click.argument('ddec_code_string')
@click.option('--run', is_flag=True, help='Actually submit calculation')
def main(cp2k_code_string, ddec_code_string, run):
    """CLI function """
    cp2k_code = Code.get_from_string(cp2k_code_string)
    ddec_code = Code.get_from_string(ddec_code_string)
    # ToDo: this nested input is not really nice. Maybe think wether we really want
    # this as some inputs are probably always change, but bringing them to a higher
    # dictionary level gives two input channels, which we should also avoid ...
    # Also, it is a bit inconsistent with the fact that we don't expose the DDEC inputs

    inputs = {
        'cp2k_multistage': {
            'base': {
                'cp2k': {
                    'structure': structure,
                    'code': cp2k_code,
                    'parameters': parameters,
                    'metadata': {
                        'options': cp2k_options
                    },
                }
            }
        },
        'ddec_code': ddec_code,
        'ddec_options': ddec_options,
    }

    if run:
        submit(DdecCp2kRelaxChargesWorkChain, **inputs)
        print('submitted cp2k ddec test run')
    else:
        print('Generating test input ...')
        inputs['cp2k_multistage']['base']['cp2k']['metadata']['dry_run'] = True
        inputs['cp2k_multistage']['base']['cp2k']['metadata']['store_provenance'] = False
        submit(DdecCp2kRelaxChargesWorkChain, **inputs)
        print('Submission test successful')
        print("In order to actually submit, add '--run'")


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
