#!/usr/bin/env bash
# <pre>/home/aiida/code/aiida-ddec/aiida_ddec/tests/
# /home/aiida/code/aiida-ddec/aiida_ddec/tests/

/sbin/my_init
chown -R aiida /home
su -c "export PATH=/home/aiida/.local/bin:$PATH && py.test --junitxml=test-results.xml" aiida
