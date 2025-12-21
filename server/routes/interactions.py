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

# ====== 3. 删除评论 ======
# API: DELETE /api/delete_comment/<comment_id>
@interaction_bp.route("/delete_comment/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor) # 使用字典游标
    try:
        # 1. 检查评论是否存在 & 验证归属权
        # 只有 "评论的作者" 才能删除该评论
        cursor.execute("SELECT user_id FROM comment WHERE comment_id = %s", (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({"message": "评论不存在"}), 404

        if comment['user_id'] != user_name:
            return jsonify({"message": "操作失败：您只能删除自己的评论"}), 403

        # 2. 执行删除
        cursor.execute("DELETE FROM comment WHERE comment_id = %s", (comment_id,))
        conn.commit()

        return jsonify({"message": "评论已删除"}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除评论失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ==========================================
# B. 收藏系统 (Favorites)
# 逻辑：先检查该用户有没有“收藏夹”，没有则创建，然后往夹子里加东西
# ==========================================
# ==========================================
# B. 收藏系统 (Favorites)
# ==========================================

# ====== 1. 获取所有收藏夹 ======
@interaction_bp.route("/favorite_folders", methods=["GET"])
def get_favorite_folders():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # ✅ 修正：使用 created_time (你的截图显示带d)
        sql = "SELECT favorite_id as id, name, created_time as created_at FROM favorites WHERE user_id = %s ORDER BY created_time DESC"
        cursor.execute(sql, (user_name,))
        folders = cursor.fetchall()
        
        for f in folders:
            f['created_at'] = str(f['created_at'])

        return jsonify({"folders": folders}), 200
    except Exception as e:
        print(f"[ERROR] 获取收藏夹失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 2. 创建收藏夹 ======
@interaction_bp.route("/create_favorite_folder", methods=["POST"])
def create_favorite_folder():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    folder_name = data.get("name")
    
    if not folder_name:
        return jsonify({"message": "收藏夹名称不能为空"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        folder_id = generate_uuid()
        # ✅ 修正：使用 created_time
        sql = "INSERT INTO favorites (favorite_id, user_id, name, created_time) VALUES (%s, %s, %s, NOW())"
        cursor.execute(sql, (folder_id, user_name, folder_name))
        conn.commit()
        
        return jsonify({"message": "收藏夹创建成功", "id": folder_id}), 201
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 创建收藏夹失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 3. 修改收藏夹名称 ======
@interaction_bp.route("/modify_favorite_folder", methods=["POST"])
def modify_favorite_folder():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    folder_id = data.get("id")
    new_name = data.get("name")

    if not folder_id or not new_name:
        return jsonify({"message": "缺少参数"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "UPDATE favorites SET name = %s WHERE favorite_id = %s AND user_id = %s"
        affected = cursor.execute(sql, (new_name, folder_id, user_name))
        conn.commit()

        if affected == 0:
            return jsonify({"message": "修改失败：收藏夹不存在或无权限"}), 404
            
        return jsonify({"message": "修改成功"}), 200
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 修改收藏夹失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 4. 删除收藏夹 ======
@interaction_bp.route("/delete_favorite_folder/<folder_id>", methods=["DELETE"])
def delete_favorite_folder(folder_id):
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM favorites WHERE favorite_id = %s AND user_id = %s", (folder_id, user_name))
        if not cursor.fetchone():
            return jsonify({"message": "收藏夹不存在或无权限"}), 404

        cursor.execute("DELETE FROM favorite_item WHERE favorite_id = %s", (folder_id,))
        cursor.execute("DELETE FROM favorites WHERE favorite_id = %s", (folder_id,))
        conn.commit()
        return jsonify({"message": "收藏夹已删除"}), 200
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除收藏夹失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 5. 收藏商品到指定收藏夹 ======
@interaction_bp.route("/favorite_product", methods=["POST"])
def add_favorite_product():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    product_id = data.get("product_id")
    folder_id = data.get("folder_id")

    if not product_id or not folder_id:
        return jsonify({"message": "缺少参数"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. 检查收藏夹是否属于该用户
        cursor.execute("SELECT * FROM favorites WHERE favorite_id = %s AND user_id = %s", (folder_id, user_name))
        if not cursor.fetchone():
            return jsonify({"message": "收藏夹不存在"}), 404

        # 2. 检查是否已经收藏过（避免重复）
        cursor.execute("SELECT * FROM favorite_item WHERE favorite_id = %s AND product_id = %s", (folder_id, product_id))
        if cursor.fetchone():
            return jsonify({"message": "该商品已在此收藏夹中"}), 200 

        # 3. 插入收藏项
        # ✅ 修正：删除了 item_id，因为你的表中没有这个字段
        # ✅ 修正：使用 created_time 对应你的截图
        sql = "INSERT INTO favorite_item (favorite_id, product_id, created_time) VALUES (%s, %s, NOW())"
        cursor.execute(sql, (folder_id, product_id))
        conn.commit()

        return jsonify({"message": "收藏成功"}), 201
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 收藏商品失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 6. 获取指定收藏夹内的商品 ======
@interaction_bp.route("/get_favorites/<folder_id>", methods=["GET"])
def get_folder_items(folder_id):
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM favorites WHERE favorite_id = %s AND user_id = %s", (folder_id, user_name))
        if not cursor.fetchone():
            return jsonify({"message": "收藏夹不存在或无权限"}), 404

        # ✅ 修正：fi.created_time
        sql = """
            SELECT fi.product_id, p.product_title as name, p.price, p.img_url, fi.created_time
            FROM favorite_item fi
            JOIN products p ON fi.product_id = p.product_id
            WHERE fi.favorite_id = %s
            ORDER BY fi.created_time DESC
        """
        cursor.execute(sql, (folder_id,))
        favorites = cursor.fetchall()
        
        for f in favorites:
            f['created_time'] = str(f['created_time'])

        return jsonify({"favorites": favorites}), 200
    except Exception as e:
        print(f"[ERROR] 获取收藏详情失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 7. 从指定收藏夹删除商品 ======
@interaction_bp.route("/delete_favorite/<folder_id>/product/<product_id>", methods=["DELETE"])
def delete_favorite_item(folder_id, product_id):
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM favorites WHERE favorite_id = %s AND user_id = %s", (folder_id, user_name))
        if not cursor.fetchone():
            return jsonify({"message": "操作失败：无权操作此收藏夹"}), 403

        sql = "DELETE FROM favorite_item WHERE favorite_id = %s AND product_id = %s"
        affected = cursor.execute(sql, (folder_id, product_id))
        conn.commit()

        if affected == 0:
            return jsonify({"message": "该商品不在收藏夹中"}), 404

        return jsonify({"message": "已移除收藏"}), 200
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除收藏项失败: {e}")
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
        # 修改点 1：SQL 语句增加 OR 逻辑
        # 含义：查找 (我是接收者) 或者 (我是发送者) 的所有消息
        sql = """
            SELECT m.*, u.nickname as sender_nickname, u.avatar_url as sender_avatar
            FROM message m
            JOIN users u ON m.sender_id = u.user_name
            WHERE m.receiver_id = %s OR m.sender_id = %s
            ORDER BY m.time DESC
        """
        
        # 修改点 2：execute 时传入两个 user_name
        # 第一个 user_name 对应 SQL 里的 m.receiver_id = %s
        # 第二个 user_name 对应 SQL 里的 m.sender_id = %s
        cursor.execute(sql, (user_name, user_name))
        
        msgs = cursor.fetchall()
        
        for m in msgs:
            m['time'] = str(m['time'])
            # 💡 小建议：给前端加一个标记，方便前端判断这是“我发的”还是“别人发的”
            # 前端可以据此决定气泡是在左边（别人）还是右边（自己）
            m['is_me'] = (m['sender_id'] == user_name)
            
        return jsonify({"messages": msgs}), 200
    except Exception as e:
        print(f"[ERROR] 获取消息失败: {e}")
        return jsonify({"message": "服务器错误"}), 500
    finally:
        cursor.close()
        conn.close()