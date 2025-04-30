# 使用官方提供的 OpenJDK 11 作为基础镜像
FROM openjdk:11-jdk-slim

# 设置工作目录
WORKDIR /app

# 将 Maven 构建生成的可执行 JAR 文件复制到容器中
# 假设您的 JAR 文件在 target 目录下，并且命名为 your-application.jar
# 请根据您的实际项目修改文件名
COPY target/shea-0.0.1-SNAPSHOT.jar app.jar

# 暴露 Spring Boot 应用的端口 (默认为 8081，请根据您的实际配置修改)
EXPOSE 8081

# 定义容器启动时执行的命令
ENTRYPOINT ["java", "-jar", "app.jar"]

# 可以添加一些优化 JVM 的参数 (可选)
# ENTRYPOINT ["java", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]