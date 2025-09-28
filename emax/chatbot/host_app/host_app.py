import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔒 허용된 명령어 목록 (Whitelist) - 보안을 위해 매우 중요
# 키는 반드시 사용자가 입력할 수 있는 '명령어'의 첫 단어여야 합니다.
ALLOWED_COMMANDS = {
    "hello": {"script": "script_default.py", "args": ["hello"]},
    "status": {"script": "script_default.py", "args": ["status"]},
    "image": {"script": "script_image.py", "args": ["make"]}
}

# 🚩 수정: 클라이언트 JavaScript 코드와 동일한 엔드포인트로 변경
@app.route('/api/send_command', methods=['POST'])
def execute_command():
    data = request.get_json()
    
    # 🚩 수정: 클라이언트로부터 받은 전체 입력 문자열을 가져옵니다.
    # 클라이언트가 { "command": "사용자 입력 내용" } 형식으로 보냅니다.
    full_user_input = data.get('command', '').strip() 
    
    # 사용자 입력에서 첫 번째 단어를 추출하여 화이트리스트 명령 이름으로 사용
    command_parts = full_user_input.split()
    if not command_parts:
        return jsonify({"status": "error", "message": "No command provided."}), 400

    command_name = command_parts[0]
    
    # 나머지 인수는 스크립트에 전달될 사용자 인수로 사용 가능
    user_args = command_parts[1:]
    
    if command_name not in ALLOWED_COMMANDS:
        return jsonify({"status": "error", "message": f"'{command_name}' is not an allowed command."}), 403

    command_details = ALLOWED_COMMANDS[command_name]
    script_to_run = command_details.get("script")
    
    # 기본 스크립트 인수에 사용자 인수를 추가합니다.
    # 예: "image make" + ["cat"] => ["python", "script_image.py", "make", "cat"]
    script_args = command_details.get("args", []) + user_args
    
    try:
        # 실제 스크립트 실행
        full_command = ["python", script_to_run] + script_args
        
        # ⚠️ 경고: 실제 운영 환경에서는 보안을 위해 'shell=False'를 유지해야 합니다.
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=5 # 명령 실행 시간 제한 추가 (선택 사항이지만 권장)
        )
        return jsonify({
            "status": "success",
            "message": f"Command '{command_name}' executed.",
            "output": result.stdout.strip()
        }), 200
    except subprocess.CalledProcessError as e:
        # 스크립트가 0이 아닌 종료 코드로 실패했을 때
        return jsonify({
            "status": "error",
            "message": f"Execution failed: {e.stderr.strip()}",
            "output": e.stdout.strip()
        }), 500
    except FileNotFoundError:
        # 'python' 인터프리터나 스크립트를 찾지 못했을 때
        return jsonify({
            "status": "error",
            "message": f"Script '{script_to_run}' or Python interpreter not found."
        }), 500
    except subprocess.TimeoutExpired:
        # 명령 실행 시간이 초과되었을 때
        return jsonify({
            "status": "error",
            "message": f"Command '{command_name}' timed out after 5 seconds."
        }), 500

if __name__ == '__main__':
    # 디버깅 모드는 실제 운영 환경에서는 반드시 꺼야 합니다.
    app.run(host='0.0.0.0', port=5000, debug=True)
