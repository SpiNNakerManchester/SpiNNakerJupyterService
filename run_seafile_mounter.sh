#!/bin/bash
BASE=/localhome/jupyteruser
MOUNTER=$BASE/SpiNNakerJupyterService/seafile_mounter
source $MOUNTER/venv/bin/activate
python $MOUNTER/seafile_mounter.py -m $BASE/drive/ -d $BASE/drive_data/ -c $MOUNTER/seadrive.conf -r https://drive.ebrains.eu/ -b /usr/local/bin/seadrive
