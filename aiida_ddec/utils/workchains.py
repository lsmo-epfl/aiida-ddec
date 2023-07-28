# -*- coding: utf-8 -*-
"""utils for the workchains"""
# pylint: disable=undefined-loop-variable

from __future__ import absolute_import

from collections.abc import Mapping

from aiida.engine import workfunction as wf
from aiida.orm import Dict


def dict_merge(dct, merge_dct):
    """Taken from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """

    for k, _ in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], Mapping):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


@wf
def merge_Dict(p1, p2):  # pylint: disable=invalid-name
    """
    Workfunction to merge two dictionaries p1 and p2 recursively.
    """
    p1_dict = p1.get_dict()
    p2_dict = p2.get_dict()
    dict_merge(p1_dict, p2_dict)
    return Dict(dict=p1_dict).store()


@wf
def extract_core_electrons(cp2k_remote_folder):
    """Read from the cp2k.out the number of core electrons (included in the
    pseudopotential) and print them as a Dict
    """
    with cp2k_remote_folder.creator.outputs.retrieved.open("aiida.out") as handle:
        content = handle.readlines()
    for n_line, line in enumerate(content):
        if line.startswith(" CP2K| version string:"):
            cp2k_version = str(line.split()[5])
        if "- Atoms:" in line:
            n_atoms = int(line.split()[2])
        if "Atom  Kind  Element       X           Y           Z" in line:
            break
    if cp2k_version.startswith("9."):
        res = {e.split()[3]: round(float(e.split()[7])) for e in content[n_line + 1 : n_line + n_atoms + 1]}
    else:
        res = {e.split()[3]: round(float(e.split()[7])) for e in content[n_line + 2 : n_line + n_atoms + 2]}
    res = [k + " " + str(int(k) - int(v)) for k, v in res.items()]
    return Dict(dict={"number of core electrons": res}).store()
