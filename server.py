import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Vercel'den gelen isteklere izin verir

@app.route('/exec', methods=['POST'])
def execute():
    command = request.json.get('command')
    try:
        # Komutu gerçek Ubuntu terminalinde çalıştırır
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({'output': output.decode('utf-8')})
    except Exception as e:
        return jsonify({'output': str(e)})

if __name__ == '__main__':
    # Render'ın portuna uyum sağlar
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
