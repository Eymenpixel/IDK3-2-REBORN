import os, subprocess, requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# BURAYA KENDİ FIREBASE URL'Nİ YAZ
DB_URL = "https://SENIN-PROJE-ADIN.firebaseio.com/users.json"

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data['username']
    password = data['password']
    mode = data['mode'] # 'login', 'register', 'clone'

    # Defteri (Firebase) oku
    r = requests.get(DB_URL)
    users = r.json() if r.json() else {}

    if mode == 'register':
        if username in users: return jsonify({'status': 'error', 'msg': 'Kullanıcı zaten var!'})
        users[username] = {'password': password}
        requests.put(DB_URL, json=users) # Deftere yaz
        os.makedirs(f'./homes/{username}', exist_ok=True)
        return jsonify({'status': 'success', 'msg': 'Kaydolundu!'})

    elif mode == 'login':
        if username in users and users[username]['password'] == password:
            os.makedirs(f'./homes/{username}', exist_ok=True)
            return jsonify({'status': 'success', 'username': username})
        return jsonify({'status': 'error', 'msg': 'Hatalı giriş!'})

@app.route('/exec', methods=['POST'])
def execute():
    data = request.json
    user_home = f"./homes/{data['username']}"
    os.makedirs(user_home, exist_ok=True)
    try:
        output = subprocess.check_output(data['command'], shell=True, cwd=user_home, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({'output': output.decode('utf-8')})
    except Exception as e:
        return jsonify({'output': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
