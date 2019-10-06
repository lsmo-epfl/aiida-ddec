# -*- coding: utf-8 -*-
"""Convert XYZ to CIF keeping the charges"""
from __future__ import absolute_import
import re
import tempfile
from math import degrees, acos
from numpy import dot
from numpy.linalg import inv, norm
from six.moves import map

from CifFile.CifFile_module import CifFile
from CifFile.StarFile import StarBlock


def xyzparser(fname):
    """Extract from XYZ files cell, atoms, coordinates, charges."""
    with open(fname, 'r') as file:
        lines = file.readlines()

    # Number of atoms
    natoms = int(lines[0])

    # Cell
    cell_string = lines[1]
    cell_unformatted = re.search(r'\[.*?\]', cell_string).group(0)[1:-1].split(',')
    cell = [re.search(r'\{.*?\}', e).group(0)[1:-1].split() for e in cell_unformatted]

    # Atoms
    atoms = [i.split()[0] for i in lines[2:natoms + 2]]

    # XYZ coordinates
    xyz = [list(map(float, i.split()[1:4])) for i in lines[2:natoms + 2]]

    # Charges
    charges = [float(i.split()[4]) for i in lines[2:natoms + 2]]

    return cell, atoms, xyz, charges


def cell2abc(cell):
    return norm(cell[0]), norm(cell[1]), norm(cell[2])


def cell2angles(cell):
    alpha = degrees(acos(dot(cell[1], cell[2]) / norm(cell[1]) / norm(cell[2])))
    beta = degrees(acos(dot(cell[0], cell[2]) / norm(cell[0]) / norm(cell[2])))
    gamma = degrees(acos(dot(cell[0], cell[1]) / norm(cell[0]) / norm(cell[1])))
    return alpha, beta, gamma


LOOPS_TO_EXTRACT = [
    '_atom_site_label',
    '_atom_site_type_symbol',
    '_atom_site_fract_x',
    '_atom_site_fract_y',
    '_atom_site_fract_z',
    '_atom_site_charge',
]


def xyz2cif(fname):
    """
    Convert xyz file produced by DDEC program to a cif file.
    """
    # Extract important data from the xyz file
    cell, atoms, xyz, charges = xyzparser(fname)

    # Transform cell into a,b,c and alpha, beta, gamma
    cell_a, cell_b, cell_c = cell2abc(cell)
    alpha, beta, gamma = cell2angles(cell)

    # Transform cartensian coordinates into the fractional ones
    fract_xyz = dot(xyz, inv(cell))

    # Prepare an output cif object
    output_cif = CifFile()
    output_cif['crystal'] = StarBlock()

    # Extract only the relevant data
    output_cif['crystal'].AddItem('_cell_length_a', cell_a)
    output_cif['crystal'].AddItem('_cell_length_b', cell_b)
    output_cif['crystal'].AddItem('_cell_length_c', cell_c)
    output_cif['crystal'].AddItem('_cell_angle_alpha', alpha)
    output_cif['crystal'].AddItem('_cell_angle_beta', beta)
    output_cif['crystal'].AddItem('_cell_angle_gamma', gamma)
    output_cif['crystal'].AddItem('_symmetry_space_group_name_Hall', 'P 1')
    output_cif['crystal'].AddItem('_symmetry_space_group_name_H-M', 'P 1')

    # Extract loops
    output_cif['crystal'].AddItem('_atom_site_label', atoms)
    output_cif['crystal'].AddItem('_atom_site_type_symbol', atoms)
    output_cif['crystal'].AddItem('_atom_site_fract_x', fract_xyz[:, 0])
    output_cif['crystal'].AddItem('_atom_site_fract_y', fract_xyz[:, 1])
    output_cif['crystal'].AddItem('_atom_site_fract_z', fract_xyz[:, 2])
    output_cif['crystal'].AddItem('_atom_site_charge', charges)

    output_cif['crystal'].CreateLoop(LOOPS_TO_EXTRACT)

    # Remove comments and empty lines
    output = [l.strip() for l in output_cif.WriteOut(comment=' ').splitlines()]
    output = [l for l in output if l != '' and not l.startswith('#')]

    # Create and return a CifFile object
    ciffile = tempfile.NamedTemporaryFile(suffix='.cif')
    with open(ciffile.name, 'w') as file:
        file.write(output_cif.WriteOut() + '\n')

    return ciffile.name
