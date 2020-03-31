# -*- coding: utf-8 -*-
"""AiiDA-DDEC input plugin"""
from __future__ import absolute_import
import os
from collections import OrderedDict
import six
from voluptuous import Schema, Optional
from aiida.engine import CalcJob
from aiida.orm import Dict
from aiida.orm import RemoteData
from aiida.common import CalcInfo, CodeInfo
from aiida.orm.nodes.data.cif import CifData


def input_render(input_dict):
    """
    Converting a dictionary into an input file
    """
    output = ''
    for key, value in input_dict.items():
        if isinstance(value, OrderedDict):
            output += '<' + key + '>' + '\n'
            for k, v in value.items():  # pylint: disable=invalid-name
                output += str(k) + ' ' + str(v) + '\n'
            output += '</' + key + '>' + '\n'
            output += '\n'
        elif isinstance(value, list):
            output += '<' + key + '>' + '\n'
            for e in value:  # pylint: disable=invalid-name
                if e == True:  # pylint: disable=singleton-comparison
                    output += '.true.'
                elif e == False:  # pylint: disable=singleton-comparison
                    output += '.false.'
                else:
                    output += str(e)
                output += '\n'
            output += '</' + key + '>' + '\n'
            output += '\n'
        elif isinstance(value, bool):
            output += '<' + key + '>' + '\n'
            if value == True:  # pylint: disable=singleton-comparison
                output += '.true.'
            elif value == False:  # pylint: disable=singleton-comparison
                output += '.false.'
            output += '\n'
            output += '</' + key + '>' + '\n'
            output += '\n'
        else:
            output += '<' + key + '>' + '\n'
            output += str(value) + '\n'
            output += '</' + key + '>' + '\n'
            output += '\n'
    return output


PARAMETERS_SCHEMA = Schema(
    {
        'net charge': float,
        'charge type': str,
        'periodicity along A, B, and C vectors': [bool, bool, bool],
        'compute BOs': bool,
        Optional('atomic densities directory complete path'): str,
        'input filename': str,
    },
    required=True,
)


def validate_parameters(parameters):
    PARAMETERS_SCHEMA(parameters.get_dict())


class DdecCalculation(CalcJob):
    """
    AiiDA plugin for the ddec code that performs density derived
    electrostatic and chemical atomic population analysis.
    """

    _DEFAULT_INPUT_FILE = 'job_control.txt'
    _DEFAULT_OUTPUT_FILE = 'valence_cube_DDEC_analysis.output'
    _DEFAULT_ADDITIONAL_RETRIEVE_LIST = '*.xyz'  # pylint: disable=invalid-name
    _CODE_PATH_EXTRA = 'DDEC_ATOMIC_DENSITIES_DIRECTORY'

    @classmethod
    def define(cls, spec):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(DdecCalculation, cls).define(spec)
        spec.input(
            'parameters',
            valid_type=Dict,
            validator=validate_parameters,
            help='Input parameters such as net charge, protocol, atomic densities path, ...',
        )
        spec.input(
            'charge_density_folder',
            valid_type=RemoteData,
            required=False,
            help='Use a remote folder (for restarts and similar)',
        )
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default='ddec')
        spec.input('metadata.options.withmpi', valid_type=bool, default=False)
        spec.input(
            'metadata.options.resources',
            valid_type=dict,
            default={
                'num_machines': 1,
                'num_mpiprocs_per_machine': 1,
                'tot_num_mpiprocs': 1,
            }
        )

        #  exit codes
        spec.exit_code(
            100,
            'ERROR_NO_RETRIEVED_FOLDER',
            message='The retrieved folder data node could not be accessed.',
        )
        spec.exit_code(
            101,
            'ERROR_NO_OUTPUT_FILE',
            message='The retrieved folder does not contain an output file.',
        )
        spec.output('structure_ddec', valid_type=CifData, required=True, help='structure with DDEC charges')

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed
         to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        # Determine atomic densities directory
        pm_dict = self.inputs.parameters.get_dict()
        path_key = 'atomic densities directory complete path'
        if path_key not in pm_dict:
            pm_dict[path_key] = self.inputs.code.extras.get(self._CODE_PATH_EXTRA)

        if not pm_dict[path_key]:
            raise ValueError("No value for '{}' - either provide in input parameters or set extra '{}' on the code." \
                             .format(path_key, self._CODE_PATH_EXTRA))

        # The directory must end with a slash or chargemol crashes
        if not pm_dict[path_key].endswith('/'):
            pm_dict[path_key] += '/'

        # Write input to file
        input_filename = folder.get_abs_path(self._DEFAULT_INPUT_FILE)
        with open(input_filename, 'w') as infile:
            infile.write(input_render(pm_dict))

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.remote_symlink_list = []
        calcinfo.retrieve_list = [
            self._DEFAULT_OUTPUT_FILE,
            [self._DEFAULT_ADDITIONAL_RETRIEVE_LIST, '.', 0],
        ]

        # Charge-density remotefolder (now working only for CP2K)
        if 'charge_density_folder' in self.inputs:
            charge_density_folder = self.inputs.charge_density_folder
            comp_uuid = charge_density_folder.computer.uuid
            remote_path = os.path.join(
                charge_density_folder.get_remote_path(),
                'aiida-ELECTRON_DENSITY-1_0.cube',
            )
            symlink = (comp_uuid, remote_path, 'valence_density.cube')
            calcinfo.remote_symlink_list.append(symlink)

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = []
        codeinfo.code_uuid = self.inputs.code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
