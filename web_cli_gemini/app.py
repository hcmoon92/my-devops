import os
import json
from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# .env 파일에서 환경 변수를 로드합니다. (GEMINI_API_KEY)
load_dotenv()

app = Flask(__name__)

# Gemini 클라이언트 초기화
client = None
MODEL_NAME = 'gemini-2.5-flash'

try:
    # 환경 변수에서 API 키를 자동으로 로드합니다.
    client = genai.Client()
except Exception as e:
    # API 키가 설정되지 않았거나 초기화에 실패한 경우
    print(f"Error initializing Gemini Client: {e}")
    client = None

@app.route('/')
def index():
    """웹 클라이언트의 기본 HTML 페이지를 렌더링합니다."""
    return render_template('index.html')

def generate_stream(command):
    """
    Gemini API 스트리밍 호출을 위한 제너레이터 함수.
    응답 토큰이 생성될 때마다 yield를 통해 실시간으로 반환합니다.
    """
    global client, MODEL_NAME

    if client is None:
        yield "Error: Gemini API Client is not initialized."
        return

    try:
        # 스트리밍 API 호출
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=[f"다음 CLI 명령에 대한 응답을 짧고 간결하게, CLI 출력 형식으로 생성해 주세요: {command}"],
        )

        for chunk in response_stream:
            # 텍스트 조각을 클라이언트에게 즉시 전송
            if chunk.text:
                yield chunk.text

    except APIError as e:
        yield f"\n\nGemini API Error: {e}"
    except Exception as e:
        yield f"\n\nAn unexpected error occurred: {e}"

@app.route('/api/send_command', methods=['POST'])
def send_command():
    """클라이언트로부터 명령을 받아 Gemini API로 전송하고 결과를 스트리밍합니다."""
    
    if client is None:
        return Response("Gemini API Client is not initialized. Check your GEMINI_API_KEY.", mimetype='text/plain', status=500)

    try:
        data = request.get_json()
        command = data.get('command', '').strip()

        if not command:
            return Response("Command is empty.", mimetype='text/plain', status=400)

        # 제너레이터 함수를 사용하여 스트리밍 응답 반환
        return Response(generate_stream(command), mimetype='text/plain')

    except Exception as e:
        return Response(f"An unexpected error occurred in Flask: {e}", mimetype='text/plain', status=500)

if __name__ == '__main__':
    # 개발 서버 실행
    # Flask 서버는 이제 0.0.0.0:7070에서 실행되며, /api/send_command는 스트리밍 응답을 제공합니다.
    app.run(host='0.0.0.0', port=7070, debug=True)
