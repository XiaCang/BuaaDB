from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import pymysql
import time
import secrets  # 用于生成安全随机 token

app = Flask(__name__)
CORS(app)



# 数据库配置
DB_CONFIG = {
    'host': '124.70.86.207',
    'port': 3306,
    'user': 'u23371131',
    'password': 'Aa085277',
    'database': 'h_db23371131',
    'charset': 'utf8mb4'
}

# ====== 新增：使用 Map 存储 token ======
# 结构: { token: { "user_name": str, "expire": timestamp } }
token_store = {}

# token 默认有效期：24 小时（秒）
TOKEN_EXPIRE_SECONDS = 24 * 3600

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def md5(text: str):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def generate_token(user_name: str) -> str:
    """生成随机 token 并存入 Map"""
    token = secrets.token_urlsafe(32)  # 生成 32 字节安全随机 token
    expire_time = time.time() + TOKEN_EXPIRE_SECONDS
    token_store[token] = {
        "user_name": user_name,
        "expire": expire_time
    }
    return token

def verify_token(token: str) -> str | None:
    """从 Map 中验证 token 是否有效，返回 user_name 或 None"""
    if token not in token_store:
        return None

    data = token_store[token]
    # 检查是否过期
    if time.time() > data["expire"]:
        del token_store[token]  # 清理过期 token
        return None

    return data["user_name"]

def clean_expired_tokens():
    """（可选）手动清理过期 token，防止内存泄漏"""
    now = time.time()
    expired_tokens = [t for t, v in token_store.items() if now > v["expire"]]
    for t in expired_tokens:
        del token_store[t]

# ====== 路由 ======

@app.route("/api/register", methods=["POST"])
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


@app.route("/api/login", methods=["POST"])
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
            token = generate_token(user_name)  # ✅ 存入 Map
            print(f"[LOGIN] 用户 {user_name} 登录成功，token 已存储")
            return jsonify({"token": token, "message": "登录成功"}), 200
        else:
            return jsonify({"message": "用户名或密码错误"}), 401

    except Exception as e:
        print(f"[ERROR] 登录失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/user", methods=["GET"])
def get_user():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "缺少token"}), 401

    user_name = verify_token(token)  # ✅ 从 Map 查 token
    if not user_name:
        return jsonify({"message": "无效或过期的token"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT user_name, nickname, avatar_url, phone, intro FROM users WHERE user_name = %s", (user_name,))
        profile = cursor.fetchone()
        if not profile:
            return jsonify({"message": "用户信息不存在"}), 404

        return jsonify({
            "username": profile["user_name"],
            "nickname": profile["nickname"],
            "avatar_url": profile["avatar_url"],
            "phone": profile["phone"],
            "intro": profile["intro"],
            "token": token  # 可选：回传 token
        }), 200

    except Exception as e:
        print(f"[ERROR] 获取用户信息失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()


# ====== （可选）新增注销接口 ======
@app.route("/api/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization")
    if token and token in token_store:
        del token_store[token]
        return jsonify({"message": "已成功退出登录"}), 200
    return jsonify({"message": "token 无效或已过期"}), 400


# 启动前测试数据库
if __name__ == "__main__":
    try:
        test_conn = get_db_connection()
        with test_conn.cursor() as cur:
            cur.execute("SELECT DATABASE();")
            print("✅ 数据库连接成功，当前库:", cur.fetchone())
        test_conn.close()
    except Exception as e:
        print("❌ 数据库连接失败:", e)

    print("ℹ️  使用 Map 存储 token，当前 token_store 容量:", len(token_store))
    app.run(port=5000, debug=True)