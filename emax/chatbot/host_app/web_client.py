from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# 호스트 API의 URL
HOST_API_URL = "http://localhost:5000/api/execute"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data.get('command')
    
    if not command:
        return jsonify({"status": "error", "message": "Command is required"}), 400

    try:
        # 호스트 API로 명령 프록시
        response = requests.post(HOST_API_URL, json={'command': command})
        response.raise_for_status()
        
        return jsonify(response.json()), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Error connecting to host API: {e}"
        }), 500

if __name__ == '__main__':
    app.run(port=8080)
