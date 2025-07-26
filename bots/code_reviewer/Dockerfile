FROM python:3.11-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python の依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY bots/ ./bots/
COPY .env* ./

# 非rootユーザーを作成
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Bot を実行
CMD ["python", "bots/code_reviewer/bot.py"]