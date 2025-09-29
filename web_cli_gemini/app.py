import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# .env ���Ͽ��� ȯ�� ������ �ε��մϴ�. (GEMINI_API_KEY)
load_dotenv()

app = Flask(__name__)

# Gemini Ŭ���̾�Ʈ �ʱ�ȭ
try:
    # ȯ�� �������� API Ű�� �ڵ����� �ε��մϴ�.
    client = genai.Client()
    # �� ���� (���ϴ� �𵨷� ���� ����)
    MODEL_NAME = 'gemini-2.5-flash'
except Exception as e:
    # API Ű�� �������� �ʾҰų� �ʱ�ȭ�� ������ ���
    print(f"Error initializing Gemini Client: {e}")
    client = None

@app.route('/')
def index():
    """�� Ŭ���̾�Ʈ�� �⺻ HTML �������� �������մϴ�."""
    return render_template('index.html')

@app.route('/api/send_command', methods=['POST'])
def send_command():
    """Ŭ���̾�Ʈ�κ��� ����� �޾� Gemini API�� �����ϰ� ����� ��ȯ�մϴ�."""
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

        # Gemini API ȣ�� (������ �ؽ�Ʈ ����)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"���� CLI ��ɿ� ���� ������ ������ �ּ���: {command}",
        )

        # ���� �ؽ�Ʈ�� �Ľ��Ͽ� CLI ��� ���Ŀ� ����ϴ�.
        # ���� CLI ȯ��ó�� ª�� �����ϰ� �����ϵ��� ������Ʈ�� ������ ���� �ֽ��ϴ�.
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
    # ���� ���� ����
    app.run(debug=True)