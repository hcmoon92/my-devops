import os
from flask import Flask, redirect, request, url_for, session
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # 세션 보안을 위한 비밀 키

# 구글 API 콘솔에서 얻은 정보
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # 개발 환경에서 HTTPS 없이 사용 허용
CLIENT_SECRETS_FILE = "client_secret.json" # 다운로드한 JSON 파일 이름

# OAuth 2.0 Flow 설정
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=['https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_uri='http://127.0.0.1:5000/callback'
)

@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # 콜백으로 받은 인증 코드를 사용해 토큰 교환
    flow.fetch_token(authorization_response=request.url)

    # 토큰이 유효한지 확인하고 사용자 정보 가져오기
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # 사용자 정보(이메일, 프로필 등)를 가져와 세션에 저장
    request_session = google.auth.transport.requests.Request()
    user_info = google.oauth2.id_token.verify_oauth2_token(
        credentials.id_token, request_session
    )
    session['google_id'] = user_info.get('sub')
    session['name'] = user_info.get('name')
    session['email'] = user_info.get('email')

    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'google_id' not in session:
        return redirect(url_for('login'))
    return f"<h1>Hello, {session['name']}!</h1><p>Email: {session['email']}</p>"

if __name__ == '__main__':
    app.run(debug=True)
