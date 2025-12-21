from flask import Blueprint, request, jsonify
import os
import uuid

file_bp = Blueprint('file', __name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "未检测到文件"}), 400
    
    file = request.files['file']
    file_type = request.form.get('type', 'common') 

    if file.filename == '':
        return jsonify({"message": "未选择文件"}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        file_url = f"{request.host_url}static/uploads/{filename}"

        return jsonify({
            "url": file_url, 
            "message": "上传成功"
        }), 201

    return jsonify({"message": "不支持的文件格式 (仅支持 png, jpg, jpeg, gif)"}), 400