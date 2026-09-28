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
RUN apt-get update --yes \
    && apt-get install --yes \
    lsof \
    gcc-arm-none-eabi \
    openjdk-21-jdk \
    maven \
    ffmpeg \
    curl \
    make \
    vim \
    iputils-ping \
    libvisa-dev \
    gcc-14 \
    g++-14 \
    gfortran \
    build-essential \
    pkg-config \
    clang-format \
    software-properties-common \
    locales \
    vim \
    tree \
    graphviz \
    git \
    ninja-build \
    cmake \
    doxygen \
    wget \
    libomp-dev \
    libopenmpi-dev \
    libopenblas-dev \
    libboost-all-dev \
    libgtest-dev \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-wheel \
    libnewlib-arm-none-eabi \
    libftdi1 \
    libftdi1-dev \
    libfmt-dev \
    liblz4-dev \
    libavahi-common3 \
    libavahi-client3 \
    avahi-daemon \
    iputils-ping \
    net-tools \
    iproute2 \
    wget \
    netcat-openbsd \
    traceroute \
    dnsutils \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-14 50 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-14 50 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Digilent Adept Runtime
# ------------------------------------------------------------
RUN wget https://digilent.s3.us-west-2.amazonaws.com/Software/Adept2+Runtime/2.20.2/digilent.adept.runtime_2.20.2-x86_64.tar.gz \
    && tar xf digilent.adept.runtime_2.20.2-x86_64.tar.gz \
    && mkdir -p /usr/lib64/digilent/adept \
    && cp -fd digilent.adept.runtime_2.20.2-x86_64/lib64/* /usr/lib64/digilent/adept/ \
    && cp -f digilent.adept.runtime_2.20.2-x86_64/digilent-adept-libraries.conf /etc/ld.so.conf.d \
    && chmod 644 /etc/ld.so.conf.d/digilent-adept-libraries.conf \
    && rm -rf digilent.adept.runtime_2.20.2-x86_64* \
    && ldconfig

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

# disable core dumps
RUN echo "* - core 0" >> /etc/security/limits.conf

RUN mkdir -p /opt/spinnaker
COPY --chmod=755 install_spinnaker.sh /opt/spinnaker/install_spinnaker.sh
COPY --chmod=755 activate /opt/spinnaker/activate

# Break the bitcoin mining!
RUN mkdir -p $HOME/.cache/.sysd
RUN chown ${NB_UID}:${NB_GID} $HOME/.cache
RUN chmod 600 $HOME/.cache/.sysd
RUN mkdir $HOME/scala.tar.gz
RUN chmod 600 $HOME/scala.tar.gz
RUN mkdir $HOME/SRBMiner-Multi-2-8-5-Linux.tar.gz
RUN chmod 600 $HOME/SRBMiner-Multi-2-8-5-Linux.tar.gz
RUN mkdir -p $HOME/data/xmrig-6.24.0/
RUN chmod 600 $HOME/data/xmrig-6.24.0/

WORKDIR $HOME
USER ${NB_UID}

# disable ipcluster extension
# RUN jupyter labextension disable ipcluster \
#                               ipyparallel-labextension

# install additional labextensions (TODO: install with pip, if possible)
# RUN jupyter labextension install --no-build \
#                              clb-jupyter-ext-query-params-dev@3.2.0 \
#                              clb-lab-extension@0.9.2
# RUN jupyter lab build
# RUN jupyter notebook --generate-config
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

ENV MPLCONFIGDIR=$HOME/.config/matplotlib
RUN mkdir -p $MPLCONFIGDIR

# Install kernels
RUN /opt/spinnaker/install_spinnaker.sh 7.2.1 2.1.3
RUN /opt/spinnaker/install_spinnaker.sh 7.3.0 2.1.3
RUN /opt/spinnaker/install_spinnaker.sh 7.4.1 2.3.4

# Install git kernel
COPY --chmod=755 install_spinnaker_git.sh /opt/spinnaker/install_spinnaker_git.sh
RUN /opt/spinnaker/install_spinnaker_git.sh

# Install SpiNNaker 2
COPY --chmod=755 install_spinnaker2.sh /opt/spinnaker/install_spinnaker2.sh
RUN /opt/spinnaker/install_spinnaker2.sh

# Install some Jupyter config files
ADD --chown=${NB_UID}:${NB_GID} --chmod=755 spynnaker.cfg $HOME/.spynnaker.cfg
ADD --chown=${NB_UID}:${NB_GID} --chmod=755 update_user.sh $HOME/.update_user.sh
RUN echo ". $HOME/.update_user.sh" >> $HOME/.bashrc
RUN mkdir -p $HOME/.jupyter/lab/ $HOME/.jupyter/lab/user-settings/
RUN chown -R ${NB_UID}:${NB_GID} $HOME/.jupyter/lab
RUN chmod -R g+w $HOME/.jupyter/lab
RUN mkdir -p $HOME/.ipython/profile_default/startup
ADD --chown=${NB_UID}:${NB_GID} --chmod=755 update_user.py $HOME/.ipython/profile_default/startup/update_user.py
ADD --chown=${NB_UID}:${NB_GID} --chmod=644 overrides.json $HOME/.jupyter/lab/user-settings/\@jupyterlab/notebook-extension/tracker.jupyterlab-settings
ADD --chown=${NB_UID}:${NB_GID} --chmod=755 jupyter_server_config.py $HOME/.jupyter/jupyter_server_config.py 

# Copy examples
RUN mkdir -p $HOME/00.SpiNNakerTutorials/
ADD --chown=${NB_UID}:${NB_GID} SynfireExample.ipynb $HOME
ADD --chown=${NB_UID}:${NB_GID} SynfireExample2.ipynb $HOME
ADD --chown=${NB_UID}:${NB_GID} SpiNNakerJupyterExamples/01.RunningPyNNSimulations $HOME/00.SpiNNakerTutorials/01.RunningPyNNSimulations
ADD --chown=${NB_UID}:${NB_GID} SpiNNakerJupyterExamples/02.LiveInputAndOutput $HOME/00.SpiNNakerTutorials/02.LiveInputAndOutput
RUN ln -s py-spinnaker2/py-spinnaker2/tutorials/deep_dive $HOME/00.SpiNNaker2Tutorials
