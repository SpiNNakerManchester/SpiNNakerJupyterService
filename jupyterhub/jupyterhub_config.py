import os

###########
# Spawner #
###########

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Spawn containers from this image
c.DockerSpawner.image = os.environ["DOCKER_NOTEBOOK_IMAGE"]

# Set up Docker network
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']

# Set up Notebook directory
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = "/home/jovyan/"
c.DockerSpawner.volumes = {
    "/localhome/jupyteruser/work/{username}/": notebook_dir
}

# Delete containers when user logs out
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# def auth_state_hook(spawner, auth_state):
#    spawner.log.info(f"Auth: {auth_state}")#
#c.DockerSpawner.auth_state_hook = auth_state_hook

async def pre_spawn(spawner):
    from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPClientError, HTTPClient

    username = spawner.user.name
    spawner.log.info(f"Making folder for {username}")
    workdir = f"/work/{username}/"
    os.makedirs(workdir, exist_ok=True)
    os.chown(workdir, 1000, 100)
    auth_state = await spawner.user.get_auth_state()
    if auth_state is None:
        spawner.log.info("No auth state found")
        return
    scope = auth_state.get("scope")
    if scope is not None and 'collab.drive' in scope:
        client = AsyncHTTPClient()
        spawner.log.info("Mounting collab drive")
        drive_request = HTTPRequest(
            f"http://host.docker.internal:5000/mount/{username}"
            f"?token={auth_state['access_token']}")
        await client.fetch(drive_request)
        spawner.log.info("Mounted Drive")
        spawner.volumes.update({
            f'/localhome/jupyteruser/drive/{username}': {
                "bind": "/home/jovyan/drive",
                "mode": "rw",
                "propagation": "rshared"
            }
        })

async def post_stop(spawner):
    from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPClientError, HTTPClient

    username = spawner.user.name
    auth_state = await spawner.user.get_auth_state()
    if auth_state is None:
        spawner.log.info("No auth state found")
        return
    scope = auth_state.get("scope")
    if scope is not None and 'collab.drive' in scope:
        client = AsyncHTTPClient()
        spawner.log.info("Unmounting collab drive")
        drive_request = HTTPRequest(
            f"http://host.docker.internal:5000/unmount/{username}")
        await client.fetch(drive_request)
        spawner.log.info("Unmounted Drive")

c.DockerSpawner.pre_spawn_hook = pre_spawn
c.DockerSpawner.post_stop_hook = post_stop


##################
# Authentication #
##################

from oauthenticator.oauth2 import OAuthenticator
from oauthenticator.google import GoogleOAuthenticator


# Use OAuth2
c.JupyterHub.authenticator_class = "multiauthenticator.MultiAuthenticator"
c.MultiAuthenticator.authenticators = [(
    OAuthenticator, 
    "/ebrains", 
    {
        "oauth_callback_url": 'https://sands.cs.man.ac.uk/hub/ebrains/oauth_callback',
        "client_id": 'spinnaker-jupyter-ebrains',
        "client_secret": '1fdaf78b-cb2e-4c3e-9f67-19dff013f937',
        "scope": ['openid', 'profile', 'clb.drive:read', 'clb.drive:write', 'collab.drive', 'email'],
        "token_url": 'https://iam.ebrains.eu/auth/realms/hbp/protocol/openid-connect/token',
        "userdata_url": 'https://iam.ebrains.eu/auth/realms/hbp/protocol/openid-connect/userinfo',
        "authorize_url": 'https://iam.ebrains.eu/auth/realms/hbp/protocol/openid-connect/auth',
        "username_claim": 'preferred_username',
        "service_name": 'EBRAINS Credentials',
        "login_service": 'ebrains',
        "enable_auth_state": True
    }), (
    GoogleOAuthenticator, "/google", 
    {
        "oauth_callback_url": "https://sands.cs.man.ac.uk/hub/google/oauth_callback",
        "client_id": "180682199926-jkrhd2t9j6j00s4gvmmqa4q9eisum635.apps.googleusercontent.com",
        "client_secret": "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",
        "service_name": 'Google',
        "login_service": "google",
        "enable_auth_state": True
    }),
]
c.MultiAuthenticator.custom_html = """
<div class="service-login">
    <a role="button" class='btn btn-jupyter btn-lg' href='https://sands.cs.man.ac.uk/hub/ebrains/oauth_login'>
    Sign in with EBRAINS
    </a>
</div>
<div class="service-login">
    <a role="button" class='btn btn-jupyter btn-lg' href='https://sands.cs.man.ac.uk/hub/google/oauth_login'>
    Sign in with Google
    </a>
</div>

"""
# c.OAuthenticator.drive_url = 'https://drive.ebrains.eu'

# Allow all signed-up users to login
c.Authenticator.allow_all = True

# Set the administrator user(s)
admin = os.environ.get("JUPYTERHUB_ADMIN")
if admin:
    c.Authenticator.admin_users = [admin]

#########
# Other #
#########

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = 8080

c.JupyterHub.shutdown_on_logout = True
