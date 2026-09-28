#!/bin/bash
# Install the release version
VENV_PATH=$HOME/py-spinnaker2/
python3.12 -m venv $VENV_PATH
source $VENV_PATH/bin/activate
pip install --upgrade setuptools wheel pip ipykernel
pip install numpy \
        scipy \
        pytest \
        pytest-cov \
        pytest-mock \
        setuptools==81.0.0\
        wheel==0.47.0 \ 
        ruff==0.12.0 \
        pillow>=12.3.0 \
        tensorflow
pip install \
        torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

cd $VENV_PATH
git clone https://gitlab.com/spinnaker2/py-spinnaker2.git
cd py-spinnaker2
git submodule set-url src/spinnaker2/libs https://gitlab.com/spinnaker2/snn-core.git
git submodule init
git submodule update --recursive
pip install -e .'[dev]'

python -m ipykernel install --user --name py-spinnaker2
