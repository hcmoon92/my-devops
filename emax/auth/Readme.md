​1. Google API Console 설정
​가장 먼저, 구글 API 콘솔에서 OAuth 클라이언트를 설정해야 합니다.
​Google Cloud Console 에 접속하여 새 프로젝트를 만듭니다.
​API 및 서비스 > 사용자 인증 정보로 이동합니다.
​사용자 인증 정보 만들기를 클릭하고 OAuth 클라이언트 ID를 선택합니다.
​애플리케이션 유형을 웹 애플리케이션으로 설정합니다.
​승인된 리디렉션 URI에 http://127.0.0.1:5000/callback (개발 환경) 또는 https://yourdomain.com/callback (운영 환경)을 추가합니다.
​이 과정이 완료되면, 클라이언트 ID와 클라이언트 보안 비밀이 생성됩니다. 이 정보는 Flask 애플리케이션에서 사용됩니다.