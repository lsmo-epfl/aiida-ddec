#!/usr/bin/env bash
# <pre>/home/aiida/code/aiida-ddec/aiida_ddec/tests/
# /home/aiida/code/aiida-ddec/aiida_ddec/tests/

chown -R aiida /home
/sbin/my_init
su -c "export PATH=/home/aiida/.local/bin:$PATH  && verdi daemon status && py.test --verbose --junitxml=test-results.xml" aiida
