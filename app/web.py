"""Web UI routes (HTML pages). Calls API v1 endpoints via HTTP."""

import requests
from flask import Blueprint, render_template, request, redirect

web_bp = Blueprint("web", __name__)

API_PREFIX = "/api/v1"


def _api_url(path: str) -> str:
    """Build full URL for API call (same host as current request)."""
    base = request.host_url.rstrip("/")
    return f"{base}{API_PREFIX}{path}"


@web_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            name = request.form.get("name", "")
            age = request.form.get("age", "")
            gender = request.form.get("gender", "")
            resp = requests.post(
                _api_url("/students"),
                json={"name": name, "age": age, "gender": gender},
                timeout=10,
            )
            resp.raise_for_status()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}", 500
    try:
        resp = requests.get(_api_url("/students"), timeout=10)
        resp.raise_for_status()
        students = resp.json()
        return render_template("index.html", students=students)
    except Exception as e:
        return f"Error: {e}", 500


@web_bp.route("/delete/<int:id>")
def delete(id: int):
    try:
        resp = requests.delete(_api_url(f"/students/{id}"), timeout=10)
        resp.raise_for_status()
        return redirect("/")
    except Exception as e:
        return f"Error: {e}", 500


@web_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id: int):
    if request.method == "POST":
        try:
            name = request.form.get("name", "")
            age = request.form.get("age", "")
            gender = request.form.get("gender", "")
            resp = requests.put(
                _api_url(f"/students/{id}"),
                json={"name": name, "age": age, "gender": gender},
                timeout=10,
            )
            resp.raise_for_status()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}", 500
    try:
        resp = requests.get(_api_url(f"/students/{id}"), timeout=10)
        resp.raise_for_status()
        student = resp.json()
        return render_template("edit.html", student=student)
    except Exception as e:
        return f"Error: {e}", 500
