import json
from flask import Flask, request, jsonify, render_template_string

# Flask 애플리케이션 초기화
app = Flask(__name__)

# HTML 템플릿 (Tailwind CSS 포함)
# 모든 HTML, CSS, JavaScript는 하나의 템플릿 문자열에 포함됩니다.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 기반 분석 챗봇</title>
    <!-- Tailwind CSS CDN 로드 -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Inter 폰트 설정 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc; /* Slate-50 */
        }
        /* 스크롤바 커스텀 */
        #chat-history::-webkit-scrollbar {
            width: 8px;
        }
        #chat-history::-webkit-scrollbar-thumb {
            background-color: #e2e8f0; /* Slate-200 */
            border-radius: 10px;
        }
        #chat-history::-webkit-scrollbar-track {
            background-color: #f8fafc; /* Slate-50 */
        }
    </style>
</head>
<body class="min-h-screen flex flex-col p-4">

    <!-- 메인 컨테이너 (중앙 정렬 및 최대 너비 설정) -->
    <div class="max-w-4xl w-full mx-auto bg-white rounded-xl shadow-2xl p-6 lg:p-8">

        <!-- 헤더 및 상태 정보 -->
        <header class="mb-6 border-b pb-4">
            <h1 class="text-xl font-bold text-gray-800">S-Parameter Analysis Tool with Ollama + ChromaDB</h1>
            <p class="text-sm text-gray-500 mt-1">Using Fine-tuned Gemma 2/7B Q4 Model + Knowledge Database</p>
            <p id="status" class="text-sm font-medium text-green-600 mt-2">[STATUS] Connected</p>
        </header>

        <!-- 탭 네비게이션 -->
        <nav class="flex space-x-4 border-b pb-1 mb-6 text-sm">
            <button class="tab-button text-gray-600 hover:text-blue-600 p-2 rounded-lg">1. Model Setup</button>
            <button class="tab-button text-gray-600 hover:text-blue-600 p-2 rounded-lg">2. Data Loading</button>
            <button class="tab-button text-blue-600 font-semibold border-b-2 border-blue-600 p-2">3. AI Analysis</button>
            <button class="tab-button text-gray-600 hover:text-blue-600 p-2 rounded-lg">4. ChromaDB Knowledge Chat</button>
            <button class="tab-button text-gray-600 hover:text-blue-600 p-2 rounded-lg">Help</button>
        </nav>

        <!-- AI 분석 섹션 헤더 -->
        <div class="mb-4">
            <h2 class="text-lg font-semibold text-gray-800">AI-Powered S-Parameter Analysis</h2>
            <p class="text-sm text-gray-500">Using Gemma 2/7B Q4 Fine-tuned Model via Ollama</p>
        </div>

        <!-- 채팅 이력 영역 -->
        <div id="chat-history" class="h-96 overflow-y-auto p-4 bg-gray-50 rounded-lg border mb-4 shadow-inner">
            <!-- 초기 챗봇 메시지 -->
            <div class="flex items-start mb-4">
                <span class="text-lg font-bold text-blue-600 mr-3">🤖</span>
                <div class="bg-blue-100 p-3 rounded-xl rounded-tl-none max-w-lg text-gray-800">
                    안녕하세요! S-Parameter 분석에 대해 어떤 질문이 있으신가요?
                </div>
            </div>
            <!-- 메시지가 여기에 동적으로 추가됩니다 -->
        </div>

        <!-- 입력 및 전송 영역 -->
        <div class="flex space-x-3 mb-3">
            <input type="text" id="user-input" placeholder="Enter Question"
                   class="flex-grow p-3 border border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500 text-sm"
                   onkeydown="if(event.key === 'Enter') document.getElementById('send-button').click()">
            <button id="send-button"
                    class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition duration-150 ease-in-out shadow-lg">
                Send
            </button>
        </div>

        <!-- 유틸리티 버튼 및 고급 설정 -->
        <div class="flex justify-between items-center mb-6 pt-2 border-t border-gray-200">
            <div class="space-x-2">
                <button id="clear-button"
                        class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-xl hover:bg-gray-200 transition duration-150">
                    [CLEAR] Clear Chat
                </button>
                <button id="stop-button"
                        class="px-4 py-2 text-sm text-red-600 bg-red-100 rounded-xl hover:bg-red-200 transition duration-150">
                    [STOP] Stop Generation
                </button>
            </div>
            <a href="#" class="text-sm text-gray-500 hover:text-gray-700">Advanced Settings <span class="ml-1">▾</span></a>
        </div>

        <!-- 예시 질문 영역 -->
        <div class="p-4 bg-gray-50 rounded-xl border">
            <p class="text-blue-600 font-semibold mb-3 text-sm">Examples</p>
            <div id="example-chips" class="flex flex-wrap gap-2">
                <!-- 예시 칩들이 여기에 추가됩니다 -->
                <button class="example-chip px-3 py-1 text-xs text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-blue-50 transition duration-150"
                        data-question="Analyze the impedance matching status from the S11 magnitude.">
                    Analyze the impedance matching status from the S11 magnitude.
                </button>
                <button class="example-chip px-3 py-1 text-xs text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-blue-50 transition duration-150"
                        data-question="What does the S21 insertion loss tell us about the circuit performance?">
                    What does the S21 insertion loss tell us about the circuit performance?
                </button>
                <button class="example-chip px-3 py-1 text-xs text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-blue-50 transition duration-150"
                        data-question="Calculate the VSWR from the S11 data and identify problem frequencies.">
                    Calculate the VSWR from the S11 data and identify problem frequencies.
                </button>
                <button class="example-chip px-3 py-1 text-xs text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-blue-50 transition duration-150"
                        data-question="Analyze the phase linearity and group delay from S21 phase data.">
                    Analyze the phase linearity and group delay from S21 phase data.
                </button>
            </div>
        </div>
    </div>

    <!-- JavaScript 로직 -->
    <script>
        const chatHistory = document.getElementById('chat-history');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        const clearButton = document.getElementById('clear-button');
        const exampleChips = document.querySelectorAll('.example-chip');

        /**
         * 새로운 메시지를 채팅 이력에 추가합니다.
         * @param {string} sender 'user' 또는 'bot'
         * @param {string} message 표시할 메시지 텍스트
         */
        function appendMessage(sender, message) {
            const messageContainer = document.createElement('div');
            messageContainer.className = 'flex items-start mb-4 ' + (sender === 'user' ? 'justify-end' : '');

            const messageBubble = document.createElement('div');
            messageBubble.className = 'p-3 rounded-xl max-w-lg text-gray-800 shadow-md';

            if (sender === 'user') {
                messageBubble.className += ' bg-indigo-500 text-white rounded-br-none';
                messageContainer.innerHTML = `<div class="text-sm font-semibold mr-3 self-start">나</div>`; // 사용자 아이콘은 생략하고 텍스트만 표시
                messageContainer.appendChild(messageBubble);
            } else {
                messageBubble.className += ' bg-blue-100 rounded-tl-none';
                messageContainer.innerHTML = `<span class="text-lg font-bold text-blue-600 mr-3 self-start">🤖</span>`;
                messageContainer.appendChild(messageBubble);
            }

            // 메시지 내용에 줄바꿈을 적용합니다.
            const messageText = document.createElement('p');
            messageText.textContent = message;
            messageBubble.appendChild(messageText);

            chatHistory.appendChild(messageContainer);
            // 스크롤을 최하단으로 이동
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        /**
         * API 호출을 처리하고 응답을 채팅에 표시합니다.
         */
        async function handleSendMessage() {
            const query = userInput.value.trim();
            if (!query) return;

            // 1. 사용자 메시지를 표시합니다.
            appendMessage('user', query);
            userInput.value = ''; // 입력 필드를 비웁니다.
            sendButton.disabled = true; // 전송 버튼 비활성화

            try {
                // 2. Flask 백엔드의 /api/command로 데이터를 전송합니다.
                const response = await fetch('/api/command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command: query })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                // 3. 챗봇 응답을 표시합니다.
                const botResponse = data.response || "죄송합니다. 응답을 받지 못했습니다.";
                appendMessage('bot', botResponse);

            } catch (error) {
                console.error('API 호출 중 오류 발생:', error);
                appendMessage('bot', 'API 호출 중 오류가 발생했습니다. 콘솔을 확인해주세요.');
            } finally {
                sendButton.disabled = false; // 전송 버튼 다시 활성화
            }
        }

        /**
         * 채팅 이력을 지웁니다.
         */
        function handleClearChat() {
            // 초기 챗봇 메시지를 제외한 모든 메시지를 제거합니다.
            while (chatHistory.children.length > 1) {
                chatHistory.removeChild(chatHistory.lastChild);
            }
            // 초기 챗봇 메시지 내용은 유지
        }

        // 이벤트 리스너 설정
        sendButton.addEventListener('click', handleSendMessage);
        clearButton.addEventListener('click', handleClearChat);

        // 예시 칩 클릭 이벤트 설정
        exampleChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const question = chip.getAttribute('data-question');
                userInput.value = question;
                // 바로 전송할 수도 있고, 사용자가 편집하도록 필드에만 채워둘 수도 있습니다.
                // 여기서는 필드에 채우고 사용자가 Send를 누르도록 합니다.
                userInput.focus();
            });
        });
        
    </script>
