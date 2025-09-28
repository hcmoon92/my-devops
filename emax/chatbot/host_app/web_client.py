import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# 호스트 API의 URL
# 클라이언트의 /api/send_command 요청을 이 API로 전달합니다.
HOST_API_URL = "http://localhost:5000/api/execute"

# 파일을 임시로 저장할 디렉토리 (보안 및 관리를 위해 필수)
UPLOAD_FOLDER = 'temp_uploads'
# 임시 폴더가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    # 'index.html' 파일은 클라이언트 CLI HTML 코드를 담고 있다고 가정합니다.
    return render_template('index.html')

@app.route('/api/send_command', methods=['POST'])
def send_command():
    # 🚩 변경: 클라이언트가 FormData로 보내므로 request.form과 request.files를 사용합니다.
    
    # 1. 텍스트 명령 추출 (FormData의 'command' 필드)
    command = request.form.get('command')
    
    # 2. 파일 추출 (FormData의 'image' 필드)
    image_file = request.files.get('image')
    
    if not command and not image_file:
        return jsonify({"status": "error", "message": "Command or image is required"}), 400

    # 3. 호스트 API로 전달할 데이터 준비
    # 텍스트 명령은 FormData의 일부로 전달합니다.
    proxy_data = {'command': command} if command else {}
    
    # 4. 파일 처리 및 전송을 위한 multipart/form-data 구성
    # requests 라이브러리를 사용하여 파일을 쉽게 전송하기 위해 'files' 파라미터를 사용합니다.
    proxy_files = {}
    if image_file:
        # 파일 이름을 'image'로 지정하여 호스트 API가 request.files.get('image')로 접근할 수 있게 합니다.
        proxy_files['image'] = (image_file.filename, image_file.stream, image_file.mimetype)

    try:
        # 호스트 API로 명령 및 파일 프록시
        # data=proxy_data는 텍스트 필드를, files=proxy_files는 파일 필드를 multipart/form-data로 자동 인코딩하여 전송합니다.
        response = requests.post(
            HOST_API_URL, 
            data=proxy_data, 
            files=proxy_files,
            # 타임아웃을 설정하여 무한 대기를 방지합니다.
            timeout=30 
        )
        response.raise_for_status() # HTTP 오류 코드가 발생하면 예외 발생

        # 호스트 API의 응답을 클라이언트에게 그대로 전달
        return jsonify(response.json()), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "status": "error",
            "message": "Host API request timed out after 30 seconds."
        }), 504
    except requests.exceptions.RequestException as e:
        # 호스트 API 연결 실패, DNS 오류, SSL 오류 등
        error_message = f"Error connecting to host API: {e}"
        
        # 호스트 API가 JSON이 아닌 응답을 반환한 경우 처리
        try:
            error_details = response.text
        except Exception:
            error_details = str(e)

        return jsonify({
            "status": "error",
            "message": error_message,
            "details": error_details
        }), 500

if __name__ == '__main__':
    # Flask 앱을 8080 포트에서 실행합니다.
    # 클라이언트 HTML 코드가 이 서버에서 제공됩니다.
    app.run(host='0.0.0.0', port=8080, debug=True)
