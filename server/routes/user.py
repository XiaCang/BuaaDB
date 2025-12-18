from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import verify_token
import pymysql

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
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # ✅ 修正：删除了 'id'，因为你的表中只有 user_name 作为标识
        sql = """
            SELECT user_name, nickname, avatar_url, phone, intro, create_time 
            FROM users 
            WHERE user_name = %s
        """
        cursor.execute(sql, (user_name,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "用户不存在"}), 404
        
        # 3. 处理时间格式
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
    token = request.headers.get("Authorization")
    user_name = verify_token(token) if token else None
    
    if not user_name:
        return jsonify({"message": "未授权的操作"}), 403

    data = request.json
    nickname = data.get("nickname")
    avatar_url = data.get("avatar_url")
    phone = data.get("phone")
    intro = data.get("intro")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ✅ 这里的字段名与你的数据库截图一致，无需修改
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