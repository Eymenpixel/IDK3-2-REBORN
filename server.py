import os, subprocess, json, urllib.request
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Senin Firebase URL'in
DB_URL = "https://idk3-2-reborn-default-rtdb.firebaseio.com/users.json"

@app.route('/')
def index():
    # index.html dosyasını ana sayfada gösterir
    return send_from_directory('.', 'index.html')

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    mode = data.get('mode')
    
    # Firebase'den kullanıcıları çek (urllib kullanarak)
    try:
        with urllib.request.urlopen(DB_URL) as response:
            users = json.loads(response.read().decode())
    except:
        users = {}

    if mode == 'register':
        if username in users: 
            return jsonify({'status': 'error', 'msg': 'Kullanıcı zaten var!'})
        users[username] = {'password': password}
        # Firebase'e yaz (urllib kullanarak)
        req = urllib.request.Request(DB_URL, data=json.dumps(users).encode(), method='PUT')
        urllib.request.urlopen(req)
        os.makedirs(f'./homes/{username}', exist_ok=True)
        return jsonify({'status': 'success', 'msg': 'Kayıt başarılı!'})

    elif mode == 'login':
        if username in users and str(users[username]['password']) == str(password):
            os.makedirs(f'./homes/{username}', exist_ok=True)
            return jsonify({'status': 'success', 'username': username})
        return jsonify({'status': 'error', 'msg': 'Hatalı kullanıcı adı veya şifre!'})

@app.route('/exec', methods=['POST'])
def execute():
    data = request.json
    user = data.get('username')
    command = data.get('command')
    user_home = f"./homes/{user}"
    
    os.makedirs(user_home, exist_ok=True)
    try:
        # Komutu Ubuntu terminalinde çalıştır
        output = subprocess.check_output(command, shell=True, cwd=user_home, stderr=subprocess.STDOUT, timeout=10)
        return jsonify({'output': output.decode('utf-8')})
    except Exception as e:
        res = getattr(e, 'output', b'').decode('utf-8') if hasattr(e, 'output') else str(e)
        return jsonify({'output': res})

if __name__ == '__main__':
    # Render'ın verdiği portu kullan
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
