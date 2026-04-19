"""Environment and app configuration."""

import os

from dotenv import load_dotenv

load_dotenv()

user = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
hostname = os.environ.get("DB_HOSTNAME")
database = os.environ.get("DB_NAME")


class Config:
    """App config."""

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{hostname}/{database}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
