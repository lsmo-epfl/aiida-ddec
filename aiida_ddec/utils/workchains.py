"""utils for the workchains"""
import os
from aiida.engine import workfunction
from aiida.orm import Dict


def dict_merge(dct, merge_dct):
    """ Taken from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    import collections  #pylint: disable=import-outside-toplevel

    for k, _ in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


@workfunction
def merge_Dict(p1, p2):  # pylint: disable=invalid-name
    """
    Workfunction to merge two dictionaries p1 and p2 recursively.
    """
    p1_dict = p1.get_dict()
    p2_dict = p2.get_dict()
    dict_merge(p1_dict, p2_dict)
    return Dict(dict=p1_dict).store()


@workfunction
def extract_core_electrons(cp2k_remote_folder):
    """Read from the cp2k.out the number of core electrons (included in the
    pseudopotential) and print them as a Dict
    """
    cp2k_out_dir = cp2k_remote_folder.creator.outputs.retrieved._repository._get_base_folder().abspath  # pylint: disable=protected-access
    cp2k_out_file = os.path.join(cp2k_out_dir, 'aiida.out')
    with open(cp2k_out_file) as f:  # pylint: disable=invalid-name
        content = f.readlines()
    for n_line, line in enumerate(content):
        if '- Atoms:' in line:
            n_atoms = int(line.split()[2])
        if 'Atom  Kind  Element       X           Y           Z' in line:
            break
    res = {
        e.split()[3]: round(float(e.split()[7])) for e in content[n_line + 2:n_line + n_atoms + 2]  # pylint: disable=undefined-loop-variable
    }
    res = [k + ' ' + str(int(k) - int(v)) for k, v in res.items()]
    return Dict(dict={'number of core electrons': res}).store()
