from flask import Flask, request, render_template, redirect, url_for, session, make_response, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import slackclient

from apscheduler.schedulers.background import BackgroundScheduler

import holidays

import logging.config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('newbie')
scheduler = BackgroundScheduler()

# auth
from flask_cors import CORS as cors
from flask_environ import get, collect, word_for_true
from authlib.flask.client import OAuth
from functools import wraps
from newbie import auth, config, settings

# endauth

current_host = 'https://nhobot.ngrok.io'

app = Flask(__name__, static_url_path='/static')
app.secret_key = settings.MONGODB_SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
cors(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET
print(f'client secret {client_secret}')
client_uri = settings.CLIENT_URI
client_audience = settings.CLIENT_AUDIENCE


slack_verification_token = settings.SLACK_VERIFICATION_TOKEN

slack_client = slackclient.SlackClient(settings.SLACK_BOT_TOKEN)

all_timezones = settings.all_timezones
us_holidays = holidays.US()
ca_holidays = holidays.CA()


message_frequency = {'day': 1, 'week': 7, 'month': 30, 'year': 365}

# auth
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=settings.AUTH_ID,
    client_secret=settings.AUTH_SECRET,
    api_base_url='https://' + settings.AUTH_HOST,
    access_token_url='https://' + settings.AUTH_HOST + '/oauth/token',
    authorize_url='https://' + settings.AUTH_HOST + '/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)

app.config.update(collect(
    get('DEBUG', default=True, convert=word_for_true),
    get('HOST', default='localhost'),
    get('PORT', default=5000, convert=int),
    get('AUTH_ID', default=settings.AUTH_ID),
    get('AUTH_SECRET', default=settings.AUTH_SECRET),
    get('AUTH_HOST', default=settings.AUTH_HOST),
    get('AUTH_SCOPE', default='openid email profile'),
    get('AUTH_AUDIENCE', default=settings.AUTH_AUDIENCE),
    get('AUTH_SECRET_KEY', default=settings.AUTH_SECRET_KEY)))

AUTH_AUDIENCE = settings.AUTH_AUDIENCE
if AUTH_AUDIENCE is '':
    AUTH_AUDIENCE = 'https://' + app.config.get('HOST') + '/userinfo'

# This will be the callback URL Auth0 returns the authenticate to.
# app.config['AUTH_URL'] = 'https://{}:{}/callback/auth'.format(app.config.get('HOST'), app.config.get('PORT'))
app.config['AUTH_URL'] = 'https://nhobot.ngrok.io/callback/auth'


oidc_config = config.OIDCConfig()
authentication = auth.OpenIDConnect(
    oidc_config
)
oidc = authentication.auth(app)
# endauth

admin_people = []