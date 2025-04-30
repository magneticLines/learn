#!/bin/bash

# ---------------------- 配置你的参数 ----------------------
PRIVATE_REGISTRY_IP="127.0.0.1"
PRIVATE_REGISTRY_PORT="5000"
DOCKERHUB_USERNAME="sheayin" # 如果您也推送到 Docker Hub 作为备份或测试
PROJECT_NAME="springboot-demo"
IMAGE_TAG="latest"
JAR_FILE_PATH="target/shea-0.0.1-SNAPSHOT.jar" # 请根据您的 Maven/Gradle 构建输出修改
CONTAINER_NAME="springboot-demo"
HOST_PORT="8081"         # 宿主机映射端口
CONTAINER_PORT="8081"  # 容器暴露端口 (与 Dockerfile 和应用配置一致)

# ---------------------- 函数定义 ----------------------

build_image() {
  echo "开始构建 Docker 镜像..."
  docker build -t "${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}/${PROJECT_NAME}:${IMAGE_TAG}" .
  if [ $? -ne 0 ]; then
    echo "构建镜像失败，请检查错误。"
    exit 1
  fi
  echo "Docker 镜像构建成功: ${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}/${PROJECT_NAME}:${IMAGE_TAG}"
}

push_image() {
  echo "开始推送 Docker 镜像到私有 Registry: ${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}"
  docker push "${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}/${PROJECT_NAME}:${IMAGE_TAG}"
  if [ $? -ne 0 ]; then
    echo "推送镜像失败，请检查错误。"
    exit 1
  fi
  echo "Docker 镜像推送成功。"
}

pull_image_on_server() {
  echo "开始在服务器上拉取 Docker 镜像: ${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}/${PROJECT_NAME}:${IMAGE_TAG}"
  ssh shea@172.17.97.140 "docker pull ${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}/${PROJECT_NAME}:${IMAGE_TAG}"
  if [ $? -ne 0 ]; then
    echo "在服务器上拉取镜像失败，请检查错误。"
    exit 1
  fi
  echo "在服务器上拉取镜像成功。"
}

stop_and_remove_old_container() {
  echo "停止并移除旧的 Docker 容器 (如果存在)..."
  ssh shea@172.17.97.140 "docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME} || true"
  echo "旧容器已停止并移除 (如果存在)。"
}

run_new_container() {
  echo "开始在服务器上运行新的 Docker 容器..."
  ssh shea@172.17.97.140 "docker run -d -p ${HOST_PORT}:${CONTAINER_PORT} --name ${CONTAINER_NAME} ${PRIVATE_REGISTRY_IP}:${PRIVATE_REGISTRY_PORT}/${PROJECT_NAME}:${IMAGE_TAG}"
  if [ $? -ne 0 ]; then
    echo "在服务器上运行容器失败，请检查错误。"
    exit 1
  fi
  echo "新的 Docker 容器已成功运行: ${CONTAINER_NAME}"
}

# ---------------------- 主流程 ----------------------

# 1. 构建 Docker 镜像
build_image

# 2. 推送 Docker 镜像到私有 Registry
push_image

# 3. 在服务器上拉取 Docker 镜像
# 注意：您需要配置 SSH 免密登录到您的服务器，或者在脚本中处理密码输入。
pull_image_on_server

# 4. 在服务器上停止并移除旧的容器 (如果存在)
stop_and_remove_old_container

# 5. 在服务器上运行新的 Docker 容器
run_new_container

echo "部署流程完成！您的应用已更新。"

exit 0