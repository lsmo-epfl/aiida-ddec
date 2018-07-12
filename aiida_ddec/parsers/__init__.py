# -*- coding: utf-8 -*-
import re
import json
import tempfile
import CifFile
from ase.io import read
from aiida.orm.data.cif import CifData
from aiida.parsers.parser import Parser
from aiida.parsers.exceptions import OutputParsingError
from aiida.orm.data.parameter import ParameterData

from aiida.orm  import CalculationFactory
DdecCalculation = CalculationFactory('ddec')

def xyz2cif(fname):
    """
    Convert xyz file produced by DDEC program to a cif file.
    """
    f = open(fname)
    lines = f.readlines()
    f.close()

    # Number of atoms
    natoms = int(lines[0])

    # Extract an array of charges
    cell_string = lines[1]
    charges = [ i.split()[4] for i in lines[2:natoms+2] ]

    # Extract cell
    cell_unformatted = re.search(r"\[.*?\]",
                                cell_string).group(0)[1:-1].split(',')
    cell = [re.search(r"\{.*?\}", e).group(0)[1:-1].split()
            for e in cell_unformatted]

    # Create a temporary file that contains the structure 
    # in cif format
    buf = tempfile.TemporaryFile()

    # Create an ase object, specify unitcell
    # write it into the buffer file
    ase_obj = read(fname)
    ase_obj.set_cell(cell)
    ase_obj.write(buf, format='cif')


    # Read the cif file into from the buffer a CifFile
    # object
    buf.seek(0)
    cf = CifFile.ReadCif(buf)
    buf.close()

    # Manipulate the cif parameters
    img0 = cf.dictionary['image0']
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


    with open(ciffile.name, 'w') as f:
        f.write(cf.WriteOut())

    return CifData(file=ciffile.name,
                        scan_type='flex', parse_policy='lazy')

class DdecParser(Parser):
    """
    Parser class for parsing output of multiplication.
    """

    def __init__(self, calculation):
        """
        Initialize Parser instance
        """
        super(DdecParser, self).__init__(calculation)

        # check for valid input
        if not isinstance(calculation, DdecCalculation):
            raise OutputParsingError("Can only parse DdecCalculation")

    # pylint: disable=protected-access
    def parse_with_retrieved(self, retrieved):
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
        success = False
        node_list = ()

        # Check that the retrieved folder is there
        try:
            out_folder = retrieved[self._calc._get_linkname_retrieved()]
        except KeyError:
            self.logger.error("No retrieved folder found")
            return success, node_list

        # Check what is inside the folder
        list_of_files = out_folder.get_folder_list()

        # We need at least the output file name as defined in calcs.py
        if self._calc._OUTPUT_FILE_NAME not in list_of_files:
            self.logger.error("Output file not found")
            return success, node_list

        finished = False
        with open(out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME)) as f:
            for line in f.readlines():
                if "Finished chargemol in" in line:
                    finished = True

        if not finished:
            self.logger.error("Error parsing the output file")
            return success, node_list

        output_cif = xyz2cif(out_folder.get_abs_path(
                    'DDEC6_even_tempered_net_atomic_charges.xyz'))
        link_name = self.get_linkname_outparams()
        node_list = [('structure', output_cif)]
        success = True

        return success, node_list

