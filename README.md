# GreenAI FastAPI Assignment

## 로컬 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# FastAPI 서버 실행
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Docker 실행 방법

```bash
# Docker 이미지 빌드
docker build -t greenai-assignment .

# Docker 컨테이너 실행 (포트 80:8000 매핑)
docker run -p 80:8000 greenai-assignment
```

## 배포 방법

1. AWS Lightsail 인스턴스 생성 (Ubuntu)
2. Static IP 할당, 포트 80 허용
3. 서버에서 Docker 설치 후 실행
4. 무료 도메인 A 레코드 → Static IP 설정

## 확인 사항

- GET / → "Hello GreenAI" HTML
- GET /static/index.html → 정적 페이지 접근