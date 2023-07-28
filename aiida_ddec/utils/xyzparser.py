# -*- coding: utf-8 -*-
"""Convert XYZ to CIF keeping the charges"""
from __future__ import absolute_import

import re
import tempfile
from math import acos, degrees

from aiida.plugins import DataFactory
from numpy import dot
from numpy.linalg import inv, norm
from six.moves import map

CifData = DataFactory("core.cif")  # pylint: disable=invalid-name

CIF_HEADER = """data_crystal

_audit_creation_method 'AiiDA-DDEC plugin'

_cell_length_a        {a:8.5f}
_cell_length_b        {b:8.5f}
_cell_length_c        {c:8.5f}

_cell_angle_alpha     {alpha:8.5f}
_cell_angle_beta     {beta:8.5f}
_cell_angle_gamma     {gamma:8.5f}

_symmetry_space_group_name_Hall 'P 1'
_symmetry_space_group_name_H-M  'P 1'

loop_
_symmetry_equiv_pos_as_xyz
 'x,y,z'

loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
_atom_site_charge
"""


def xyzparser(lines):
    """Extract from XYZ files cell, atoms, coordinates, charges.

    :param lines: List of lines of XYZ file, e.g. result of open(filename).readlines()
    """

    # Number of atoms
    natoms = int(lines[0])

    # Cell
    cell_string = lines[1]
    cell_unformatted = re.search(r"\[.*?\]", cell_string).group(0)[1:-1].split(",")
    cell = [list(map(float, re.search(r"\{.*?\}", e).group(0)[1:-1].split())) for e in cell_unformatted]

    # Atoms
    atoms = [i.split()[0] for i in lines[2 : natoms + 2]]

    # XYZ coordinates
    xyz = [list(map(float, i.split()[1:4])) for i in lines[2 : natoms + 2]]

    # Charges
    charges = [float(i.split()[4]) for i in lines[2 : natoms + 2]]

    return cell, atoms, xyz, charges


def cell2abc(cell):
    """Compute norms of cell vectors."""
    return norm(cell[0]), norm(cell[1]), norm(cell[2])


def cell2angles(cell):
    """Return angles alpha, beta, gamma between cell vectors."""
    alpha = degrees(acos(dot(cell[1], cell[2]) / norm(cell[1]) / norm(cell[2])))
    beta = degrees(acos(dot(cell[0], cell[2]) / norm(cell[0]) / norm(cell[2])))
    gamma = degrees(acos(dot(cell[0], cell[1]) / norm(cell[0]) / norm(cell[1])))
    return alpha, beta, gamma


def xyz2cif(lines):
    """
    Convert xyz file produced by DDEC program to a cif file.

    :param lines: List of lines of XYZ file, e.g. result of open(filename).readlines()
    """
    # Extract important data from the xyz file
    cell, atoms, xyz, charges = xyzparser(lines)

    # Transform cell into a,b,c and alpha, beta, gamma
    cell_a, cell_b, cell_c = cell2abc(cell)
    alpha, beta, gamma = cell2angles(cell)

    # Transform cartensian coordinates into the fractional ones
    fract_xyz = dot(xyz, inv(cell))

    # Create and return a CifFile object
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cif") as file:
        file.write(CIF_HEADER.format(a=cell_a, b=cell_b, c=cell_c, alpha=alpha, beta=beta, gamma=gamma))
        for i, atm in enumerate(atoms):
            file.write(
                "{atm:10} {atm:5} {x:>9.5f} {y:>9.5f} {z:>9.5f} {c:>9.5f}\n".format(
                    atm=atm,
                    x=fract_xyz[i][0],
                    y=fract_xyz[i][1],
                    z=fract_xyz[i][2],
                    c=charges[i],
                )
            )
        file.flush()
        return CifData(file=file.name, scan_type="flex", parse_policy="lazy")
