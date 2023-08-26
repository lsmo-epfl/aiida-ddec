#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Test/example for the DdecCp2kChargesWorkChain"""
# pylint: disable=invalid-name
from __future__ import absolute_import

import ase.build
import click
from aiida import cmdline, engine
from aiida.orm import Dict, SinglefileData, StructureData
from aiida.plugins import DataFactory, WorkflowFactory
from importlib_resources import files

import aiida_ddec

DATA_DIR = files(aiida_ddec).parent / "examples" / "data"

Cp2kDdecWorkChain = WorkflowFactory("ddec.cp2k_ddec")
StructureData = DataFactory("structure")


def run_cp2k_ddec_zn_mof74(cp2k_code, ddec_code):  # pylint: disable=redefined-outer-name
    """Run example for the DdecCp2kChargesWorkChain"""

    builder = Cp2kDdecWorkChain.get_builder()
    builder.metadata.label = "test-MOF-74"

    builder.cp2k_base.cp2k.code = cp2k_code
    atoms = ase.build.molecule("H2O")
    atoms.center(vacuum=2.0)
    builder.cp2k_base.cp2k.structure = StructureData(ase=ase.io.read(DATA_DIR / "Zn-MOF-74.cif"))
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
                    "SCF": {
                        "MAX_SCF": 3,  # limited for testing purpose
                    },
                    "XC": {
                        "XC_FUNCTIONAL": {
                            "_": "PBE",
                        },
                    },
                },
                "SUBSYS": {
                    "KIND": [
                        {
                            "_": "H",
                            "BASIS_SET": "SZV-MOLOPT-SR-GTH",
                            "POTENTIAL": "GTH-PBE",
                        },
                        {
                            "_": "C",
                            "BASIS_SET": "SZV-MOLOPT-SR-GTH",
                            "POTENTIAL": "GTH-PBE",
                        },
                        {
                            "_": "O",
                            "BASIS_SET": "SZV-MOLOPT-SR-GTH",
                            "POTENTIAL": "GTH-PBE",
                        },
                        {
                            "_": "Zn",
                            "BASIS_SET": "SZV-MOLOPT-SR-GTH",
                            "POTENTIAL": "GTH-PBE",
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
    """Run DdecCp2kChargesWorkChain on Zn-MOF-74"""
    run_cp2k_ddec_zn_mof74(ddec_code=ddec_code, cp2k_code=cp2k_code)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
