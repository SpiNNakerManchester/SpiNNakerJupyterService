#!/bin/bash
# Install the release version
version=$1
pyver=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}');")
VENV_PATH=$HOME/sPyNNakerGit/
python -m venv $VENV_PATH
cp /opt/spinnaker/activate $VENV_PATH/bin/
source $VENV_PATH/bin/activate
pip install --upgrade wheel setuptools pip ipykernel
cd $VENV_PATH
git clone https://github.com/SpiNNakerManchester/SupportScripts ./support
git clone https://github.com/SpiNNakerManchester/SpiNNUtils
cd SpiNNUtils && python setup.py develop && cd ..
./support/install.sh all -y
./support/setup.sh
./support/automatic_make.sh
mvn -f JavaSpiNNaker -DskipTests clean package
python -m spynnaker.pyNN.setup_pynn
python -m ipykernel install --user --name sPyNNakerGit
