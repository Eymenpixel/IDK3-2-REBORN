import os, subprocess, requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Senin Firebase Linkin
DB_URL = "https://idk3-2-reborn-default-rtdb.firebaseio.com/users.json"

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    mode = data.get('mode') # 'login', 'register', 'clone'
    target_user = data.get('target_user') # Klonlama için

    r = requests.get(DB_URL)
    users = r.json() if r.json() else {}

    if mode == 'register':
        if username in users: return jsonify({'status': 'error', 'msg': 'Kullanıcı mevcut!'})
        users[username] = {'password': password}
        requests.put(DB_URL, json=users)
        os.makedirs(f'./homes/{username}', exist_ok=True)
        return jsonify({'status': 'success', 'msg': 'Kayıt başarılı!'})

    elif mode == 'login':
        if username in users and users[username]['password'] == password:
            os.makedirs(f'./homes/{username}', exist_ok=True)
            return jsonify({'status': 'success', 'username': username})
        return jsonify({'status': 'error', 'msg': 'Hatalı şifre veya kullanıcı!'})

    elif mode == 'clone':
        if target_user in users and users[target_user]['password'] == password:
            os.makedirs(f'./homes/{username}', exist_ok=True)
            # Linux komutuyla klasörü kopyala
            subprocess.run(f"cp -r ./homes/{target_user}/* ./homes/{username}/", shell=True)
            return jsonify({'status': 'success', 'msg': f'{target_user} verileri kopyalandı!'})
        return jsonify({'status': 'error', 'msg': 'Hedef kullanıcı şifresi hatalı!'})

@app.route('/exec', methods=['POST'])
def execute():
    data = request.json
    user = data.get('username')
    user_home = f"./homes/{user}"
    os.makedirs(user_home, exist_ok=True)
    try:
        # Komutu o kullanıcının klasöründe çalıştır
        output = subprocess.check_output(data['command'], shell=True, cwd=user_home, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({'output': output.decode('utf-8')})
    except Exception as e:
        return jsonify({'output': str(e)})

if __name__ == '__main__':
    os.makedirs('./homes', exist_ok=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
