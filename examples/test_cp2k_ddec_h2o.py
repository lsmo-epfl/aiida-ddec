#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Test/example for the DdecCp2kChargesWorkChain"""

from __future__ import absolute_import, print_function

import ase.build
import click
from aiida import cmdline, engine
from aiida.orm import Dict, SinglefileData, StructureData
from aiida.plugins import DataFactory, WorkflowFactory
from importlib_resources import files

import aiida_ddec

DATA_DIR = files(aiida_ddec).parent / "examples" / "data"

Cp2kDdecWorkChain = WorkflowFactory("ddec.cp2k_ddec")  # pylint: disable=invalid-name
StructureData = DataFactory("structure")  # pylint: disable=invalid-name


def run_cp2k_ddec_h2o(cp2k_code, ddec_code):  # pylint: disable=redefined-outer-name
    """Run example for the DdecCp2kChargesWorkChain"""
    print("Testing CP2K ENERGY calculation + DDEC on H2O...")

    builder = Cp2kDdecWorkChain.get_builder()
    builder.metadata.label = "test-h2o"

    builder.cp2k_base.cp2k.code = cp2k_code
    atoms = ase.build.molecule("H2O")
    atoms.center(vacuum=2.0)
    builder.cp2k_base.cp2k.structure = StructureData(ase=atoms)
    builder.cp2k_base.cp2k.metadata.options.resources = {
        "num_machines": 1,
        "num_mpiprocs_per_machine": 1,
    }
    builder.cp2k_base.cp2k.metadata.options.withmpi = False
    builder.cp2k_base.cp2k.metadata.options.max_wallclock_seconds = 10 * 60
    builder.cp2k_base.cp2k.parameters = Dict(
        dict={
            "FORCE_EVAL": {
                "METHOD": "Quickstep",
                "DFT": {
                    "BASIS_SET_FILE_NAME": "BASIS_MOLOPT",
                    "POTENTIAL_FILE_NAME": "GTH_POTENTIALS",
                    "QS": {
                        "EPS_DEFAULT": 1.0e-12,
                        "WF_INTERPOLATION": "ps",
                        "EXTRAPOLATION_ORDER": 3,
                    },
                    "MGRID": {
                        "NGRIDS": 4,
                        "CUTOFF": 280,
                        "REL_CUTOFF": 30,
                    },
                    "XC": {
                        "XC_FUNCTIONAL": {
                            "_": "LDA",
                        },
                    },
                    "POISSON": {
                        "PERIODIC": "none",
                        "PSOLVER": "MT",
                    },
                },
                "SUBSYS": {
                    "KIND": [
                        {
                            "_": "O",
                            "BASIS_SET": "DZVP-MOLOPT-SR-GTH",
                            "POTENTIAL": "GTH-LDA-q6",
                        },
                        {
                            "_": "H",
                            "BASIS_SET": "DZVP-MOLOPT-SR-GTH",
                            "POTENTIAL": "GTH-LDA-q1",
                        },
                    ],
                },
            }
        }
    )
    # The following is not needed, if the files are available in the data directory of your CP2K executable
    cp2k_dir = DATA_DIR / "cp2k"
    builder.cp2k_base.cp2k.file = {
        "basis": SinglefileData(file=str(cp2k_dir / "BASIS_MOLOPT")),
        "pseudo": SinglefileData(file=str(cp2k_dir / "GTH_POTENTIALS")),
    }

    builder.ddec.code = ddec_code
    builder.ddec.parameters = Dict(
        dict={
            "net charge": 0.0,
            "charge type": "DDEC6",
            "periodicity along A, B, and C vectors": [True, True, True],
            "compute BOs": False,
            "input filename": "valence_density",
        }
    )
    builder.ddec.metadata.options.max_wallclock_seconds = 10 * 60

    results = engine.run(builder)

    assert "structure_ddec" in results, results


@click.command()
@cmdline.utils.decorators.with_dbenv()
@click.option("--ddec-code", type=cmdline.params.types.CodeParamType())
@click.option("--cp2k-code", type=cmdline.params.types.CodeParamType())
def cli(ddec_code, cp2k_code):
    """Run example for the DdecCp2kChargesWorkChain"""
    run_cp2k_ddec_h2o(ddec_code=ddec_code, cp2k_code=cp2k_code)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
