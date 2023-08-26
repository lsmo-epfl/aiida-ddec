#!/bin/bash

verdi run /opt/aiida-ddec/examples/test_cp2k_ddec_h2o.py --ddec-code ddec@localhost --cp2k-code cp2k
verdi run /opt/aiida-ddec/examples/run_cp2k_ddec_Zn-MOF-74.py --ddec-code ddec@localhost --cp2k-code cp2k
