# 🔑 API キー完全取得ガイド

AI Forgeの各機能を使うために必要なAPIキーの取得方法を詳しく説明します。

## 🎯 必要なAPIキー一覧

| API | 用途 | 必須度 | 月額コスト目安 |
|-----|------|--------|----------------|
| **OpenAI** | 論文要約、コードレビュー | 高 | $10-50 |
| **GitHub** | リポジトリ連携 | 中 | 無料 |
| **Google Perspective** | モデレーション | 中 | 無料 |
| **Anthropic Claude** | 高品質AI応答 | 低 | $10-30 |

## 🤖 OpenAI API キー取得

### 必要な理由
- **Paper Summarizer**: 論文要約生成
- **Code Reviewer**: Pull Request自動レビュー
- **Human-in-the-Loop**: AI応答生成

### 取得手順

1. **OpenAI Platform**にアクセス
   ```
   https://platform.openai.com/
   ```

2. **アカウント作成/ログイン**
   - 「Sign up」または「Log in」
   - 電話番号認証が必要

3. **支払い方法設定**
   - 右上のアカウントメニュー → 「Billing」
   - 「Add payment method」
   - クレジットカード情報を入力
   - **重要**: $5-10程度をチャージ推奨

4. **APIキー作成**
   - 左サイドバー「API keys」
   - 「Create new secret key」
   - 名前を入力：`AI Forge Bot`
   - **キーをコピー**（再表示されません）

5. **使用量制限設定**
   - 「Usage limits」で月額上限を設定
   - 推奨：$20-50/月

### .env設定
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### コスト管理
```
GPT-3.5-turbo: $0.0015/1K tokens（入力）、$0.002/1K tokens（出力）
GPT-4: $0.03/1K tokens（入力）、$0.06/1K tokens（出力）

目安：
- 論文要約1回: 約$0.01-0.05
- コードレビュー1回: 約$0.05-0.20
```

## 🐙 GitHub Personal Access Token

### 必要な理由
- **Code Reviewer**: Pull Request情報取得
- **Webhook設定**: リポジトリ管理

### 取得手順

1. **GitHub Settings**にアクセス
   ```
   https://github.com/settings/tokens
   ```

2. **「Generate new token」** → **「Generate new token (classic)」**

3. **トークン設定**
   ```
   Note: AI Forge Bot
   Expiration: 90 days（推奨）
   
   Select scopes:
   ✅ repo（フルアクセス）
   ✅ admin:repo_hook（Webhook管理）
   ✅ read:org（組織情報読み取り）
   ✅ user:email（メールアドレス読み取り）
   ```

4. **「Generate token」**をクリック

5. **トークンをコピー**（再表示されません）

### .env設定
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repository_name
```

## 🛡️ Google Perspective API

### 必要な理由
- **Moderator Bot**: 有害コンテンツ検出

### 取得手順

1. **Google Cloud Console**にアクセス
   ```
   https://console.cloud.google.com/
   ```

2. **プロジェクト作成**
   - 「プロジェクトを選択」→「新しいプロジェクト」
   - プロジェクト名：`AI Forge Moderation`

3. **Perspective API有効化**
   - 「APIとサービス」→「ライブラリ」
   - 「Perspective Comment Analyzer API」を検索
   - 「有効にする」をクリック

4. **認証情報作成**
   - 「APIとサービス」→「認証情報」
   - 「認証情報を作成」→「APIキー」
   - **キーをコピー**

5. **API制限設定**
   - 作成したAPIキーをクリック
   - 「APIの制限」→「キーを制限」
   - 「Perspective Comment Analyzer API」のみ選択

### .env設定
```env
PERSPECTIVE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TOXICITY_THRESHOLD=0.7
```

### 使用量制限
```
無料枠: 1日1,000リクエスト
有料: $1/1,000リクエスト（1日1,000超過分）
```

## 🧠 Anthropic Claude API（オプション）

### 必要な理由
- **高品質なAI応答**が必要な場合
- OpenAIの代替として

### 取得手順

1. **Anthropic Console**にアクセス
   ```
   https://console.anthropic.com/
   ```

2. **アカウント作成**
   - 「Sign up」
   - メール認証

3. **支払い設定**
   - 「Billing」→「Add payment method」
   - クレジットカード登録

4. **APIキー作成**
   - 「API Keys」→「Create Key」
   - 名前：`AI Forge Bot`
   - **キーをコピー**

### .env設定
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🔗 Discord Webhook URL

### 必要な理由
- **GitHub連携**: Push/PR通知をDiscordに送信

### 取得手順

1. **Discordチャンネル設定**
   - 通知を受け取りたいチャンネル（例：#general-dev）を右クリック
   - 「連携サービス」をクリック

2. **Webhook作成**
   - 「ウェブフックを作成」
   - 名前：`GitHub Notifier`
   - 「ウェブフックURLをコピー」

### .env設定
```env
GITHUB_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 📊 RSS フィード設定

### 設定内容
```env
ARXIV_RSS_URLS=http://export.arxiv.org/rss/cs.AI,http://export.arxiv.org/rss/cs.LG,http://export.arxiv.org/rss/cs.CL
```

### 利用可能なフィード
```
cs.AI  - 人工知能
cs.LG  - 機械学習  
cs.CL  - 計算言語学
cs.CV  - コンピュータビジョン
cs.RO  - ロボティクス
cs.NE  - ニューラル・進化計算
```

## 💾 データベース設定

### 開発環境（SQLite）
```env
DATABASE_URL=sqlite:///ai_community.db
```

### 本番環境（PostgreSQL）
```env
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
DB_PASSWORD=your_secure_password
```

## 🔒 セキュリティ注意事項

### APIキー管理
1. **絶対に公開しない**
   - GitHub、Discord、SNSに投稿禁止
   - スクリーンショットに含めない

2. **定期的な更新**
   - 3-6ヶ月ごとにキーを再生成
   - 古いキーは無効化

3. **権限最小化**
   - 必要最小限の権限のみ付与
   - 不要なスコープは選択しない

### .envファイル保護
```bash
# ファイル権限設定
chmod 600 .env

# Gitから除外確認
echo ".env" >> .gitignore
```

## 💰 コスト見積もり

### 小規模コミュニティ（50人）
```
OpenAI API: $10-20/月
Google Perspective: 無料
GitHub: 無料
合計: $10-20/月
```

### 中規模コミュニティ（200人）
```
OpenAI API: $30-60/月
Google Perspective: $5-10/月
GitHub: 無料
合計: $35-70/月
```

### 大規模コミュニティ（500人+）
```
OpenAI API: $100-200/月
Google Perspective: $20-40/月
GitHub: 無料
合計: $120-240/月
```

## ✅ 設定完了チェックリスト

- [ ] OpenAI APIキー取得・設定
- [ ] GitHub Personal Access Token取得・設定
- [ ] Google Perspective APIキー取得・設定
- [ ] Discord Webhook URL取得・設定
- [ ] RSS フィードURL設定
- [ ] .envファイル権限設定（600）
- [ ] 全APIキーの動作テスト完了

## 🧪 APIキーテスト

### テストスクリプト実行
```bash
python test_api_keys.py
```

### 手動テスト
```bash
# OpenAI テスト
python -c "import openai; print('OpenAI OK')"

# GitHub テスト  
python -c "from github import Github; print('GitHub OK')"

# Perspective テスト
python -c "from googleapiclient import discovery; print('Perspective OK')"
```

**🎉 全てのAPIキーが設定できたら、AI Forgeの全機能が利用可能になります！**