# -*- coding: utf-8 -*-
"""AiiDA DDEC plugin parser"""
from __future__ import absolute_import
import re
import os
import json
import tempfile
import CifFile
from ase.io import read
from aiida.orm.nodes.data.cif import CifData
from aiida.parsers.parser import Parser
from aiida.common import NotExistent, OutputParsingError
from aiida.orm import Dict
from aiida.engine import ExitCode
from aiida.plugins import CalculationFactory

DdecCalculation = CalculationFactory('ddec')  # pylint: disable=invalid-name


def xyz2cif(fname):
    """
    Convert xyz file produced by DDEC program to a cif file.
    """
    with open(fname, 'r') as file:
        lines = file.readlines()

    # Number of atoms
    natoms = int(lines[0])

    # Extract an array of charges
    cell_string = lines[1]
    charges = [i.split()[4] for i in lines[2:natoms + 2]]

    # Extract cell
    cell_unformatted = re.search(r'\[.*?\]', cell_string).group(0)[1:-1].split(',')
    cell = [re.search(r'\{.*?\}', e).group(0)[1:-1].split() for e in cell_unformatted]

    # Create a temporary file that contains the structure
    # in cif format
    buf = tempfile.TemporaryFile(mode='w+')

    # Create an ase object, specify unitcell
    # write it into the buffer file
    ase_obj = read(fname)
    ase_obj.set_cell(cell)
    ase_obj.write(buf, format='cif')

    # Read the cif file into from the buffer a CifFile
    # object
    buf.seek(0)
    _ciffile = CifFile.ReadCif(buf)
    buf.close()

    # Manipulate the cif parameters
    img0 = _ciffile.dictionary['image0']
    img0.RemoveItem('_atom_site_label')
    img0.RemoveItem('_atom_site_occupancy')
    img0.RemoveItem('_atom_site_thermal_displace_type')
    img0.RemoveItem('_atom_site_B_iso_or_equiv')
    img0.ChangeItemOrder('_atom_site_type_symbol', 0)

    # Add chaages and placing them into the _atom_site_charge
    # loop
    img0.AddItem('_atom_site_charge', charges)
    img0.AddLoopName('_atom_site_type_symbol', '_atom_site_charge')

    # Add _atom_site_label loop that is the same as _atom_site_type_symbol one
    asts = img0.GetFullItemValue('_atom_site_type_symbol')[0]
    img0.AddItem('_atom_site_label', asts)
    img0.AddLoopName('_atom_site_type_symbol', '_atom_site_label')
    img0.ChangeItemOrder('_atom_site_label', 1)

    # Add two more items and placing them before the loops
    img0.AddItem('_symmetry_space_group_name_H-M', 'P 1')
    img0.ChangeItemOrder('_symmetry_space_group_name_h-m', -1)
    img0.AddItem('_space_group_name_Hall', 'P 1')
    img0.ChangeItemOrder('_space_group_name_Hall', -1)

    ciffile = tempfile.NamedTemporaryFile(suffix='.cif')

    with open(ciffile.name, 'w') as file:
        file.write(_ciffile.WriteOut() + '\n')

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
