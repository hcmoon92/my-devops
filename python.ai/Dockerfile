# 파이썬 기본 이미지를 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 애플리케이션 실행 명령어
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_app_name:app"]
