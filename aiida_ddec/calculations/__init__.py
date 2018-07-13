# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c), The AiiDA team. All rights reserved.                         #
# This file is part of the AiiDA code.                                        #
#                                                                             #
# The code is hosted on GitHub at https://github.com/yakutovicha/aiida-raspa  #
# For further information on the license, see the LICENSE.txt file            #
# For further information please visit http://www.aiida.net                   #
###############################################################################
import os
from collections import OrderedDict

from aiida.orm.calculation.job import JobCalculation
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.remote import RemoteData
from aiida.common.utils import classproperty
from aiida.common.exceptions import (InputValidationError, ValidationError)
from aiida.common.datastructures import (CalcInfo, CodeInfo)
from aiida.orm import DataFactory

def input_render(input_dict):
    """
    Converting a dictionary into an input file
    """
    output = ""
    for key,value in input_dict.iteritems():
        if isinstance(value, OrderedDict):
            output += '<' + key + '>' + '\n'
            for k,v in value.iteritems():
                output += str(k) + ' ' + str(v) + '\n'
            output += '</' + key + '>' + '\n'
            output += '\n'
        elif isinstance(value, list):
            output += '<' + key + '>' + '\n'
            for e in value:
                if e == True:
                    output += '.true.'
                elif e == False:
                    output += '.false.'
                else:
                    output += str(e)
                output += '\n'
            output += '</' + key + '>' + '\n'
            output += '\n'
        elif isinstance(value, bool):
            output += '<' + key + '>' + '\n'
            if value == True:
                output += '.true.'
            elif value == False:
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

class DdecCalculation(JobCalculation):
    """
    AiiDA plugin for the ddec code that performs density derived
    electrostatic and chemical atomic population analysis.
    """

    def _init_internal_params(self):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(DdecCalculation, self)._init_internal_params()

        self._INPUT_FILE_NAME = 'job_control.txt'
        self._OUTPUT_FILE_NAME = 'valence_cube_DDEC_analysis.output'
        self._ADDITIONAL_RETRIEVE_LIST = '*.xyz'
        self._ELECTRONIC_CALC_FOLDER_NAME = 'electronic_calc/'
        # template.product entry point defined in setup.json
        self._default_parser = 'ddec'

    @classproperty
    def _use_methods(cls):
        """
        Add use_* methods for calculations.
        
        Code below enables the usage
        my_calculation.use_parameters(my_parameters)
        """
        use_dict = JobCalculation._use_methods
        use_dict.update({
            "parameters": {
                'valid_types': ParameterData,
                'additional_parameter': None,
                'linkname': 'parameters',
                'docstring':
                ("Use a node that specifies the input parameters ")
            },
            "electronic_calc_folder": {
               'valid_types': RemoteData,
               'additional_parameter': None,
               'linkname': 'electronic_calc_folder',
               'docstring': "Use a remote folder "
                            "(for restarts and similar)",
               },
        })
        return use_dict

    def _prepare_for_submission(self, tempfolder, inputdict):
        """
        Create input files.

            :param tempfolder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
            :param inputdict: dictionary of the input nodes as they would
                be returned by get_inputs_dict
        """
        # Check inputdict
        try:
            parameters = inputdict.pop(self.get_linkname('parameters'))
        except KeyError:
            raise InputValidationError("No parameters specified for this "
                                       "calculation")
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters not of type "
                                       "ParameterData")
        try:
            code = inputdict.pop(self.get_linkname('code'))
        except KeyError:
            raise InputValidationError("No code specified for this "
                                       "calculation")

        try:
            electronic_calc_folder = inputdict.pop('electronic_calc_folder', None)
        except:
            pass

        if inputdict:
            raise ValidationError("Unknown inputs besides ParameterData")

        # In this example, the input file is simply a json dict.
        # Adapt for your particular code!
        input_dict = parameters.get_dict()

        # Write input to file
        input_filename = tempfolder.get_abs_path(self._INPUT_FILE_NAME)
        with open(input_filename, 'w') as infile:
            infile.write(input_render(input_dict))

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.remote_symlink_list = []
        calcinfo.retrieve_list = [
            self._OUTPUT_FILE_NAME,
            [self._ADDITIONAL_RETRIEVE_LIST, '.',0]
        ]

        # Electronic calc folder
        if electronic_calc_folder is not None:
            if not isinstance(electronic_calc_folder, RemoteData):
                msg = "electronic_calc_folder type not RemoteData"
                raise InputValidationError(msg)

            comp_uuid = electronic_calc_folder.get_computer().uuid
            remote_path = electronic_calc_folder.get_remote_path()+'/'+'aiida-ELECTRON_DENSITY-1_0.cube'
            symlink = (comp_uuid, remote_path, 'valence_density.cube')
            calcinfo.remote_symlink_list.append(symlink)

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = []
        codeinfo.code_uuid = code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
