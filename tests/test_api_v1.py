"""Unit tests for API v1 endpoints."""

import json


def test_healthcheck_returns_200(client):
    """GET /api/v1/healthcheck returns 200 and status ok."""
    resp = client.get("/api/v1/healthcheck")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {"status": "ok"}


def test_list_students_empty(client):
    """GET /api/v1/students returns 200 and empty list when no students."""
    resp = client.get("/api/v1/students")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_student_returns_201(client):
    """POST /api/v1/students creates a student and returns 201 with body."""
    resp = client.post(
        "/api/v1/students",
        data=json.dumps({"name": "Alice", "age": 20, "gender": "Female"}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Alice"
    assert data["age"] == 20
    assert data["gender"] == "Female"
    assert "id" in data
    assert "created_at" in data


def test_list_students_after_create(client):
    """GET /api/v1/students returns created students."""
    client.post(
        "/api/v1/students",
        data=json.dumps({"name": "Bob", "age": 22, "gender": "Male"}),
        content_type="application/json",
    )
    resp = client.get("/api/v1/students")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Bob"
    assert data[0]["age"] == 22
    assert data[0]["gender"] == "Male"


def test_get_student_returns_200(client):
    """GET /api/v1/students/<id> returns 200 and student when exists."""
    create = client.post(
        "/api/v1/students",
        data=json.dumps({"name": "Carol", "age": 19, "gender": "Female"}),
        content_type="application/json",
    )
    sid = create.get_json()["id"]
    resp = client.get(f"/api/v1/students/{sid}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == sid
    assert data["name"] == "Carol"
    assert data["age"] == 19
    assert data["gender"] == "Female"


def test_get_student_returns_404_when_missing(client):
    """GET /api/v1/students/<id> returns 404 when student does not exist."""
    resp = client.get("/api/v1/students/99999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_update_student_returns_200(client):
    """PUT /api/v1/students/<id> updates and returns 200 with updated body."""
    create = client.post(
        "/api/v1/students",
        data=json.dumps({"name": "Dave", "age": 21, "gender": "Male"}),
        content_type="application/json",
    )
    sid = create.get_json()["id"]
    resp = client.put(
        f"/api/v1/students/{sid}",
        data=json.dumps({"name": "David", "age": 22, "gender": "Male"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == sid
    assert data["name"] == "David"
    assert data["age"] == 22
    assert data["gender"] == "Male"


def test_update_student_returns_404_when_missing(client):
    """PUT /api/v1/students/<id> returns 404 when student does not exist."""
    resp = client.put(
        "/api/v1/students/99999",
        data=json.dumps({"name": "X", "age": 1, "gender": "Male"}),
        content_type="application/json",
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_delete_student_returns_204(client):
    """DELETE /api/v1/students/<id> returns 204 and removes student."""
    create = client.post(
        "/api/v1/students",
        data=json.dumps({"name": "Eve", "age": 18, "gender": "Female"}),
        content_type="application/json",
    )
    sid = create.get_json()["id"]
    resp = client.delete(f"/api/v1/students/{sid}")
    assert resp.status_code == 204
    assert resp.data in (b"", b"\n")
    get_resp = client.get(f"/api/v1/students/{sid}")
    assert get_resp.status_code == 404


def test_delete_student_returns_404_when_missing(client):
    """DELETE /api/v1/students/<id> returns 404 when student does not exist."""
    resp = client.delete("/api/v1/students/99999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_create_student_with_defaults(client):
    """POST /api/v1/students with missing fields uses defaults."""
    resp = client.post(
        "/api/v1/students",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == ""
    assert data["age"] == 0
    assert data["gender"] == ""
    assert "id" in data
