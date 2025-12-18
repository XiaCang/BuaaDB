from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import verify_token
import pymysql

# 1. 创建蓝图
user_bp = Blueprint('user', __name__)

# ====== 获取用户信息 ======
@user_bp.route("/user", methods=["GET"])
def get_user_info():
    # 1. 获取并验证 Token
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "未登录，缺少 token"}), 401
    
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "登录失效，请重新登录"}), 403

    # 2. 查询数据库
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor) # 使用 DictCursor 让结果变成字典

    try:
        # 注意：这里不需要查密码，保护隐私
        sql = """
            SELECT id, user_name, nickname, avatar_url, phone, intro, create_time 
            FROM users 
            WHERE user_name = %s
        """
        cursor.execute(sql, (user_name,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "用户不存在"}), 404
        
        # 3. 返回数据
        # 把 create_time 转成字符串，否则 JSON 序列化可能会报错
        if user.get('create_time'):
            user['create_time'] = str(user['create_time'])

        return jsonify(user), 200

    except Exception as e:
        print(f"[ERROR] 获取用户信息失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()


# ====== 更新用户信息 ======
@user_bp.route("/update_user", methods=["POST"])
def update_user_info():
    # 1. 验证 Token
    token = request.headers.get("Authorization")
    user_name = verify_token(token) if token else None
    
    if not user_name:
        return jsonify({"message": "未授权的操作"}), 403

    # 2. 获取前端传来的参数
    data = request.json
    nickname = data.get("nickname")
    avatar_url = data.get("avatar_url")
    phone = data.get("phone")
    intro = data.get("intro")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 3. 执行更新 SQL
        # 这种写法会一次性更新所有字段，如果前端传的是空值，也会更新为空
        # 如果希望“只更新非空字段”，逻辑会稍微复杂一点，目前这样写最简单稳妥
        sql = """
            UPDATE users 
            SET nickname = %s, avatar_url = %s, phone = %s, intro = %s 
            WHERE user_name = %s
        """
        cursor.execute(sql, (nickname, avatar_url, phone, intro, user_name))
        conn.commit()

        print(f"[UPDATE] 用户 {user_name} 更新了资料")
        return jsonify({"message": "用户信息更新成功"}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 更新失败: {e}")
        return jsonify({"message": "更新失败，服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()