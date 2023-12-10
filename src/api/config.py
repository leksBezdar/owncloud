import os

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.environ.get("ROOT_DIR")
UPLOAD_DIR = os.environ.get("UPLOAD_DIR")
