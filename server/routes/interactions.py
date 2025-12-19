from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import verify_token
import pymysql
import uuid

interaction_bp = Blueprint('interaction', __name__)

def generate_uuid():
    return uuid.uuid4().hex

# ==========================================
# A. 评论系统 (Comment)
# ==========================================

# 1. 发布评论
@interaction_bp.route("/publish_comment", methods=["POST"])
def publish_comment():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    product_id = data.get("product_id")
    content = data.get("content")
    rate = data.get("rate", 5) # 默认5分

    if not product_id or not content:
        return jsonify({"message": "参数不完整"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 生成评论ID
        comment_id = generate_uuid()
        
        # 对应你的表结构: comment_id, user_id, product_id, time, rating, content
        sql = """
            INSERT INTO comment 
            (comment_id, user_id, product_id, time, rating, content)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """
        cursor.execute(sql, (comment_id, user_name, product_id, rate, content))
        conn.commit()
        return jsonify({"message": "评论发布成功"}), 201
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 发布评论失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# 2. 获取某商品的评论
@interaction_bp.route("/get_comments/<product_id>", methods=["GET"])
def get_comments(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 关联查询用户表，为了显示评论人的头像和昵称
        sql = """
            SELECT c.*, u.nickname, u.avatar_url 
            FROM comment c
            JOIN users u ON c.user_id = u.user_name
            WHERE c.product_id = %s
            ORDER BY c.time DESC
        """
        cursor.execute(sql, (product_id,))
        comments = cursor.fetchall()
        
        # 时间转字符串
        for c in comments:
            c['time'] = str(c['time'])
            
        return jsonify({"comments": comments, "message": "获取成功"}), 200
    except Exception as e:
        print(f"[ERROR] 获取评论失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ==========================================
# B. 收藏系统 (Favorites)
# 逻辑：先检查该用户有没有“收藏夹”，没有则创建，然后往夹子里加东西
# ==========================================

@interaction_bp.route("/favorite_product/<product_id>", methods=["POST"])
def favorite_product(product_id):
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 先找这个用户的 favorite_id (收藏夹ID)
        cursor.execute("SELECT favorite_id FROM favorites WHERE user_id = %s", (user_name,))
        fav_folder = cursor.fetchone()
        
        if not fav_folder:
            # 如果是新用户，还没有收藏夹，帮他创建一个
            fav_id = generate_uuid()
            cursor.execute("INSERT INTO favorites (favorite_id, user_id, created_time) VALUES (%s, %s, NOW())", 
                           (fav_id, user_name))
        else:
            fav_id = fav_folder['favorite_id']

        # 2. 检查是否重复收藏
        cursor.execute("SELECT * FROM favorite_item WHERE favorite_id = %s AND product_id = %s", (fav_id, product_id))
        if cursor.fetchone():
            return jsonify({"message": "您已收藏过该商品"}), 200 # 也可以返回 409

        # 3. 插入收藏项
        item_id = generate_uuid()
        insert_sql = "INSERT INTO favorite_item (item_id, favorite_id, product_id) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (item_id, fav_id, product_id))
        
        conn.commit()
        return jsonify({"message": "收藏成功"}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 收藏失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

@interaction_bp.route("/get_favorites", methods=["GET"])
def get_favorites():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 三表连接：favorites -> favorite_item -> products
        sql = """
            SELECT p.* FROM favorites f
            JOIN favorite_item fi ON f.favorite_id = fi.favorite_id
            JOIN products p ON fi.product_id = p.product_id
            WHERE f.user_id = %s
        """
        cursor.execute(sql, (user_name,))
        favorites = cursor.fetchall()
        
        # 格式化数据
        result = []
        for p in favorites:
            # 这里简单处理，如果需要 seller 信息可能还需要连 users 表
            result.append({
                "product_id": p['product_id'],
                "name": p['product_title'],
                "price": float(p['price']),
                "image_url": p['img_url']
            })
            
        return jsonify({"favorites": result}), 200
    except Exception as e:
        print(f"[ERROR] 获取收藏失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 删除收藏 (Delete Favorite) ======
@interaction_bp.route("/delete_favorite/<product_id>", methods=["DELETE"])
def delete_favorite(product_id):
    # 1. 验证 Token
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 2. 先找到该用户的收藏夹 ID
        cursor.execute("SELECT favorite_id FROM favorites WHERE user_id = %s", (user_name,))
        fav_folder = cursor.fetchone()
        
        if not fav_folder:
            return jsonify({"message": "操作失败：你还没有收藏夹"}), 404
            
        fav_id = fav_folder['favorite_id']

        # 3. 执行删除操作
        # 逻辑：从我的收藏夹(fav_id)里，把指定商品(product_id)移除
        sql = "DELETE FROM favorite_item WHERE favorite_id = %s AND product_id = %s"
        affected_rows = cursor.execute(sql, (fav_id, product_id))
        conn.commit()
        
        if affected_rows == 0:
            return jsonify({"message": "删除失败：收藏夹中未找到该商品"}), 404

        return jsonify({"message": "已取消收藏"}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 取消收藏失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ==========================================
# C. 消息系统 (Messages)
# ==========================================

@interaction_bp.route("/send_msg", methods=["POST"])
def send_msg():
    token = request.headers.get("Authorization")
    sender = verify_token(token)
    if not sender:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    receiver_id = data.get("receiver_id")
    content = data.get("content")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        msg_id = generate_uuid()
        # 对应表结构: message_id, sender_id, receiver_id, time, content
        sql = """
            INSERT INTO message 
            (message_id, sender_id, receiver_id, time, content)
            VALUES (%s, %s, %s, NOW(), %s)
        """
        cursor.execute(sql, (msg_id, sender, receiver_id, content))
        conn.commit()
        return jsonify({"message": "发送成功"}), 201
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 发送消息失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

@interaction_bp.route("/get_msgs", methods=["GET"])
def get_msgs():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403
        
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 获取别人发给我的消息
        sql = """
            SELECT m.*, u.nickname as sender_nickname, u.avatar_url as sender_avatar
            FROM message m
            JOIN users u ON m.sender_id = u.user_name
            WHERE m.receiver_id = %s
            ORDER BY m.time DESC
        """
        cursor.execute(sql, (user_name,))
        msgs = cursor.fetchall()
        
        for m in msgs:
            m['time'] = str(m['time'])
            
        return jsonify({"messages": msgs}), 200
    except Exception as e:
        print(f"[ERROR] 获取消息失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()