import os
from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
from google import genai
# types 모듈을 가져와서 GenerateContentConfig를 사용합니다.
from google.genai import types 
from google.genai.errors import APIError

# .env 파일에서 환경 변수를 로드합니다. (실제 환경에서 GEMINI_API_KEY를 설정해야 합니다.)
load_dotenv()

app = Flask(__name__)

# Gemini 클라이언트 초기화. 키는 서버 환경에서 안전하게 로드됩니다.
client = None
MODEL_NAME = 'gemini-2.5-flash-preview-05-20'

try:
    # 환경 변수에서 API 키를 자동으로 로드합니다.
    client = genai.Client()
    print("Gemini Client initialized successfully.")
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")
    client = None

@app.route('/')
def index():
    """웹 클라이언트의 기본 HTML 페이지를 렌더링합니다."""
    # 클라이언트 HTML 파일을 렌더링합니다.
    return render_template('index.html')

def generate_stream(command):
    """
    Gemini API 스트리밍 호출을 위한 제너레이터 함수.
    응답 토큰이 생성될 때마다 yield를 통해 실시간으로 반환합니다.
    """
    global client, MODEL_NAME

    if client is None:
        yield "Error: Gemini API Client is not initialized. Please check server configuration."
        return

    try:
        # Gemini API 호출 설정
        # 오류 해결: tools 인수를 GenerateContentConfig 객체를 통해 config 매개변수로 전달합니다.
        generation_config = types.GenerateContentConfig(
            tools=[{ "google_search": {} }] # Google Search Grounding 설정
        )
        
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=[f"사용자의 명령/질문에 답변하세요. CLI 형식의 답변처럼 짧고 명료하게 응답하되, **굵은 글씨**와 줄 바꿈 등의 Markdown 서식을 사용하여 응답 내용을 풍부하게 작성하세요. 질문: {command}"],
            config=generation_config, # 설정 객체를 config 인수로 전달
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
        return Response("Gemini API Client is not initialized. Check your server API key.", mimetype='text/plain', status=500)

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
    app.run(host='0.0.0.0', port=7070, debug=True)
