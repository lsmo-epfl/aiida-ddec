"""AiiDA-DDEC input plugin"""
import os
from collections import OrderedDict
import six
from aiida.engine import CalcJob
from aiida.orm import Bool, Dict
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


class DdecCalculation(CalcJob):
    """
    AiiDA plugin for the ddec code that performs density derived
    electrostatic and chemical atomic population analysis.
    """

    _DEFAULT_INPUT_FILE = 'job_control.txt'
    _DEFAULT_ADDITIONAL_RETRIEVE_LIST = 'DDEC6_even_tempered_net_atomic_charges.xyz'  # pylint: disable=invalid-name

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
            help='Input parameters such as net charge, protocol, atomic densities path, ...',
        )
        spec.input(
            'charge_density_folder',
            valid_type=RemoteData,
            required=False,
            help='Use a remote folder (for restarts and similar)'
        )
        spec.input(
            'spin', valid_type=Bool, default=Bool(False), help='Set True if want to have atomic spin moments reported!'
        )
        spec.inputs['metadata']['options']['parser_name'].default = 'ddec'
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
        }
        spec.inputs['metadata']['options']['withmpi'].default = False

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
        spec.output(
            'structure_ddec_spin', valid_type=CifData, required=False, help='structure with DDEC atomic spin moments'
        )

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed
         to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        # Write input to file
        input_filename = folder.get_abs_path(self._DEFAULT_INPUT_FILE)
        with open(input_filename, 'w') as infile:
            infile.write(input_render(self.inputs.parameters.get_dict()))

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.remote_symlink_list = []

        # Charge-density remotefolder (now working only for CP2K)
        if 'charge_density_folder' in self.inputs:
            charge_density_folder = self.inputs.charge_density_folder
            comp_uuid = charge_density_folder.computer.uuid
            if 'aiida-ELECTRON_DENSITY-1_0.cube' in self.inputs.charge_density_folder.listdir():
                OUTPUT_FILE = 'valence_cube_DDEC_analysis.output'  # pylint: disable=invalid-name
                remote_path = os.path.join(
                    charge_density_folder.get_remote_path(),
                    'aiida-ELECTRON_DENSITY-1_0.cube',
                )
                symlink = (comp_uuid, remote_path, 'valence_density.cube')
                calcinfo.remote_symlink_list.append(symlink)
            elif 'AECCAR0' in self.inputs.charge_density_folder.listdir():
                OUTPUT_FILE = 'VASP_DDEC_analysis.output'  # pylint: disable=invalid-name
                vasp_specific_files = ['AECCAR0', 'AECCAR2', 'CHGCAR', 'POTCAR']
                copy_list = [(comp_uuid, os.path.join(charge_density_folder.get_remote_path(), name), '.')
                             for name in charge_density_folder.listdir()
                             if name in vasp_specific_files]
                calcinfo.remote_copy_list = copy_list
            else:
                raise AttributeError('We currently only support CP2K and VASP generated potential files!')

        calcinfo.retrieve_list = [
            OUTPUT_FILE,
            [self._DEFAULT_ADDITIONAL_RETRIEVE_LIST, '.', 0],
        ]

        if self.inputs.spin:
            calcinfo.retrieve_list.append('DDEC6_even_tempered_atomic_spin_moments.xyz')

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = []
        codeinfo.code_uuid = self.inputs.code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
