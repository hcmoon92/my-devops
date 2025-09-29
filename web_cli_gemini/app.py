import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# .env 파일에서 환경 변수를 로드합니다. (GEMINI_API_KEY)
load_dotenv()

app = Flask(__name__)

# Gemini 클라이언트 초기화
try:
    # 환경 변수에서 API 키를 자동으로 로드합니다.
    client = genai.Client()
    # 모델 설정 (원하는 모델로 변경 가능)
    MODEL_NAME = 'gemini-2.5-flash'
except Exception as e:
    # API 키가 설정되지 않았거나 초기화에 실패한 경우
    print(f"Error initializing Gemini Client: {e}")
    client = None

@app.route('/')
def index():
    """웹 클라이언트의 기본 HTML 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/api/send_command', methods=['POST'])
def send_command():
    """클라이언트로부터 명령을 받아 Gemini API로 전송하고 결과를 반환합니다."""
    if client is None:
        return jsonify({
            "status": "error",
            "message": "Gemini API Client is not initialized. Check your GEMINI_API_KEY.",
            "output": ""
        }), 500

    try:
        data = request.get_json()
        command = data.get('command', '').strip()

        if not command:
            return jsonify({
                "status": "error",
                "message": "Command is empty.",
                "output": ""
            })

        # Gemini API 호출 (간단한 텍스트 생성)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"다음 CLI 명령에 대한 응답을 생성해 주세요: {command}",
        )

        # 응답 텍스트를 파싱하여 CLI 출력 형식에 맞춥니다.
        # 실제 CLI 환경처럼 짧고 간결하게 응답하도록 프롬프트를 구성할 수도 있습니다.
        output_text = response.text

        return jsonify({
            "status": "success",
            "message": f"Command executed successfully by {MODEL_NAME}.",
            "output": output_text
        })

    except APIError as e:
        return jsonify({
            "status": "error",
            "message": f"Gemini API Error: {e}",
            "output": ""
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {e}",
            "output": ""
        }), 500

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True)