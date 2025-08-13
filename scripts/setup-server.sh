#!/bin/bash

# AWS Lightsail 서버 초기 설정 스크립트

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
rm get-docker.sh

echo "Docker 설치 완료!"
echo "로그아웃 후 재로그인하여 docker 명령어를 사용하세요."