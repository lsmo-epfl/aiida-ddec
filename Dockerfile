FROM yakutovich/aiida-complete

RUN apt-get update && apt-get install -y cp2k && service rabbitmq-server start

# Install AiiDA
USER aiida
ENV PATH="/home/aiida/.local/bin:${PATH}"
COPY . /home/aiida/code/aiida-ddec
WORKDIR /home/aiida/code/aiida-ddec
RUN pip install --user  .[pre-commit,testing]
RUN pip install --user  git+https://github.com/kjappelbaum/aiida-cp2k.git@aiida1_multistage && pip install --user pytest-azurepipelines
COPY .ci/chargemol/ddec /usr/bin
USER root
