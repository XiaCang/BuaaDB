from flask import Blueprint, request, jsonify
from db import get_db_connection
from utils import verify_token
import pymysql
import uuid

product_bp = Blueprint('product', __name__)

def generate_uuid():
    return uuid.uuid4().hex

# 获取所有商品分类
@product_bp.route("/get_categories", methods=["GET"])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql = "SELECT category_id, category_name FROM categories"
        cursor.execute(sql)
        categories = cursor.fetchall()
        return jsonify({"categories": categories, "message": "获取成功"}), 200
    except Exception as e:
        print(f"[ERROR] 获取分类失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# 1.获取商品列表
@product_bp.route("/get_products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        sql = """
            SELECT p.*, u.nickname as seller_name, u.avatar_url as seller_avatar
            FROM products p
            LEFT JOIN users u ON p.owner_id = u.user_name
            ORDER BY p.create_time DESC
        """
        cursor.execute(sql)
        products = cursor.fetchall()
        
        result_list = []
        for p in products:
            result_list.append({
                "id": p["product_id"],
                "name": p["product_title"],
                "price": float(p["price"]),
                "image_url": p["img_url"],
                "description": p["description"],
                "category_id": p.get("category_id"), 
                "seller_id": p["owner_id"],
                "seller_name": p["seller_name"],
                "seller_avatar": p["seller_avatar"],
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

# 2. 获取商品详情
@product_bp.route("/product/<product_id>", methods=["GET"])
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

        data = {
            "id": p["product_id"],
            "name": p["product_title"],
            "price": float(p["price"]),
            "image_url": p["img_url"],
            "description": p["description"],
            "category_id": p.get("category_id"), 
            "seller_id": p["owner_id"],
            "seller_name": p["seller_name"], 
            "seller_avatar": p["seller_avatar"],
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

# 3. 发布商品
@product_bp.route("/create_product", methods=["POST"])
def create_product():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    title = data.get("name")
    price = data.get("price")
    img_url = data.get("image_url")
    desc = data.get("description")
    category_id = data.get("category_id") 
    
    if not title or not price:
        return jsonify({"message": "标题和价格必填"}), 400

    new_id = generate_uuid()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            INSERT INTO products 
            (product_id, product_title, price, img_url, description, category_id, owner_id, status, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', NOW(), NOW())
        """
        cursor.execute(sql, (new_id, title, price, img_url, desc, category_id, user_name))
        conn.commit()
        
        return jsonify({"message": "商品发布成功", "product_id": new_id}), 201

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 发布商品失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# 4. 修改商品
@product_bp.route("/modify_product", methods=["POST"])
def modify_product():
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    data = request.json
    product_id = data.get("id")
    title = data.get("name")
    price = data.get("price")
    img_url = data.get("image_url")
    desc = data.get("description")
    category_id = data.get("category_id") 

    if not product_id:
        return jsonify({"message": "缺少商品ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
            UPDATE products 
            SET product_title = %s, 
                price = %s, 
                img_url = %s, 
                description = %s, 
                category_id = %s,
                update_time = NOW()
            WHERE product_id = %s AND owner_id = %s
        """
        affected_rows = cursor.execute(sql, (title, price, img_url, desc, category_id, product_id, user_name))
        conn.commit()

        if affected_rows == 0:
            return jsonify({"message": "修改失败：商品不存在或您无权修改"}), 403

        return jsonify({"message": "商品修改成功"}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 修改商品失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# 5. 删除商品
@product_bp.route("/delete_product/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    token = request.headers.get("Authorization")
    user_name = verify_token(token)
    if not user_name:
        return jsonify({"message": "未登录"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
            UPDATE products 
            SET status = 'deleted', update_time = NOW()
            WHERE product_id = %s AND owner_id = %s
        """
        affected_rows = cursor.execute(sql, (product_id, user_name))
        conn.commit()

        if affected_rows == 0:
            return jsonify({"message": "删除失败：商品不存在或您无权删除"}), 403

        return jsonify({"message": "商品已删除"}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 删除商品失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()

# 6. 搜索商品
@product_bp.route("/search_products", methods=["GET"])
def search_products():
    keyword = request.args.get("keyword", "").strip()

    if not keyword:
        return jsonify({"message": "请输入搜索关键词"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        sql = """
            SELECT p.*, u.nickname as seller_name, u.avatar_url as seller_avatar
            FROM products p
            LEFT JOIN users u ON p.owner_id = u.user_name
            WHERE p.status = 'active' 
            AND (p.product_title LIKE %s OR p.description LIKE %s)
            ORDER BY p.create_time DESC
        """
        search_pattern = f"%{keyword}%"
        cursor.execute(sql, (search_pattern, search_pattern))
        products = cursor.fetchall()

        result_list = []
        for p in products:
            result_list.append({
                "id": p["product_id"],
                "name": p["product_title"],
                "price": float(p["price"]),
                "image_url": p["img_url"],
                "description": p["description"],
                "category_id": p.get("category_id"), 
                "seller_id": p["owner_id"],
                "seller_name": p["seller_name"],
                "seller_avatar": p["seller_avatar"],
                "created_at": str(p["create_time"]),
                "status": p["status"]
            })

        return jsonify({
            "products": result_list, 
            "count": len(result_list),
            "message": "搜索完成"
        }), 200

    except Exception as e:
        print(f"[ERROR] 搜索失败: {e}")
        return jsonify({"message": "服务器内部错误"}), 500
    finally:
        cursor.close()
        conn.close()