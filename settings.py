import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID= os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_URI = os.getenv("CLIENT_URI")
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_VERIFICATION_TOKEN = os.getenv('SLACK_VERIFICATION_TOKEN')
SLACK_WEBHOOK_SECRET = os.getenv('SLACK_WEBHOOK_SECRET')
MONGODB_SECRET = os.getenv('MONGODB_SECRET')