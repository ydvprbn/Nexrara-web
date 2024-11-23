from dotenv import load_dotenv
import os

load_dotenv()

database_hostname = os.environ.get("database_hostname")
database_port = os.environ.get("database_port")
database_password = os.environ.get("database_password")
database_name = os.environ.get("database_name")
database_username = os.environ.get("database_username")
secret_key = os.environ.get("secret_key")
algorithm = os.environ.get("algorithm")
access_token_expire_minutes = os.environ.get("access_token_expire_minute")
