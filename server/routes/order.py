from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import verify_token
import pymysql
import uuid

order_bp = Blueprint('order', __name__)

# 辅助函数
def generate_uuid():
    return uuid.uuid4().hex

# ====== 1. 购买商品 (核心事务功能) ======
@order_bp.route("/buy_product/<product_id>", methods=["POST"])
def buy_product(product_id):
    # 补全 Token 验证代码
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 1. 检查商品状态
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            return jsonify({"message": "商品不存在"}), 404
        
        if product['status'] != 'active':
            return jsonify({"message": "手慢了，商品已售出"}), 409

        # 防止买自己的商品
        if product['owner_id'] == user_name:
             return jsonify({"message": "不能购买自己发布的商品"}), 400

        # 2. 插入订单
        order_id = generate_uuid()
        seller_id = product['owner_id']
        
        insert_sql = """
            INSERT INTO orders 
            (order_id, order_status, buyer_id, seller_id, product_id, created_time)
            VALUES (%s, 'completed', %s, %s, %s, NOW())
        """
        cursor.execute(insert_sql, (order_id, user_name, seller_id, product_id))

        # 提交事务 (触发器会自动更新 products 表状态)
        conn.commit()
        
        print(f"[ORDER] 订单 {order_id} 创建成功，触发器已自动更新商品状态")
        return jsonify({"message": "购买成功", "order_id": order_id}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 购买失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 2. 获取我的订单 ======
@order_bp.route("/get_orders", methods=["GET"])
def get_orders():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # ✅ 修改点：在 SELECT 中增加了 o.product_id
        sql = """
            SELECT o.order_id, o.order_status, o.created_time,
                   o.product_id, 
                   p.product_title, p.img_url, p.price,
                   o.seller_id
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.buyer_id = %s
            ORDER BY o.created_time DESC
        """
        cursor.execute(sql, (user_name,))
        orders = cursor.fetchall()

        # 格式化时间
        for order in orders:
            order['created_time'] = str(order['created_time'])

        return jsonify({"orders": orders, "message": "获取成功"}), 200

    except Exception as e:
        print(f"[ERROR] 获取订单失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()