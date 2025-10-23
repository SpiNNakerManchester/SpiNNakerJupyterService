from configparser import ConfigParser
import os

home = os.getenv("HOME")
user = os.getenv("JUPYTERHUB_USER")
config_file = f"{home}/.spynnaker.cfg"

config = ConfigParser()
config.read(config_file)

if 'Machine' in config and 'spalloc_user' in config['Machine']:
    if config['Machine']['spalloc_user'] == "JupyterUser":
        config['Machine']['spalloc_user'] = f"JupyterUser-{user}"
        with open(config_file, "w") as f:
            config.write(f)
