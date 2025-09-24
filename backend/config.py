# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///trendtracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PLATFORM_APIS = {
        'youtube': {
            'api_key': os.environ.get('YOUTUBE_API_KEY')
        },
        'reddit': {
            'client_id': os.environ.get('REDDIT_CLIENT_ID'),
            'client_secret': os.environ.get('REDDIT_CLIENT_SECRET'),
        },
        'twitter': {
            'bearer_token': os.environ.get('TWITTER_BEARER_TOKEN')
        },
        'tiktok': {
            'api_key': os.environ.get('TIKTOK_API_KEY')
        }
    }