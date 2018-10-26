#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
import sys
import os
import click

from aiida.common.example_helpers import test_and_get_code
from aiida.orm.data.parameter import ParameterData

input_dict = {
        "net charge": 0.0,
        "charge type": "DDEC6",
        "periodicity along A, B, and C vectors" : [True, True, True,],
        "compute BOs" : False,
        "atomic densities directory complete path" : "/home/yakutovi/chargemol_09_26_2017/atomic_densities/",
        "input filename" : "valence_density",
        "number of core electrons":[
            "1  0",
            "2  0",
            "3  0",
            "4  0",
            "5  2",
            "6  2",
            "7  2",
            "8  2",
            "9  2",
            "10 2",
            "11 2",
            "12 2",
            "13 10",
            "14 10",
            "15 10",
            "16 10",
            "17 10",
            "18 10",
            "19 10",
            "20 10",
            "21 10",
            "22 10",
            "23 10",
            "24 10",
            "25 10",
            "26 10",
            "27 10",
            "28 10",
            "29 18",
            "30 18",
            "35 28",
            "53 46",
            ]
        }

@click.command('cli')
@click.argument('codename')
@click.argument('cp2k_calculation_pk')
@click.option('--submit', is_flag=True, help='Actually submit calculation')
def main(codename, cp2k_calculation_pk, submit):
    """Command line interface for testing and submitting calculations.

    Usage: ./cli.py CODENAME CP2K_CALCULATION
    
    CODENAME       from "verdi code setup"

    COMPUTER_NAME  from "verdi calculation list -a"

    This script extends submit.py, adding flexibility in the selected code/computer.
    """
    code = test_and_get_code(codename, expected_code_type='ddec')

    # input parameters
    parameters = ParameterData(dict=input_dict)

    # set up calculation
    calc = code.new_calc()
    calc.label = "aiida_plugin_template computes 2*3"
    calc.description = "Test job submission with the aiida_plugin_template plugin"
    calc.set_max_wallclock_seconds(30 * 60)  # 30 min

    calc.set_withmpi(False)
    calc.set_resources({"num_machines": 1})
    calc.use_parameters(parameters)

    # use cp2k calculations
    cp2k_calc = load_node(int(cp2k_calculation_pk))
    calc.use_charge_density_folder(cp2k_calc.out.remote_folder)

    if submit:
        calc.store_all()
        calc.submit()
        print("submitted calculation; calc=Calculation(uuid='{}') # ID={}"\
                .format(calc.uuid,calc.dbnode.pk))
    else:
        subfolder, script_filename = calc.submit_test()
        path = os.path.relpath(subfolder.abspath)
        print("submission test successful")
        print("Find remote folder in {}".format(path))
        print("In order to actually submit, add '--submit'")


if __name__ == '__main__':
    main()
