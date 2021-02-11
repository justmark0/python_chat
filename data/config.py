from dotenv import load_dotenv
from pathlib import Path
import os

# Server data
HOST = "0.0.0.0"
PORT = 4702

# Chat data
max_symbols_in_message = 600

# Encryption options
RSA_KEY_LENGTH = 512
rsa_max_length = {"128": 5, "256": 21, "384": 37, "512": 53, "1024": 117, "2048": 245, "3072": 373, "4096": 501}

# Account data
my_default_name = 'mark'

# database setup
DB_URI = os.getenv("DB_URI")
