# -*- coding: utf-8 -*-
"""AiiDA DDEC plugin parser"""
from __future__ import print_function
from __future__ import absolute_import

import re
import os
import json
import tempfile
import math
from numpy.linalg import inv
from aiida.orm.nodes.data.cif import CifData
from aiida.parsers.parser import Parser
from aiida.common import NotExistent, OutputParsingError
from aiida.orm import Dict
from aiida.engine import ExitCode
from aiida.plugins import CalculationFactory
from six.moves import range

DdecCalculation = CalculationFactory('ddec')  # pylint: disable=invalid-name


def xyz2cif(fname):  # pylint: disable=too-many-statements
    """Convert xyz file produced by DDEC program to a cif file."""
    # parse .xyz file
    file = open(fname, 'r')
    natom = int(file.readline().split()[0])
    data = file.readline().split()
    cell = []
    cell.append([float(data[10]), float(data[11]), float(data[12])])
    cell.append([float(data[15]), float(data[16]), float(data[17])])
    cell.append([float(data[20]), float(data[21]), float(data[22])])
    atom_element = []
    atom_xyz = []
    atom_charge = []
    for i in range(natom):
        data = file.readline().split()
        atom_element.append(data[0])
        atom_xyz.append([float(data[1]), float(data[2]), float(data[3])])
        if len(data) == 5:
            atom_charge.append(float(data[4]))
    file.close()

    # convert to lengths, angles and fractional coordinates
    length = []
    angle = []
    length.append(math.sqrt(cell[0][0] * cell[0][0] + cell[0][1] * cell[0][1] + cell[0][2] * cell[0][2]))
    length.append(math.sqrt(cell[1][0] * cell[1][0] + cell[1][1] * cell[1][1] + cell[1][2] * cell[1][2]))
    length.append(math.sqrt(cell[2][0] * cell[2][0] + cell[2][1] * cell[2][1] + cell[2][2] * cell[2][2]))
    angle.append(
        math.degrees(
            math.acos((cell[1][0] * cell[2][0] + cell[1][1] * cell[2][1] + cell[1][2] * cell[2][2]) / length[1] /
                      length[2])))  #alpha=B^C
    angle.append(
        math.degrees(
            math.acos((cell[0][0] * cell[2][0] + cell[0][1] * cell[2][1] + cell[0][2] * cell[2][2]) / length[0] /
                      length[2])))  #beta=A^C
    angle.append(
        math.degrees(
            math.acos((cell[0][0] * cell[1][0] + cell[0][1] * cell[1][1] + cell[0][2] * cell[1][2]) / length[0] /
                      length[1])))  #gamma=A^B
    atom_fract = [[0.0] * 3 for i in range(natom)]
    invcell = inv(cell)
    for i in range(natom):
        for j in range(3):
            atom_fract[i][j] = atom_xyz[i][0] * invcell[0][j] + \
                               atom_xyz[i][1] * invcell[1][j] + \
                               atom_xyz[i][2] * invcell[2][j]

    # print .cif file
    ciffile = tempfile.NamedTemporaryFile(suffix='.cif')
    ofile = open(ciffile.name, 'w')
    print('data_crystal', file=ofile)
    print(' ', file=ofile)
    print('_audit_creation_method AiiDA-ddec_plugin ', file=ofile)
    print(' ', file=ofile)
    print('_cell_length_a    %.5f' % length[0], file=ofile)
    print('_cell_length_b    %.5f' % length[1], file=ofile)
    print('_cell_length_c    %.5f' % length[2], file=ofile)
    print('_cell_angle_alpha %.5f' % angle[0], file=ofile)
    print('_cell_angle_beta  %.5f' % angle[1], file=ofile)
    print('_cell_angle_gamma %.5f' % angle[2], file=ofile)
    print(' ', file=ofile)
    print("_symmetry_space_group_name_Hall 'P 1'", file=ofile)
    print("_symmetry_space_group_name_H-M  'P 1'", file=ofile)
    print(' ', file=ofile)
    print('loop_', file=ofile)
    print('_symmetry_equiv_pos_as_xyz', file=ofile)
    print(" 'x,y,z' ", file=ofile)
    print(' ', file=ofile)
    print('loop_', file=ofile)
    print('_atom_site_label', file=ofile)
    print('_atom_site_type_symbol', file=ofile)
    print('_atom_site_fract_x', file=ofile)
    print('_atom_site_fract_y', file=ofile)
    print('_atom_site_fract_z', file=ofile)
    print('_atom_site_charge', file=ofile)
    for i in range(natom):
        print('{0:10} {1:5} {2:>9.5f} {3:>9.5f} {4:>9.5f} {5:>9.5f}'.format(atom_element[i], atom_element[i],
                                                                            atom_fract[i][0], atom_fract[i][1],
                                                                            atom_fract[i][2], atom_charge[i]),
              file=ofile)
    ofile.close()

    return CifData(file=ciffile.name, scan_type='flex', parse_policy='lazy')


class DdecParser(Parser):
    """
    Parser class for parsing output of multiplication.
    """

    # pylint: disable=protected-access
    def parse(self, **kwargs):
        """
        Parse output data folder, store results in database.

        :param retrieved: a dictionary of retrieved nodes, where
          the key is the link name
        :returns: a tuple with two values ``(bool, node_list)``,
          where:

          * ``bool``: variable to tell if the parsing succeeded
          * ``node_list``: list of new nodes to be stored in the db
            (as a list of tuples ``(link_name, node)``)
        """

        # Check that the retrieved folder is there
        try:
            out_folder = self.retrieved
        except NotExistent:
            self.logger.error('No retrieved folder found')
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # Check what is inside the folder
        list_of_files = out_folder._repository.list_object_names()  # pylint: disable=protected-access

        output_file = self.node.process_class._DEFAULT_OUTPUT_FILE

        # We need at least the output file name as defined in calcs.py
        if output_file not in list_of_files:
            raise self.exit_codes.ERROR_NO_OUTPUT_FILE

        finished = False
        with open(os.path.join(out_folder._repository._get_base_folder().abspath, output_file)) as file:  # pylint: disable=protected-access
            for line in file.readlines():
                if 'Finished chargemol in' in line:
                    finished = True

        if not finished:
            raise OutputParsingError('Calculation did not finish correctly')

        output_cif = xyz2cif(
            os.path.join(out_folder._repository._get_base_folder().abspath,
                         'DDEC6_even_tempered_net_atomic_charges.xyz'))

        self.out('structure_ddec', output_cif)

        return ExitCode(0)
