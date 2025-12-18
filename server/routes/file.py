from flask import Blueprint, request, jsonify
import os
import uuid

file_bp = Blueprint('file', __name__)

# ====== 配置存储路径 ======
# 自动获取当前代码所在目录的上一级 (server目录)，然后指向 static/uploads
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

# 允许上传的文件后缀
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route("/upload", methods=["POST"])
def upload_file():
    # 1. 检查请求中是否有文件部分
    if 'file' not in request.files:
        return jsonify({"message": "未检测到文件"}), 400
    
    file = request.files['file']
    file_type = request.form.get('type', 'common') # 获取 'avatar' 或 'product'，默认 'common'

    if file.filename == '':
        return jsonify({"message": "未选择文件"}), 400

    if file and allowed_file(file.filename):
        # 2. 生成安全的文件名 (使用 UUID 防止文件名冲突)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 3. 保存文件到本地
        # 建议按类型分文件夹存储，这里为了最简单，暂时全存在 uploads 下
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        # 4. 生成可访问的 URL
        # request.host_url 会自动获取当前服务器地址 (如 http://127.0.0.1:5000/)
        # 最终 URL 类似: http://127.0.0.1:5000/static/uploads/abcd...jpg
        file_url = f"{request.host_url}static/uploads/{filename}"

        return jsonify({
            "url": file_url, 
            "message": "上传成功"
        }), 201

    return jsonify({"message": "不支持的文件格式 (仅支持 png, jpg, jpeg, gif)"}), 400