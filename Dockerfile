FROM python:3.9-slim

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && apt-get clean

# Pythonライブラリをインストール
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# アプリケーションをコピー
COPY app /app
WORKDIR /app

# Flaskを起動
CMD ["python", "main.py"]
