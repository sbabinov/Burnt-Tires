import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
SERVICE_DB_PATH = os.path.join(os.getenv("SERVICE_DB_PATH"))

admins = [
    1005532278,
]
