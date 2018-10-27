"""Configuration loader for different environments."""
import base64
import get_config

CONFIG = get_config.get_config()


class Config(object):
    def __init__(self, app):
        self.app = app

        self.environment = CONFIG('environment', default='development')
        self.settings = self._init_env()

    def _init_env(self):
        return DefaultConfig()


class DefaultConfig(object):
    """Defaults for the configuration objects."""
    DEBUG = bool(CONFIG('debug', namespace=None, default='True'))
    TESTING = bool(CONFIG('testing', namespace=None, default='False'))
    CSRF_ENABLED = bool(CONFIG('csrf_enabled', default='True'))
    PERMANENT_SESSION = bool(CONFIG('permanent_session', namespace=None, default='True'))
    PERMANENT_SESSION_LIFETIME = int(CONFIG('permanent_session_lifetime', namespace=None, default='86400'))

    SESSION_COOKIE_HTTPONLY = bool(CONFIG('session_cookie_httponly', namespace=None, default='True'))
    LOGGER_NAME = CONFIG('logger_name', namespace=None, default='nhobot')

    SECRET_KEY = CONFIG('auth_secret', namespace=None)
    SERVER_NAME = CONFIG('server_name', namespace=None, default='localhost:5000')

    # S3_BUCKET = CONFIG('s3_bucket', namespace=None)

    CDN = 'https://cdn.{SERVER_NAME}'.format(SERVER_NAME=SERVER_NAME)

    # FORBIDDEN_PAGE_PUBLIC_KEY = base64.b64decode(
    #     CONFIG('forbidden_page_public_key', namespace=None)
    # )

    PREFERRED_URL_SCHEME = CONFIG('preferred_url_scheme', namespace=None, default='https')


class OIDCConfig(object):
    """Convienience Object for returning required vars to flask."""
    def __init__(self):
        """General object initializer."""
        CONFIG = get_config.get_config()
        self.OIDC_DOMAIN = CONFIG('AUTH_HOST', namespace=None)
        self.OIDC_CLIENT_ID = CONFIG('AUTH_ID', namespace=None)
        self.OIDC_CLIENT_SECRET = CONFIG(
            'AUTH_SECRET', namespace=None
        )
        self.LOGIN_URL = "https://{DOMAIN}/login?client={CLIENT_ID}".format(
            DOMAIN=self.OIDC_DOMAIN,
            CLIENT_ID=self.OIDC_CLIENT_ID
        )

    @property
    def client_id(self):
        return self.OIDC_CLIENT_ID

    @property
    def client_secret(self):
        return self.OIDC_CLIENT_SECRET

    def auth_endpoint(self):
        return "https://{DOMAIN}/authorize".format(
            DOMAIN=self.OIDC_DOMAIN
        )

    def token_endpoint(self):
        return "https://{DOMAIN}/oauth/token".format(
            DOMAIN=self.OIDC_DOMAIN
        )

    def userinfo_endpoint(self):
        return "https://{DOMAIN}/userinfo".format(
            DOMAIN=self.OIDC_DOMAIN
        )
