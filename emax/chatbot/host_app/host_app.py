import subprocess
import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename # 파일 이름 보안을 위해 사용

app = Flask(__name__)

# 파일이 임시로 저장될 디렉토리
UPLOAD_FOLDER = 'uploaded_images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 🔒 허용된 명령어 목록 (Whitelist) - 보안을 위해 매우 중요
ALLOWED_COMMANDS = {
    "hello": {"script": "script_default.py", "base_args": ["hello"]},
    "status": {"script": "script_default.py", "base_args": ["status"]},
    # 🚩 추가: 'image' 명령어를 'analyze'로 변경하고, 파일 경로를 인수로 받도록 설정
    "analyze": {"script": "script_image.py", "base_args": ["analyze"]}, 
    "make": {"script": "script_image.py", "base_args": ["make"]} # 기존 image 명령 유지 (파일 미사용 가정)
}

# 🚩 엔드포인트는 프록시 서버가 요청하는 /api/execute로 유지
@app.route('/api/execute', methods=['POST'])
def execute_command():
    # 🚩 변경: FormData로 데이터를 받으므로 request.form 사용
    full_user_input = request.form.get('command', '').strip()
    image_file = request.files.get('image') # 'image'는 클라이언트 FormData에서 설정한 필드 이름

    # 1. 명령어 및 인자 파싱
    command_parts = full_user_input.split()
    command_name = command_parts[0] if command_parts else ""
    user_args = command_parts[1:]
    
    if not command_name:
        return jsonify({"status": "error", "message": "Command is required."}), 400

    if command_name not in ALLOWED_COMMANDS:
        return jsonify({"status": "error", "message": f"'{command_name}' is not an allowed command."}), 403

    command_details = ALLOWED_COMMANDS[command_name]
    script_to_run = command_details.get("script")
    base_args = command_details.get("base_args", [])
    
    # 2. 이미지 파일 처리
    file_path = None
    file_cleanup_needed = False
    
    if image_file:
        try:
            # 2-1. 안전한 파일 이름 생성 (보안 및 충돌 방지)
            filename = secure_filename(image_file.filename)
            # UUID를 추가하여 파일 이름 충돌을 거의 확실하게 방지
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # 2-2. 파일 저장
            image_file.save(file_path)
            file_cleanup_needed = True
            
            # 사용자 인수에 저장된 파일 경로를 추가합니다. (스크립트가 사용할 수 있도록)
            user_args.append(file_path) 
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"File upload failed: {str(e)}"
            }), 500

    # 3. 최종 명령어 및 인자 조합
    # base_args (스크립트가 필요한 고정 인자) + user_args (사용자 입력 및 파일 경로)
    full_command = ["python", script_to_run] + base_args + user_args
    
    output = ""
    stderr = ""

    try:
        # 4. 실제 스크립트 실행
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=10 # 실행 시간 제한
        )
        output = result.stdout.strip()
        message = f"Command '{command_name}' executed successfully."
        status_code = 200
        response_status = "success"

    except subprocess.CalledProcessError as e:
        output = e.stdout.strip()
        stderr = e.stderr.strip()
        message = f"Execution failed. Check the script output for details."
        status_code = 500
        response_status = "error"

    except FileNotFoundError:
        message = f"Error: Python interpreter or script '{script_to_run}' not found."
        status_code = 500
        response_status = "error"
        
    except subprocess.TimeoutExpired:
        message = f"Error: Command '{command_name}' timed out."
        status_code = 500
        response_status = "error"
        
    finally:
        # 5. 파일 정리 (try/except/finally를 사용하여 에러 발생 여부와 관계없이 파일 삭제 시도)
        if file_cleanup_needed and file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # 파일 삭제 오류는 치명적이지 않으므로 로그만 남기고 계속 진행
                print(f"Cleanup warning: Failed to delete temporary file {file_path}. Error: {e}")
                
        # 6. 최종 응답 반환
        return jsonify({
            "status": response_status,
            "message": message,
            "output": output + ("\n\nStderr: " + stderr if stderr else "")
        }), status_code

if __name__ == '__main__':
    # 이 호스트 API는 5000번 포트에서 실행됩니다.
    app.run(host='0.0.0.0', port=5000, debug=True)
