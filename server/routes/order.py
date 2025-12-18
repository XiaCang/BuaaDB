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
    # 1. 身份验证
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 2. 检查商品是否存在，以及是否还在架上 (active)
        # 注意：这里最好加上 FOR UPDATE (悲观锁) 防止高并发下超卖，
        # 但考虑到是课程作业，普通查询也可以，只要利用 UPDATE 的返回值判断即可。
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            return jsonify({"message": "商品不存在"}), 404
        
        if product['status'] != 'active':
            return jsonify({"message": "手慢了，商品已售出或下架"}), 409 # 409 Conflict

        # 防止自己买自己的商品
        if product['owner_id'] == user_name:
             return jsonify({"message": "不能购买自己发布的商品"}), 400

        # ====== 3. 开启事务 (Transaction) ======
        # (PyMySQL 默认开启事务，只要不 commit 就不会生效)
        
        # A. 更新商品状态为 'sold'
        # 这里的 WHERE status='active' 是关键，这是乐观锁的一种实现
        update_sql = "UPDATE products SET status = 'sold' WHERE product_id = %s AND status = 'active'"
        rows_affected = cursor.execute(update_sql, (product_id,))
        
        if rows_affected == 0:
            # 如果更新行数为0，说明刚才那一瞬间被别人买走了
            conn.rollback()
            return jsonify({"message": "购买失败，商品已被他人抢先购买"}), 409

        # B. 生成订单记录
        order_id = generate_uuid()
        seller_id = product['owner_id']
        
        insert_sql = """
            INSERT INTO orders 
            (order_id, order_status, buyer_id, seller_id, product_id, created_time)
            VALUES (%s, 'completed', %s, %s, %s, NOW())
        """
        cursor.execute(insert_sql, (order_id, user_name, seller_id, product_id))

        # C. 提交事务 (原子性：要么全成功，要么全失败)
        conn.commit()
        print(f"[ORDER] 用户 {user_name} 购买了商品 {product_id}, 订单号 {order_id}")
        
        return jsonify({"message": "购买成功", "order_id": order_id}), 200

    except Exception as e:
        conn.rollback() # 发生任何报错，回滚所有操作，保证数据安全
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
        # 查询我是买家的订单，顺便关联查出商品的信息(标题、图片)，前端展示更好看
        sql = """
            SELECT o.order_id, o.order_status, o.created_time,
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