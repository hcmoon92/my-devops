import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔒 허용된 명령어 목록 (Whitelist) - 보안을 위해 매우 중요
ALLOWED_COMMANDS = {
    "hello": {"script": "script_default.py", "args": ["hello"]},
    "status": {"script": "script_default.py", "args": ["status"]},
    "image": {"script": "script_image.py", "args": ["make"]}
}

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command_name = data.get('command')
    
    if command_name not in ALLOWED_COMMANDS:
        return jsonify({"status": "error", "message": f"'{command_name}' is not an allowed command."}), 403

    command_details = ALLOWED_COMMANDS[command_name]
    script_to_run = command_details.get("script")
    script_args = command_details.get("args", [])
    
    try:
        # 실제 스크립트 실행
        full_command = ["python", script_to_run] + script_args
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({
            "status": "success",
            "message": f"Command '{command_name}' executed.",
            "output": result.stdout.strip()
        }), 200
    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": f"Execution failed: {e.stderr.strip()}",
            "output": e.stdout.strip()
        }), 500
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": f"Script '{script_to_run}' not found."
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
