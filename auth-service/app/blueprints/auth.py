import bcrypt
from app import db
from app.models import User
from flask import Blueprint, jsonify, request
from sqlalchemy import select

auth_bp = Blueprint("auth", __name__)


# POST /register - 회원 가입
# 레이어 별로 로직을 분기하는 작업은 나중에.
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "body: email, password 필요"}), 400

        query = select(User).where(User.email == email)
        existing_user = db.session.execute(query).scalar_one_or_none()
        if existing_user:
            return jsonify({"message": "이미 존재하는 이메일"}), 409

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        password_hash = hashed.decode("utf-8")

        user = User(email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "ok"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"message": "서버 오류"}), 500
