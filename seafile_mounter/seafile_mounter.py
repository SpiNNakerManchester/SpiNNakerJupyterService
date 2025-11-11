import flask
import os
from os.path import isdir, isfile
import subprocess
from configparser import ConfigParser
from flask import request
import signal
import argparse
import shutil
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPClientError, HTTPClient


app = flask.Flask(__name__)
app.config["DEBUG"] = True


__processes_by_user = dict()
__mount_dir = None
__data_dir = None
__default_drive_config = None
__seadrive_bin = None
__uid = None
__gid = None
__drive_url = None


def __mkdir(d):
    if not os.path.exists(d):
        os.makedirs(d)
        return True
    return False


async def __get_drive_token(token):
    global __drive_url
    client = AsyncHTTPClient()
    request = HTTPRequest(
        __drive_url + '/api2/account/token/',
        headers={'Authorization': f'Bearer {token}'},
        connect_timeout=1.0,
        request_timeout=1.0
    )
    try:
        # Get the drive token
        resp = await client.fetch(request)
        return resp.body.decode('utf-8')

    except HTTPClientError as e:
        print("Failed to obtain drive token or mount drive.\n"
              f"Exception: {e}")

def check_path_safe(base_path, check_path):
    abs_base = os.path.abspath(base_path)
    abs_check = os.path.abspath(check_path)
    return os.path.commonprefix([abs_base, abs_check]) == abs_base


@app.route("/prepare/<username>")
async def prepare(username):
    global __data_dir
    global __mount_dir
    global __default_drive_config

    token = request.args.get("token")
    if token is None:
        app.logger.error("No token for {}".format(username))
        return "Missing token", 500

    user_drive_mnt = os.path.join(__mount_dir, username)
    if not check_path_safe(__mount_dir, user_drive_mnt):
        app.logger.error("Invalid mount path for {}".format(username))
        return "Invalid mount path", 500

    # Unmount if the directory exists (ignore errors)
    try:
        if os.path.exists(user_drive_mnt):
            unmount(username)
    except Exception:
        app.logger.exception("Ignoring unmount error for {}".format(username))
        pass

    try:
        # Make directories to do the mounting
        user_drive_data = os.path.join(__data_dir, username)
        if not check_path_safe(__data_dir, user_drive_data):
            app.logger.error("Invalid data path for {}".format(username))
            return "Invalid data path", 500
        __mkdir(user_drive_data)
        __mkdir(user_drive_mnt)

        # Write the config for mounting the drive
        user_drive_cfg = os.path.join(user_drive_data, "seadrive.conf")
        config = ConfigParser()
        config.read(__default_drive_config)
        config['account']['username'] = username
        config['account']['token'] = await __get_drive_token(token)
        with open(user_drive_cfg, "w") as configfile:
            config.write(configfile)

    except Exception:
        app.logger.exception("Error mounting for {}".format(username))
        return {
            "result": False,
        }, 500

    return {"result": True}


@app.route("/mount/<username>")
async def mount(username):
    global __processes_by_user
    global __data_dir
    global __mount_dir
    global __seadrive_bin
    global __uid
    global __gid

    await prepare(username)

    try:
        user_drive_mnt = os.path.join(__mount_dir, username)
        if not check_path_safe(__mount_dir, user_drive_mnt):
            app.logger.error("Invalid mount path for {}".format(username))
            return "Invalid mount path", 500
        user_drive_data = os.path.join(__data_dir, username)
        if not check_path_safe(__data_dir, user_drive_data):
            app.logger.error("Invalid data path for {}".format(username))
            return "Invalid data path", 500
        user_drive_cfg = os.path.join(user_drive_data, "seadrive.conf")
        user_drive_data_folder = os.path.join(user_drive_data, "data")

        # Do the mount (fuse)
        app.logger.info("Starting the mount for {} in {}".format(username, user_drive_mnt))
        drive_process = subprocess.Popen(" ".join([
            __seadrive_bin, "-c", user_drive_cfg, "-f",
            "-d", user_drive_data_folder, "-o", f"uid={__uid},gid={__gid},allow_other,umask=002",
            user_drive_mnt]), shell=True)
        app.logger.info("Mount done for {} in {}".format(username, user_drive_mnt))

        # Store the process to be cleared later
        __processes_by_user[username] = drive_process

    except Exception:
        app.logger.exception("Error mounting for {}".format(username))
        return {
            "result": False,
        }, 500

    return {"result": True}


@app.route("/unmount/<username>")
def unmount(username):
    global __processes_by_user

    # Unmount using fusermount
    app.logger.info("Unmounting for {} using fusermount".format(username))
    user_drive_mnt = os.path.join(__mount_dir, username)
    if not check_path_safe(__mount_dir, user_drive_mnt):
        app.logger.error("Invalid mount path for {}".format(username))
        return "Invalid mount path", 500
    subprocess.run(["fusermount", "-u", user_drive_mnt])

    # If the process was started here, stop it now
    if username in __processes_by_user:
        app.logger.info("Stopping mount process for {}".format(username))
        drive_process = __processes_by_user[username]
        del __processes_by_user[username]
        drive_process.send_signal(signal.SIGINT)
        drive_process.wait()
        del drive_process

        # And delete everything (only caches anyway)
        # user_drive_mnt = os.path.join(__mount_dir, username)
        user_drive_data = os.path.join(__data_dir, username)
        if not check_path_safe(__data_dir, user_drive_data):
            app.logger.error("Invalid data path for {}".format(username))
            return "Invalid data path", 500
        try:
            # shutil.rmtree(user_drive_mnt)
            shutil.rmtree(user_drive_data)
        except Exception:
            app.logger.exception("Error removing drive paths for {}".format(username))

    return {"result": True}


parser = argparse.ArgumentParser(
    description="REST service for mounting Seadrive for docker users")
parser.add_argument("-m", "--mountdir", required=True,
                    help="Directory to mount into")
parser.add_argument("-d", "--datadir", required=True,
                    help="Directory to store data in")
parser.add_argument("-c", "--config", required=True,
                    help="Default config file to fill in")
parser.add_argument("-p", "--port", required=False, default=5000,
                    help="Port to listen on")
parser.add_argument("-b", "--binary", required=True,
                    help="Seadrive-cli instance to use")
parser.add_argument("-u", "--uid", required=False, default=1000,
                    help="User id to serve files using")
parser.add_argument("-g", "--gid", required=False, default=100,
                    help="Group id to serve files using")
parser.add_argument("-r", "--driveurl", required=True,
                    help="The URL of the seafile drive")

args = parser.parse_args()
__mount_dir = args.mountdir
__data_dir = args.datadir
__default_drive_config = args.config
__seadrive_bin = args.binary
__uid = args.uid
__gid = args.gid
__drive_url = args.driveurl

if not isdir(__mount_dir):
    raise ValueError(f"Mount Directory {__mount_dir} must be an existing directory")
if not isdir(__data_dir):
    raise ValueError(f"Data Directory {__data_dir} must be an existing directory")
if not isfile(__default_drive_config):
    raise ValueError(f"Default config {__default_drive_config} must be an existing file")
if not isfile(__seadrive_bin):
    raise ValueError(f"Seadrive client binary {__seadrive_bin} must be an existing file")

app.run(host="0.0.0.0", port=args.port)
