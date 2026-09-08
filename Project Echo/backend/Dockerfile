FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖：ffmpeg 是 Whisper 必需的
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . .

# Hugging Face Spaces 默认使用 7860 端口
ENV PORT=7860
EXPOSE 7860

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
