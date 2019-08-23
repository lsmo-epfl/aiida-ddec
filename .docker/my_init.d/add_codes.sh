# Install the ddec and cp2k codes
DDEC_FOLDER=/home/aiida/code/aiida-ddec
su aiida -c "verdi code show ddec@localhost || verdi code setup --config ${DDEC_FOLDER}/.docker/ddec-code.yml --non-interactive"
su aiida -c "verdi code show cp2k@localhost || verdi code setup --config ${DDEC_FOLDER}/.docker/cp2k-code.yml --non-interactive"
