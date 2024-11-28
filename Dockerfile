FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . /app/

# 컨테이너 실행 시 FastAPI 앱 실행
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
