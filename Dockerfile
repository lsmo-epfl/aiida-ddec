FROM aiidateam/aiida-docker-stack

# Install cp2k
RUN apt-get update && apt-get install -y --no-install-recommends  \
    cp2k

# Set HOME variable:
ENV HOME="/home/aiida"


# Copy the current folder and change permissions
COPY . ${HOME}/code/aiida-ddec
RUN chown -R aiida:aiida ${HOME}/code

# Install AiiDA
USER aiida
ENV PATH="${HOME}/.local/bin:${PATH}"

# Download and install Chargemol
#WORKDIR ${HOME}/code/
#RUN wget https://sourceforge.net/projects/ddec/files/latest/download -O chargemol.zip
#RUN unzip chargemol.zip
#RUN chmod 755 chargemol_09_26_2017/chargemol_FORTRAN_09_26_2017/compiled_binaries/linux/Chargemol_09_26_2017_linux_parallel


# Install aiida-ddec plugin and it's dependencies
WORKDIR ${HOME}/code/aiida-ddec
RUN pip install --user .[cp2k,pre-commit,testing]

# Populate reentry cache for aiida user https://pypi.python.org/pypi/reentry/
RUN reentry scan

# Install the ddec and cp2k codes
COPY .docker/opt/add-codes.sh /opt/
COPY .docker/my_init.d/add-codes.sh /etc/my_init.d/40_add-codes.sh

# Change workdir back to $HOME
WORKDIR ${HOME}

# Important to end as user root!
USER root

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]
