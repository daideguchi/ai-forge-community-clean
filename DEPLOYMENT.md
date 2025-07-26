# 🚀 AI Forge デプロイメントガイド

このガイドでは、AI Forge を本番環境にデプロイする方法を説明します。

## 🎯 デプロイメント戦略

### 段階的デプロイメント
1. **Phase 1**: Paper Summarizer Bot のみ
2. **Phase 2**: Code Reviewer Bot 追加
3. **Phase 3**: Human-in-the-Loop Bot 追加
4. **Phase 4**: Moderator Bot 追加

## 🐳 Docker デプロイメント

### 前提条件
- Docker & Docker Compose インストール済み
- 環境変数の設定完了

### 本番環境起動

```bash
# 1. リポジトリクローン
git clone https://github.com/daideguchi/ai-forge-community.git
cd ai-forge-community

# 2. 環境変数設定
cp .env.example .env
# .env ファイルを編集

# 3. 本番環境起動
docker-compose up -d

# 4. ログ確認
docker-compose logs -f
```

### サービス管理

```bash
# 全サービス停止
docker-compose down

# 特定サービスのみ起動
docker-compose up -d paper-summarizer

# サービス再起動
docker-compose restart paper-summarizer

# ログ確認
docker-compose logs paper-summarizer
```

## ☁️ クラウドデプロイメント

### Railway デプロイメント

1. **Railway アカウント作成**
   - https://railway.app/

2. **GitHub リポジトリ連携**
   - Railway ダッシュボードで "New Project"
   - GitHub リポジトリを選択

3. **環境変数設定**
   - Railway プロジェクト設定で環境変数を追加
   - `.env.example` の内容を参考に設定

4. **自動デプロイ**
   - Git push で自動デプロイ

### Heroku デプロイメント

```bash
# 1. Heroku CLI インストール
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Heroku アプリ作成
heroku create ai-forge-community

# 3. 環境変数設定
heroku config:set DISCORD_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key

# 4. デプロイ
git push heroku main
```

### AWS ECS デプロイメント

```bash
# 1. ECR リポジトリ作成
aws ecr create-repository --repository-name ai-forge

# 2. Docker イメージビルド・プッシュ
docker build -t ai-forge .
docker tag ai-forge:latest 123456789012.dkr.ecr.region.amazonaws.com/ai-forge:latest
docker push 123456789012.dkr.ecr.region.amazonaws.com/ai-forge:latest

# 3. ECS タスク定義・サービス作成
# AWS コンソールまたは CLI で設定
```

## 🔧 環境変数設定

### 必須環境変数

```env
# Discord Bot (全Bot共通)
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_server_id

# AI API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# GitHub (Code Reviewer用)
GITHUB_TOKEN=your_github_token
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo

# Moderation (Moderator用)
PERSPECTIVE_API_KEY=your_perspective_key
TOXICITY_THRESHOLD=0.7

# Database (本番環境)
DATABASE_URL=postgresql://user:pass@host:5432/db
DB_PASSWORD=secure_password
```

### オプション環境変数

```env
# RSS Feeds
ARXIV_RSS_URLS=http://export.arxiv.org/rss/cs.AI,http://export.arxiv.org/rss/cs.LG

# Webhook URLs
GITHUB_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/github

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/ai-forge.log
```

## 📊 監視・ログ

### ヘルスチェック

```bash
# Docker ヘルスチェック
docker-compose ps

# Bot ステータス確認
curl http://localhost:8080/health
```

### ログ管理

```bash
# リアルタイムログ
docker-compose logs -f paper-summarizer

# ログファイル確認
tail -f logs/ai-forge.log

# エラーログのみ
docker-compose logs paper-summarizer | grep ERROR
```

### メトリクス収集

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-forge'
    static_configs:
      - targets: ['localhost:8080']
```

## 🔒 セキュリティ

### 環境変数の保護

```bash
# 1. 環境変数ファイルの権限設定
chmod 600 .env

# 2. Git から除外
echo ".env" >> .gitignore

# 3. シークレット管理サービス使用
# AWS Secrets Manager, Azure Key Vault, etc.
```

### ネットワークセキュリティ

```yaml
# docker-compose.yml
networks:
  ai-forge-network:
    driver: bridge
    internal: true

services:
  paper-summarizer:
    networks:
      - ai-forge-network
```

## 🔄 CI/CD パイプライン

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Railway
        uses: railway-app/railway-action@v1
        with:
          api-token: ${{ secrets.RAILWAY_TOKEN }}
          project-id: ${{ secrets.RAILWAY_PROJECT_ID }}
```

### 自動テスト

```bash
# テスト実行
python -m pytest tests/ -v

# カバレッジ確認
pytest --cov=bots tests/
```

## 📈 スケーリング

### 水平スケーリング

```yaml
# docker-compose.yml
services:
  paper-summarizer:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### 負荷分散

```nginx
# nginx.conf
upstream ai-forge {
    server app1:8080;
    server app2:8080;
    server app3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://ai-forge;
    }
}
```

## 🚨 トラブルシューティング

### よくある問題

1. **Bot が起動しない**
   ```bash
   # ログ確認
   docker-compose logs paper-summarizer
   
   # 環境変数確認
   docker-compose exec paper-summarizer env | grep DISCORD
   ```

2. **メモリ不足**
   ```yaml
   # リソース制限追加
   services:
     paper-summarizer:
       mem_limit: 1g
   ```

3. **API レート制限**
   ```python
   # レート制限対応
   await asyncio.sleep(1)  # API呼び出し間隔
   ```

## 📞 サポート

### 問題報告
- GitHub Issues: https://github.com/daideguchi/ai-forge-community/issues
- Discord サーバー: [招待リンク]

### 緊急時対応
1. 全サービス停止: `docker-compose down`
2. ログ収集: `docker-compose logs > emergency.log`
3. 問題報告: GitHub Issues に詳細投稿

---

**🎉 デプロイメント完了！**

AI Forge が本番環境で稼働し、コミュニティメンバーがAI駆動開発を体験できるようになります。