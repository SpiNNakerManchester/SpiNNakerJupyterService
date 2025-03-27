# SpiNNakerJupyterService
Jupyter Service Files for running a SpiNNaker Jupyter Service

## Setup

1. Check out this repository somewhere, and call it $JHOME
2. Install Docker, Python, fuse3, supervisor and nginx.
3. Build the Jupyterhub service image
    ``` docker compose --project_directory $JHOME/SpiNNakerJupyterService/jupyterhub build ```
4. Build the Jupyter user image
    ``` docker build -t spinnaker_jupyter $JHOME/SpiNNakerJupyterService/SpiNNakerJupyter ```
5. (Download)[https://s3.eu-central-1.amazonaws.com/download.seadrive.org/SeaDrive-cli-x86_64-3.0.13.AppImage] and (install)[https://help.seafile.com/drive_client/drive_client_for_linux/#running-seadrive-without-gui] the Seadrive cli.  Only the copying of the client to "seadrive" and making it executable is necessary.
6. Make a virtualenv for the seafile mounter
    ``` python -m virtualenv $JHOME/SpiNNakerJupyterService/seafile_mounter/venv ```
7. Install the requirements for the seafile mounter
    ``` source $JHOME/SpiNNakerJupyterService/seafile_mounter/venv && pip -r $JHOME/SpiNNakerJupyterService/seafile_mounter/requirements.txt ```
8. Copy or link the files in $JHOME/SpiNNakerJupyterService/supervisor.d/ to /etc/supervisor.d/ and restart supervisord
9. Copy or link $JHOME/SpiNNakerJupyterService/nginx/jupyterhub to /etc/nginx/sites-enabled and restart nginx
