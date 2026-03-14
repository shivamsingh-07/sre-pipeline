"""API v1 routes — REST students resource."""

import logging
from flask import request, jsonify

from app.extensions import db
from app.models import Student

logger = logging.getLogger(__name__)


def register_routes(bp):
    @bp.route("/healthcheck", methods=["GET"])
    def healthcheck():
        return jsonify({"status": "ok"}), 200

    @bp.route("/students", methods=["GET"])
    def list_students():
        logger.info("GET /api/v1/students — listing students")
        try:
            students = Student.query.all()
            logger.info("GET /api/v1/students — returned %d students", len(students))
            return jsonify([s.to_dict() for s in students])
        except Exception as e:
            logger.exception("GET /api/v1/students — failed: %s", e)
            return jsonify({"error": str(e)}), 500

    @bp.route("/students", methods=["POST"])
    def create_student():
        data = request.get_json(force=True, silent=True) or {}
        logger.info("POST /api/v1/students — create student name=%r", data.get("name"))
        try:
            name = data.get("name", "")
            age = data.get("age", 0)
            gender = data.get("gender", "")
            try:
                age = int(age)
            except (TypeError, ValueError):
                age = 0
            student = Student(name=name, age=age, gender=gender)
            db.session.add(student)
            db.session.commit()
            logger.info("POST /api/v1/students — created student id=%s", student.id)
            return jsonify(student.to_dict()), 201
        except Exception as e:
            logger.exception("POST /api/v1/students — failed: %s", e)
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @bp.route("/students/<int:id>", methods=["GET"])
    def get_student(id: int):
        logger.debug("GET /api/v1/students/%s", id)
        student = db.session.get(Student, id)
        if student is None:
            logger.warning("GET /api/v1/students/%s — not found", id)
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student.to_dict())

    @bp.route("/students/<int:id>", methods=["PUT", "PATCH"])
    def update_student(id: int):
        logger.info("PUT /api/v1/students/%s — update", id)
        student = db.session.get(Student, id)
        if student is None:
            logger.warning("PUT /api/v1/students/%s — not found", id)
            return jsonify({"error": "Student not found"}), 404
        try:
            data = request.get_json(force=True, silent=True) or {}
            student.name = data.get("name", student.name)
            try:
                student.age = int(data.get("age", student.age))
            except (TypeError, ValueError):
                student.age = 0
            student.gender = data.get("gender", student.gender)
            db.session.commit()
            logger.info("PUT /api/v1/students/%s — updated", id)
            return jsonify(student.to_dict())
        except Exception as e:
            logger.exception("PUT /api/v1/students/%s — failed: %s", id, e)
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @bp.route("/students/<int:id>", methods=["DELETE"])
    def delete_student(id: int):
        logger.info("DELETE /api/v1/students/%s", id)
        student = db.session.get(Student, id)
        if student is None:
            logger.warning("DELETE /api/v1/students/%s — not found", id)
            return jsonify({"error": "Student not found"}), 404
        try:
            db.session.delete(student)
            db.session.commit()
            logger.info("DELETE /api/v1/students/%s — deleted", id)
            return "", 204
        except Exception as e:
            logger.exception("DELETE /api/v1/students/%s — failed: %s", id, e)
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
