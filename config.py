from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
# POSTGRES_HOST = 'db'
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
# POSTGRES_PORT = '5432'
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DATABASE = os.getenv('POSTGRES_DB')
UPLOAD_FOLDER = 'uploaded_images'
TOKEN_TTL = os.getenv("TOKEN_TTL", 86400)

DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
