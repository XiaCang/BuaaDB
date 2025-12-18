from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import verify_token
import pymysql
import uuid # 👈 新增：用于生成 varchar(32) 的 ID

product_bp = Blueprint('product', __name__)

# 辅助函数：生成唯一ID
def generate_uuid():
    return uuid.uuid4().hex # 生成32位不带横线的字符串

# ====== 1. 获取所有商品列表 ======
@product_bp.route("/get_products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 修改 SQL 匹配你的表结构
        # owner_id 关联 users.user_name (假设 user_name 是主键)
        sql = """
            SELECT p.*, u.nickname as seller_name, u.avatar_url as seller_avatar
            FROM products p
            LEFT JOIN users u ON p.owner_id = u.user_name
            WHERE p.status = 'active'
            ORDER BY p.create_time DESC
        """
        cursor.execute(sql)
        products = cursor.fetchall()
        
        # 格式化数据以符合前端 api.txt 的要求
        result_list = []
        for p in products:
            result_list.append({
                "id": p["product_id"],          # 前端叫 id，数据库叫 product_id
                "name": p["product_title"],     # 前端叫 name，数据库叫 product_title
                "price": float(p["price"]),     # Decimal 转 float
                "image_url": p["img_url"],      # 字段名转换
                "description": p["description"],
                "seller_id": p["owner_id"],
                "seller_name": p["seller_name"],   # 额外补充的
                "seller_avatar": p["seller_avatar"], # 额外补充的
                "created_at": str(p["create_time"]),
                "status": p["status"]
            })
                
        return jsonify({"products": result_list, "message": "获取成功"}), 200

    except Exception as e:
        print(f"[ERROR] 获取商品列表失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 2. 获取单个商品详情 ======
@product_bp.route("/product/<product_id>", methods=["GET"]) # 注意这里去掉了 int: 类型限制
def get_product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        sql = """
            SELECT p.*, u.nickname as seller_name, u.avatar_url as seller_avatar
            FROM products p
            LEFT JOIN users u ON p.owner_id = u.user_name
            WHERE p.product_id = %s
        """
        cursor.execute(sql, (product_id,))
        p = cursor.fetchone()
        
        if not p:
            return jsonify({"message": "商品不存在"}), 404

        # 格式化返回
        data = {
            "id": p["product_id"],
            "name": p["product_title"],
            "price": float(p["price"]),
            "image_url": p["img_url"],
            "description": p["description"],
            "seller_id": p["owner_id"],
            "created_at": str(p["create_time"]),
            "status": p["status"]
        }

        return jsonify(data), 200

    except Exception as e:
        print(f"[ERROR] 获取商品详情失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# ====== 3. 发布商品 (Create) ======
@product_bp.route("/create_product", methods=["POST"])
def create_product():
    # 1. 验证 Token
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    # 2. 获取参数
    data = request.json
    title = data.get("name") # 前端传的是 name
    price = data.get("price")
    img_url = data.get("image_url")
    desc = data.get("description")
    
    if not title or not price:
        return jsonify({"message": "标题和价格必填"}), 400

    # 3. 生成 ID 和 插入数据库
    new_id = generate_uuid() # 生成随机字符串ID
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            INSERT INTO products 
            (product_id, product_title, price, img_url, description, owner_id, status, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, 'active', NOW(), NOW())
        """
        cursor.execute(sql, (new_id, title, price, img_url, desc, user_name))
        conn.commit()
        
        return jsonify({"message": "商品发布成功", "product_id": new_id}), 201

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 发布商品失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()