</body>
</html>
"""

# 루트 경로 핸들러
@app.route('/')
def index():
    """HTML 템플릿을 렌더링합니다."""
    # render_template_string을 사용하여 HTML_TEMPLATE 문자열을 렌더링합니다.
    return render_template_string(HTML_TEMPLATE)

# API 명령 처리 핸들러
@app.route('/api/command', methods=['POST'])
def handle_command():
    """
    프론트엔드에서 전송된 명령(쿼리)을 처리합니다.
    여기에 실제 AI/Python 실행 로직을 추가하세요.
    """
    try:
        data = request.get_json()
        command = data.get('command')

        if not command:
            return jsonify({'response': '오류: 명령이 제공되지 않았습니다.'}), 400

        print(f"받은 명령: {command}")

        # --- 이 부분에 실제 Python AI/분석 코드를 구현하세요. ---
        # 예시: 간단한 에코 응답 (더미 응답)
        bot_response = f"귀하의 질문 '{command}'에 대한 AI 분석을 실행합니다. (현재는 더미 응답입니다.)"
        # ----------------------------------------------------

        return jsonify({'response': bot_response})

    except Exception as e:
        print(f"API 처리 오류: {e}")
        return jsonify({'response': '서버 처리 중 오류가 발생했습니다.'}), 500

# 앱 실행
if __name__ == '__main__':
    # 디버그 모드로 Flask 앱 실행
    # 터미널에서 'python app.py'로 실행 가능
    app.run(debug=True)
