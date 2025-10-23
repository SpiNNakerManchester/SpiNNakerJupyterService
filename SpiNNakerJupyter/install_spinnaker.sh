#!/bin/bash
# Install the release version
version=$1
numpy_version=$2
pyver=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}');")
VENV_PATH=$HOME/.kernels/sPyNNaker_$version/
python -m venv $VENV_PATH
cp /opt/spinnaker/activate $VENV_PATH/bin/
source $VENV_PATH/bin/activate
pip install --upgrade setuptools wheel pip "numpy==$numpy_version" "spynnaker==1!$version" "spinnakergraphfrontend==1!$version" ipykernel
python -m spynnaker.pyNN.setup_pynn
python -m ipykernel install --user --name sPyNNaker_$version
mkdir -p $VENV_PATH/lib/python$pyver/JavaSpiNNaker/SpiNNaker-front-end/target/
wget https://github.com/SpiNNakerManchester/JavaSpiNNaker/releases/download/$version/spinnaker-exe.jar \
    -O  $VENV_PATH/lib/python$pyver/JavaSpiNNaker/SpiNNaker-front-end/target/spinnaker-exe.jar
