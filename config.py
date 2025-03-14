import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'generate_a_random_secret_key_and_keep_it_secret'
    
    # Database settings
    DB_NAME = os.environ.get('DB_NAME') or 'contas'
    DB_USER = os.environ.get('DB_USER') or 'andrino'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'Rebecca@2023'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    
    # Database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
