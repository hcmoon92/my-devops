import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# A list of allowed commands to prevent arbitrary code execution
ALLOWED_COMMANDS = [
    "run_my_script",
    "get_status",
    "stop_process"
]

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command')
    
    # 1. Input Validation: Check if the command is in the allowed list
    if command not in ALLOWED_COMMANDS:
        return jsonify({"status": "error", "message": "Command not allowed."}), 403

    # 2. Command Execution based on the received command
    if command == "run_my_script":
        try:
            # Example: Run a Python script named 'my_script.py' on the host
            result = subprocess.run(
                ["python", "my_script.py"],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({
                "status": "success",
                "message": f"Command '{command}' executed.",
                "output": result.stdout.strip()
            }), 200
        except subprocess.CalledProcessError as e:
            return jsonify({
                "status": "error",
                "message": f"Execution failed: {e.stderr.strip()}",
                "output": e.stdout.strip()
            }), 500
            
    elif command == "get_status":
        # Example: Another command to get system status
        return jsonify({
            "status": "success",
            "message": "System is running normally."
        }), 200

    # You can add more 'elif' blocks for other commands

    return jsonify({"status": "error", "message": "Unknown command."}), 400

if __name__ == '__main__':
    # Use a specific port, e.g., 5000
    app.run(host='0.0.0.0', port=5000)
