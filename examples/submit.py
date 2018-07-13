# -*- coding: utf-8 -*-
"""Submit a test calculation on localhost.

Usage: verdi run submit.py

Note: This script assumes you have set up computer and code as in README.md.
"""
import os
from aiida.orm import load_node
from aiida.orm.data.parameter import ParameterData
input_dict = {
        "net charge": 0.0,
        "charge type": "DDEC6",
        "periodicity along A, B, and C vectors" : [True, True, True,],
        "compute BOs" : False,
        "atomic densities directory complete path" : "/scratch/snx3000/ongari/atomic_densities/",
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
parameters = ParameterData(dict=input_dict)

# use code name specified using 'verdi code setup'
code = Code.get_from_string('ddec')

# use computer name specified using 'verdi computer setup'
computer = Computer.get('daint-s761')


# set up calculation
calc = code.new_calc()
calc.label = "Computing DDEC point charges"
calc.set_prepend_text("export OMP_NUM_THREADS=12")
calc.description = "Test job submission with the aiida_plugin_template plugin"
calc.set_max_wallclock_seconds(4 * 60 * 60)  # 30 min
# This line is only needed for local codes, otherwise the computer is
# automatically set from the code
calc.set_computer(computer)
calc.set_withmpi(False)
calc.set_resources({"num_machines": 1, "num_mpiprocs_per_machine":1})
calc.use_parameters(parameters)

# use cp2k calculations
cp2k_calc = load_node(2590)
pf = cp2k_calc.out.remote_folder
calc.use_electronic_calc_folder(pf)

calc.store_all()
calc.submit()
print("submitted calculation; calc=Calculation(uuid='{}') # ID={}"\
        .format(calc.uuid,calc.dbnode.pk))
