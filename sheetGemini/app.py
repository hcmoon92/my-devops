import os
from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
from google import genai
from google.genai import types 
from google.genai.errors import APIError

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

app = Flask(__name__)

# Gemini 클라이언트 초기화. 키는 서버 환경에서 안전하게 로드됩니다.
client = None
MODEL_NAME = 'gemini-2.5-flash-preview-05-20'

try:
    client = genai.Client()
    print("Gemini Client initialized successfully.")
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")
    client = None

# ----------------------------------------------------
# 1. Google Sheet Data Mocking (가상의 구글 시트 데이터)
# ----------------------------------------------------
# 실제 환경에서는 Google Sheets API를 사용하여 이 데이터를 동적으로 가져와야 합니다.
GOOGLE_SHEET_DATA = """
### Data Context (Simulated Sales Report) ###
| Month | Product | Sales (Units) | Revenue (USD) |
|---|---|---|---|
| Jan | Laptop | 150 | 150000 |
| Jan | Monitor | 300 | 45000 |
| Feb | Laptop | 120 | 120000 |
| Feb | Monitor | 350 | 52500 |
| Mar | Keyboard | 800 | 16000 |
| Mar | Laptop | 200 | 200000 |
| Mar | Monitor | 100 | 15000 |
### End of Data Context ###
"""

@app.route('/')
def index():
    """웹 클라이언트의 기본 HTML 페이지를 렌더링합니다."""
    return render_template('index.html')

def generate_stream(command):
    """
    Gemini API 스트리밍 호출을 위한 제너레이터 함수.
    시트 데이터를 포함하여 Gemini에 분석을 요청합니다.
    """
    global client, MODEL_NAME

    if client is None:
        yield "Error: Gemini API Client is not initialized. Please check server configuration."
        return

    # 사용자의 명령과 시트 데이터를 결합하여 최종 프롬프트 생성
    full_prompt = (
        f"당신은 데이터 분석가입니다. 다음 Google Sheet 데이터 컨텍스트를 분석하여 사용자의 요청에 대해 답변하세요. "
        f"응답은 **굵은 글씨**와 줄 바꿈 등의 Markdown 서식을 사용하여 명확하게 작성해 주세요.\n\n"
        f"{GOOGLE_SHEET_DATA}\n\n"
        f"사용자 요청: {command}"
    )

    try:
        # API 설정 (외부 검색 도구는 분석 시 불필요하므로 제거하거나 선택적으로 사용 가능)
        generation_config = types.GenerateContentConfig(
            # tools=[{ "google_search": {} }] # 외부 검색 도구는 데이터 분석 시에는 일반적으로 사용하지 않음
        )
        
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=[full_prompt],
            config=generation_config,
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
    app.run(host='0.0.0.0', port=7080, debug=True)
