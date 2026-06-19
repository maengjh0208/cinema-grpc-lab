from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from app import db
from app.models import User
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select

auth_bp = Blueprint("auth", __name__)

# TODO: 레이어 별로 로직을 분기하는 작업은 나중에.


# POST /auth/register - 회원 가입
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "body: email, password 필수"}), 400

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
        # TODO: commit, rollback 처리 방법 고민
        db.session.rollback()
        return jsonify({"message": "서버 오류"}), 500


# POST /auth/login - 로그인
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "body: email, password 필수"}), 400

    # 이메일로 유저 조회 - 없으면 401 에러
    query = select(User).where(User.email == email)
    user = db.session.execute(query).scalar_one_or_none()
    if not user:
        return jsonify({"message": "존재하지 않는 email"}), 401

    # 비밀번호 검증 - 틀리면 401
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"message": "password 일치하지 않음"}), 401

    # JWT 토큰 발급 후 반환
    jwt_token = jwt.encode(
        payload={"user_id": user.id, "exp": datetime.now(tz=timezone.utc) + timedelta(hours=24)},
        key=current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({"access_token": jwt_token}), 200
