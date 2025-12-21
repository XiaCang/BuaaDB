from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import md5, generate_token, token_store
import pymysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user_name = data.get("username")
    password = data.get("password")

    if not user_name or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT user_name, password_md5 FROM users WHERE user_name = %s", (user_name,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "用户不存在"}), 404

        if md5(password) == user["password_md5"]:
            token = generate_token(user_name)
            print(f"[LOGIN] 用户 {user_name} 登录成功")
            return jsonify({"token": token, "message": "登录成功"}), 200
        else:
            return jsonify({"message": "用户名或密码错误"}), 401

    except Exception as e:
        print(f"[ERROR] 登录失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    user_name = data.get("username")
    password = data.get("password")

    if not user_name or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT user_name FROM users WHERE user_name = %s", (user_name,))
        if cursor.fetchone():
            return jsonify({"message": "用户名已存在"}), 409

        hashed_password = md5(password)
        
        cursor.execute("""
            INSERT INTO users (user_name, password_md5, create_time)
            VALUES (%s, %s, NOW())
        """, (user_name, hashed_password))
        
        conn.commit()

        print(f"[REGISTER] 用户 {user_name} 注册成功")
        return jsonify({"message": "注册成功"}), 201

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 注册失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()
    
@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization")
    if token and token in token_store:
        del token_store[token]
        return jsonify({"message": "已成功退出登录"}), 200
    return jsonify({"message": "token 无效或已过期"}), 400