#!/bin/bash

# GreenAI 배포 스크립트

# 기존 컨테이너 정리
docker stop greenai-app 2>/dev/null || true
docker rm greenai-app 2>/dev/null || true

# 이미지 빌드
docker build -t greenai-assignment .

# 컨테이너 실행 (포트 80:8000)
docker run -d -p 80:8000 --name greenai-app greenai-assignment

echo "배포 완료!"
echo "확인: curl http://localhost/"
docker ps --filter "name=greenai-app"