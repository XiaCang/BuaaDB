from flask import Flask
from flask_cors import CORS
from db import get_db_connection

# 引入我们拆分好的蓝图
from routes.auth import auth_bp
from routes.user import user_bp
from routes.product import product_bp  
from routes.order import order_bp
from routes.interactions import interaction_bp
from routes.file import file_bp

app = Flask(__name__)
CORS(app)

# 注册蓝图
# url_prefix='/api' 意味着 auth_bp 里的所有路由都会自动加上 /api 前缀
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')
app.register_blueprint(interaction_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')

# 测试连接
if __name__ == "__main__":
    try:
        conn = get_db_connection()
        print("✅ 数据库连接成功")
        conn.close()
    except Exception as e:
        print("❌ 数据库连接失败:", e)
        
    app.run(port=5000, debug=True)