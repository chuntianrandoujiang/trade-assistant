FROM python:3.11-slim

WORKDIR /app

# 系统依赖（reportlab 字体渲染需要）
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# HF Spaces 通过环境变量 $PORT 提供端口（默认 7860）
ENV PORT=7860
EXPOSE 7860

CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
