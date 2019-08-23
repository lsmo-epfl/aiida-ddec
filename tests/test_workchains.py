# -*- coding: utf-8 -*-
"""Test workchains for the DDEC plugin"""
from __future__ import absolute_import
import os
import io
import pytest  # pylint: disable=unused-import


def test_water_sp(clear_database, ddec_code, cp2k_code, basic_options_cp2k, basic_options_ddec):  # pylint: disable=unused-argument
    """Test submitting a calculation"""
    from aiida_ddec.tests import TEST_DIR
    from aiida_ddec.workflows.cp2k_sp_charges import DdecCp2kSpChargesWorkChain
    from aiida.engine import run_get_node
    from aiida.orm import Dict, StructureData
    import ase.build

    atoms = ase.build.molecule('H2O')
    atoms.center(vacuum=2.0)
    structure = StructureData(ase=atoms)
    parameters = Dict(
        dict={  # pylint: disable=invalid-name
            'FORCE_EVAL': {
                'DFT': {
                    'UKS': True,
                    'MULTIPLICITY': 2,
                    'CHARGE': -1,
                    'MGRID': {
                        'CUTOFF': 260,
                        'REL_CUTOFF': 20,
                    },
                },
            }
        })


    ddec_params = Dict(  # pylint: disable=invalid-name
        dict={
            'net charge': 0.0,
            'charge type': 'DDEC6',
            'periodicity along A, B, and C vectors': [True, True, True],
            'compute BOs': False,
            'atomic densities directory complete path': '.ci/chargemol/atomic_densities/',
            'input filename': 'valence_density',
        }
    )

    inputs = {
        'cp2k_multistage': {
            'base': {
                'cp2k': {
                    'structure': structure,
                    'code': cp2k_code,
                    'parameters': parameters,
                    'metadata': {
                        'options': basic_options_cp2k
                    },
                },
            }
        },
        'ddec_parameters': ddec_params,
        'ddec_code': ddec_code,
        'ddec_options': basic_options_ddec,
    }

    _result, node = run_get_node(DdecCp2kSpChargesWorkChain, **inputs)

    structure_w_charge = io.open(os.path.join(TEST_DIR, 'water.cif'), 'r', encoding='utf8').read()
    assert structure_w_charge == node.outputs.output_structure.get_content()
