# FastAPI Application

FastAPI 기반 간단한 웹 애플리케이션

## 로컬 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# FastAPI 서버 실행 (포트 8000)
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Docker 실행 방법

```bash
# Docker 이미지 빌드
docker build -t greenai-app .

# Docker 컨테이너 실행 (포트 80:8000 매핑)
docker run -p 80:8000 greenai-app
```

## 배포 방법

### AWS Lightsail 배포

1. **Lightsail 인스턴스 생성**
   - Ubuntu 20.04 LTS
   - Static IP 할당
   - 포트 80 허용

2. **서버 설정 및 배포**
   ```bash
   # Docker 설치
   sudo apt update && sudo apt install -y docker.io
   sudo systemctl start docker
   
   # 프로젝트 배포
   git clone <repository-url>
   cd greenai-fastapi-assignment
   chmod +x scripts/deploy.sh
   sudo ./scripts/deploy.sh
   ```

3. **도메인 연결**
   - DNS A 레코드를 Static IP로 설정

## API 엔드포인트

| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/` | `<h1>Hello GreenAI</h1>` |
| GET | `/static` | 정적 페이지 (index.html) |

## 검증

```bash
# 로컬
curl -i http://localhost:8000/
curl -I http://localhost:8000/static

# 배포
curl -i http://www.greenai.kro.kr/
curl -I http://www.greenai.kro.kr/static
```