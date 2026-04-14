import os
import subprocess
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Firebase Linkin (Sonunda /users.json olduğuna emin ol)
DB_URL = "https://idk3-2-reborn-default-rtdb.firebaseio.com/users.json"

# --- ANA SAYFAYI AÇAN KOD (NOT FOUND HATASINI ÇÖZER) ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    mode = data.get('mode') 
    target_user = data.get('target_user')

    try:
        r = requests.get(DB_URL)
        users = r.json() if r.json() else {}
    except:
        users = {}

    if mode == 'register':
        if username in users: return jsonify({'status': 'error', 'msg': 'Kullanıcı mevcut!'})
        users[username] = {'password': password}
        requests.put(DB_URL, json=users)
        os.makedirs(f'./homes/{username}', exist_ok=True)
        return jsonify({'status': 'success', 'msg': 'Kayıt başarılı!'})

    elif mode == 'login':
        if username in users and str(users[username]['password']) == str(password):
            os.makedirs(f'./homes/{username}', exist_ok=True)
            return jsonify({'status': 'success', 'username': username})
        return jsonify({'status': 'error', 'msg': 'Hatalı şifre veya kullanıcı!'})

    elif mode == 'clone':
        if target_user in users and str(users[target_user]['password']) == str(password):
            os.makedirs(f'./homes/{username}', exist_ok=True)
            subprocess.run(f"cp -r ./homes/{target_user}/* ./homes/{username}/", shell=True)
            return jsonify({'status': 'success', 'msg': f'{target_user} verileri kopyalandı!'})
        return jsonify({'status': 'error', 'msg': 'Hedef kullanıcı şifresi hatalı!'})

@app.route('/exec', methods=['POST'])
def execute():
    data = request.json
    user = data.get('username')
    command = data.get('command')
    user_home = f"./homes/{user}"
    
    if not user: return jsonify({'output': 'Giriş yapmalısın!'})
    
    os.makedirs(user_home, exist_ok=True)
    try:
        output = subprocess.check_output(command, shell=True, cwd=user_home, stderr=subprocess.STDOUT, timeout=10)
        return jsonify({'output': output.decode('utf-8')})
    except subprocess.CalledProcessError as e:
        return jsonify({'output': e.output.decode('utf-8')})
    except Exception as e:
        return jsonify({'output': str(e)})

if __name__ == '__main__':
    # Render portu için ayar
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
