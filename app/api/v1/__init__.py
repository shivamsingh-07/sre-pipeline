"""API v1."""

from flask import Blueprint
from app.api.v1.routes import register_routes

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")
register_routes(api_v1)
