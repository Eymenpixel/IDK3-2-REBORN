import os, subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({'status': 'error', 'msg': 'İsim yaz kanka!'})
    
    # Kullanıcıya özel klasör oluştur (Ubuntu evi gibi)
    user_home = f"./homes/{username}"
    os.makedirs(user_home, exist_ok=True)
    return jsonify({'status': 'success', 'username': username})

@app.route('/exec', methods=['POST'])
def execute():
    data = request.json
    user = data.get('username')
    command = data.get('command')
    user_home = f"./homes/{user}"
    
    os.makedirs(user_home, exist_ok=True)
    try:
        # Komutu o kullanıcının klasöründe çalıştır
        output = subprocess.check_output(command, shell=True, cwd=user_home, stderr=subprocess.STDOUT, timeout=10)
        return jsonify({'output': output.decode('utf-8')})
    except Exception as e:
        res = getattr(e, 'output', b'').decode('utf-8') if hasattr(e, 'output') else str(e)
        return jsonify({'output': res})

if __name__ == '__main__':
    # Termux'ta 5000 portunda çalıştır
    app.run(host='0.0.0.0', port=5000)
