from dotenv import load_dotenv
from pathlib import Path
import os

# Server data
HOST = "0.0.0.0"
PORT = 4702

# Encryption options
RSA_KEY_LENGTH = 512


# Account data
my_default_name = 'mark'

# database setup
DB_URI = os.getenv("DB_URI")
