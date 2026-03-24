#!/usr/bin/env python3
import os
import markdown
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

# конфигурация
PORT = 8080
HOST = '::'
API_TOKEN = "my_secret_token"
UPLOAD_FOLDER = './md_storage'
ALLOWED_EXTENSIONS = {'md'}

# укажите ваш реальный yggdrasil ipv6 адрес
YGGDRASIL_IP = "202:184a:fd9:c392:c10b:4621:62be:9003"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; background: #f4f4f4; }
        .content { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        img { max-width: 100%; }
        code { background: #eee; padding: 2px 5px; border-radius: 3px; }
        pre { background: #2d2d2d; color: #fff; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="content">
        {{ content|safe }}
    </div>
</body>
</html>
"""

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.headers.get('X-Auth-Token') != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        import time
        safe_name = f"{int(time.time())}_{filename}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(path)
        
        link = f"http://[{YGGDRASIL_IP}]:{PORT}/view/{safe_name}"
        
        return jsonify({
            "status": "success",
            "filename": safe_name,
            "link": link
        }), 201
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/view/<filename>')
def view_file(filename):
    filename = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(path):
        return "File not found", 404
    
    with open(path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
    return render_template_string(HTML_TEMPLATE, content=html_content, title=filename)

@app.route('/')
def index():
    return "Yggdrasil MD Server is running. Use /upload endpoint."

if __name__ == '__main__':
    print(f"[*] Server starting on http://[{HOST}]:{PORT}")
    print(f"[*] Yggdrasil IP: {YGGDRASIL_IP}")
    app.run(host=HOST, port=PORT, threaded=True)