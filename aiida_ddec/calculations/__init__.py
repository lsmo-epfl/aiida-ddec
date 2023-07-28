# -*- coding: utf-8 -*-
"""AiiDA-DDEC input plugin"""
from __future__ import absolute_import

import os
from collections import OrderedDict

import six
from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import CifData, Dict, RemoteData
from voluptuous import Optional, Schema


def input_render(input_dict):
    """
    Converting a dictionary into an input file
    """
    output = ""
    for key, value in input_dict.items():
        if isinstance(value, OrderedDict):
            output += "<" + key + ">" + "\n"
            for k, v in value.items():  # pylint: disable=invalid-name
                output += str(k) + " " + str(v) + "\n"
            output += "</" + key + ">" + "\n"
            output += "\n"
        elif isinstance(value, list):
            output += "<" + key + ">" + "\n"
            for e in value:  # pylint: disable=invalid-name
                if e == True:  # pylint: disable=singleton-comparison
                    output += ".true."
                elif e == False:  # pylint: disable=singleton-comparison
                    output += ".false."
                else:
                    output += str(e)
                output += "\n"
            output += "</" + key + ">" + "\n"
            output += "\n"
        elif isinstance(value, bool):
            output += "<" + key + ">" + "\n"
            output += ".true." if value else ".false."
            output += "\n"
            output += "</" + key + ">" + "\n"
            output += "\n"
        else:
            output += "<" + key + ">" + "\n"
            output += str(value) + "\n"
            output += "</" + key + ">" + "\n"
            output += "\n"
    return output


DENSITY_DIR_KEY = "atomic densities directory complete path"
DENSITY_DIR_EXTRA = "DDEC_ATOMIC_DENSITIES_DIRECTORY"
DENSITY_DIR_SYMLINK = "atomic_densities/"
PARAMETERS_SCHEMA = Schema(
    {
        "net charge": float,
        "charge type": str,
        "periodicity along A, B, and C vectors": [bool, bool, bool],
        "compute BOs": bool,
        Optional(DENSITY_DIR_KEY): str,
        "input filename": str,
        Optional("number of core electrons"): list,
    },
    required=True,
)


def validate_parameters(parameters, port):  # pylint: disable=unused-argument
    """Validate input parameters according to voluptuous schema."""
    PARAMETERS_SCHEMA(parameters.get_dict())


class DdecCalculation(CalcJob):
    """
    AiiDA plugin for the ddec code that performs density derived
    electrostatic and chemical atomic population analysis.
    """

    _DEFAULT_INPUT_FILE = "job_control.txt"
    _DEFAULT_OUTPUT_FILE = "valence_cube_DDEC_analysis.output"
    _DEFAULT_ADDITIONAL_RETRIEVE_LIST = "*.xyz"  # pylint: disable=invalid-name

    @classmethod
    def define(cls, spec):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(DdecCalculation, cls).define(spec)
        spec.input(
            "parameters",
            valid_type=Dict,
            validator=validate_parameters,
            help="Input parameters such as net charge, protocol, atomic densities path, ...",
        )
        spec.input(
            "charge_density_folder",
            valid_type=RemoteData,
            required=False,
            help="Use a remote folder (for restarts and similar)",
        )
        spec.inputs["metadata"]["options"]["parser_name"].default = "ddec"
        spec.inputs["metadata"]["options"]["resources"].default = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }
        spec.inputs["metadata"]["options"]["withmpi"].default = False

        #  exit codes
        spec.exit_code(
            100,
            "ERROR_NO_RETRIEVED_FOLDER",
            message="The retrieved folder data node could not be accessed.",
        )
        spec.exit_code(
            101,
            "ERROR_NO_OUTPUT_FILE",
            message="The retrieved folder does not contain an output file.",
        )
        spec.output(
            "structure_ddec",
            valid_type=CifData,
            required=True,
            help="structure with DDEC charges",
        )

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed
         to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        # Determine atomic densities directory
        pm_dict = self.inputs.parameters.get_dict()

        if DENSITY_DIR_KEY not in pm_dict:
            pm_dict[DENSITY_DIR_KEY] = self.inputs.code.extras.get(DENSITY_DIR_EXTRA)

        if not pm_dict[DENSITY_DIR_KEY]:
            raise ValueError(
                f"Please provide '{DENSITY_DIR_KEY}' in the input parameters or set the "
                f"{DENSITY_DIR_EXTRA} extra on the ddec code."
            )

        # The directory must end with a slash or chargemol crashes
        if not pm_dict[DENSITY_DIR_KEY].endswith("/"):
            pm_dict[DENSITY_DIR_KEY] += "/"

        if not os.path.isabs(pm_dict[DENSITY_DIR_KEY]):
            raise ValueError(f"Path to atomic densities directory '{pm_dict[DENSITY_DIR_KEY]}' is not absolute.")

        # Create symlink to atomic densities directory
        density_dir_symlink = (
            self.inputs.code.computer.uuid,
            pm_dict[DENSITY_DIR_KEY],
            DENSITY_DIR_SYMLINK,
        )
        pm_dict[DENSITY_DIR_KEY] = DENSITY_DIR_SYMLINK

        # Write input to file
        input_filename = folder.get_abs_path(self._DEFAULT_INPUT_FILE)
        with open(input_filename, "w", encoding="utf-8") as infile:
            infile.write(input_render(pm_dict))

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.remote_symlink_list = [density_dir_symlink]
        calcinfo.retrieve_list = [
            self._DEFAULT_OUTPUT_FILE,
            [self._DEFAULT_ADDITIONAL_RETRIEVE_LIST, ".", 0],
        ]

        # Charge-density remote folder (now working only for CP2K)
        if "charge_density_folder" in self.inputs:
            charge_density_folder = self.inputs.charge_density_folder
            comp_uuid = charge_density_folder.computer.uuid
            remote_path = os.path.join(
                charge_density_folder.get_remote_path(),
                "aiida-ELECTRON_DENSITY-1_0.cube",
            )
            copy_info = (comp_uuid, remote_path, "valence_density.cube")
            if self.inputs.code.computer.uuid == comp_uuid:  # if running on the same computer - make a symlink
                calcinfo.remote_symlink_list.append(copy_info)
            else:  # if not - copy the folder
                self.report(
                    f"Warning: Transferring cube file {charge_density_folder.get_remote_path()} from "
                    + f"computer {charge_density_folder.computer.label} to computer {self.inputs.code.computer.label}. "
                    + "This may put strain on your network."
                )
                calcinfo.remote_copy_list.append(copy_info)

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = []
        codeinfo.code_uuid = self.inputs.code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
