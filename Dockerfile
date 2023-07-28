FROM aiidateam/aiida-core:2.3.1

# Install cp2k
RUN apt-get update && apt-get install -y --no-install-recommends  \
    cp2k

# Download and install Chargemol
WORKDIR /opt/code
RUN wget https://sourceforge.net/projects/ddec/files/latest/download -O chargemol.zip
RUN unzip chargemol.zip
RUN chmod 755 chargemol_09_26_2017/chargemol_FORTRAN_09_26_2017/compiled_binaries/linux/Chargemol_09_26_2017_linux_parallel

COPY . /opt/aiida-ddec
RUN pip install -e /opt/aiida-ddec[pre-commit,tests]

# # Install the ddec and cp2k codes
COPY .docker/opt/add-codes.sh /opt/add-codes.sh
COPY .docker/my_init.d/add-codes.sh /etc/my_init.d/50_add-codes.sh

# COPY the examples test script
COPY .github/workflows/run_examples.sh /home/aiida/run_examples.sh
