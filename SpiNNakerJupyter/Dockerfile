FROM quay.io/jupyter/minimal-notebook

LABEL maintainer="SpiNNaker Team"

ENV USER="${NB_USER}" \
    SHELL=/bin/bash \
    SSL_CERT_DIR=/etc/ssl/certs \
    XDG_CACHE_HOME=/tmp/cache/ \
    LAB_IMAGE_NAME=SpiNNaker

USER root

# Set the UK timezone (necessary to make r-base install noninteractive)
RUN ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime

# Set to noninteractive for install
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --yes && \
    apt-get install --yes \
    gcc \
    lsof \
    gcc-arm-none-eabi \
    openjdk-17-jdk \
    maven \
    ffmpeg \
    curl \
    make \
    vim  && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install nodejs
ENV NODE_VERSION=16.13.0
ENV NVM_DIR=/root/.nvm
RUN mkdir $NVM_DIR && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
RUN . "$NVM_DIR/nvm.sh" && \
    nvm install ${NODE_VERSION} && \
    nvm use v${NODE_VERSION} && \
    nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"

# install pip packages
COPY base/requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# disable ipcluster extension
# RUN jupyter labextension disable ipcluster \
#                               ipyparallel-labextension

# install additional labextensions (TODO: install with pip, if possible)
# RUN jupyter labextension install --no-build \
#                              clb-jupyter-ext-query-params-dev@3.2.0 \
#                              clb-lab-extension@0.9.2
# RUN jupyter lab build
# RUN jupyter notebook --generate-config
# RUN mkdir -p $HOME/.ipython/profile_default/startup/

# disable core dumps
RUN echo "* - core 0" >> /etc/security/limits.conf

RUN mkdir -p /opt/spinnaker
COPY --chmod=755 install_spinnaker.sh /opt/spinnaker/install_spinnaker.sh
COPY --chmod=755 activate /opt/spinnaker/activate

WORKDIR $HOME
USER ${NB_UID}

COPY spynnaker.cfg $HOME/.spynnaker.cfg
COPY --chmod=755 update_user.sh $HOME/.update_user.sh
RUN echo ". $HOME/.update_user.sh" >> $HOME/.bashrc

ENV MPLCONFIGDIR=$HOME/.config/matplotlib
RUN mkdir -p $MPLCONFIGDIR

# Install kernels
RUN /opt/spinnaker/install_spinnaker.sh 7.2.1
RUN /opt/spinnaker/install_spinnaker.sh 7.3.0

# Install git kernel
COPY --chmod=755 install_spinnaker_git.sh /opt/spinnaker/install_spinnaker_git.sh
RUN /opt/spinnaker/install_spinnaker_git.sh

# Copy examples
ADD --chown=${NB_UID}:${NB_GID} SynfireExample.ipynb $HOME
ADD --chown=${NB_UID}:${NB_GID} SpiNNakerJupyterExamples/01.RunningPyNNSimulations $HOME/01.RunningPyNNSimulations
ADD --chown=${NB_UID}:${NB_GID} SpiNNakerJupyterExamples/02.LiveInputAndOutput $HOME/02.LiveInputAndOutput
