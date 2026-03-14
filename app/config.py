"""Environment and app configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """App config."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
