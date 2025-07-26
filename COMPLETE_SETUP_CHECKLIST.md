# ✅ AI Forge 完全セットアップチェックリスト

このチェックリストを**全て完了**しないとBotは動きません。一つずつ確実に実行してください。

## 🎯 Phase 1: 基本準備

### 📦 環境準備
- [ ] Python 3.8以上がインストール済み
- [ ] Gitがインストール済み
- [ ] リポジトリをクローン済み
- [ ] `pip install -r requirements.txt` 実行済み

### 💳 アカウント準備
- [ ] Discordアカウント作成済み
- [ ] GitHubアカウント作成済み
- [ ] OpenAIアカウント作成済み（支払い方法設定済み）
- [ ] Google Cloudアカウント作成済み（オプション）

## 🤖 Phase 2: Discord設定（必須）

### Discord Developer Portal
- [ ] https://discord.com/developers/applications にアクセス
- [ ] 「New Application」でアプリ作成
- [ ] アプリ名設定：`AI Forge Bot`
- [ ] 「Bot」タブでBot作成
- [ ] **Botトークンをコピー**（重要！）
- [ ] 以下の設定を有効化：
  - [ ] MESSAGE CONTENT INTENT
  - [ ] SERVER MEMBERS INTENT  
  - [ ] PRESENCE INTENT

### Bot権限設定
- [ ] OAuth2 → URL Generator
- [ ] Scopes選択：`bot`, `applications.commands`
- [ ] Bot Permissions選択：
  - [ ] Manage Roles
  - [ ] Manage Channels
  - [ ] View Channels
  - [ ] Send Messages
  - [ ] Manage Messages
  - [ ] Embed Links
  - [ ] Attach Files
  - [ ] Read Message History
  - [ ] Add Reactions
  - [ ] Use Slash Commands
  - [ ] Send Messages in Threads
  - [ ] Create Public Threads
  - [ ] Use External Emojis

### Discordサーバー設定
- [ ] サーバー作成または管理者権限確認
- [ ] 開発者モード有効化
- [ ] **サーバーIDをコピー**
- [ ] 以下のチャンネル構造を**完全に**作成：

```
🏠 WELCOME & INFO
├── 📋 welcome-and-rules
├── 📢 announcements  
└── 👋 introduce-yourself

💻 CORE DEVELOPMENT
├── 💬 general-dev
├── 🆘 dev-help
├── 🔍 code-review-queue    ← 重要
└── 👥 pair-programming

🧠 AI RESEARCH & DISCUSSION  
├── 📄 paper-summaries      ← 重要
├── 🎨 model-showcase
├── 📊 dataset-discussion
└── ⚖️ ai-ethics

🤖 AI TRAINING & FEEDBACK
├── 🧠 ai-training          ← 重要
├── 📈 feedback-stats
└── 🎯 training-results

🛡️ MODERATION & LOGS
├── 📋 mod-log              ← 重要
├── ⚠️ warnings
└── 🔒 admin-only
```

### Bot招待
- [ ] 生成されたOAuth2 URLでBot招待
- [ ] 全権限が付与されていることを確認
- [ ] BotがサーバーにいることをDiscordで確認

## 🔑 Phase 3: APIキー設定

### OpenAI API（必須）
- [ ] https://platform.openai.com/ でアカウント作成
- [ ] 支払い方法設定（クレジットカード）
- [ ] $5-10をチャージ
- [ ] APIキー作成：`AI Forge Bot`
- [ ] **APIキーをコピー**
- [ ] 使用量制限設定：$20-50/月

### GitHub Token（コードレビュー用）
- [ ] https://github.com/settings/tokens でトークン作成
- [ ] スコープ選択：`repo`, `admin:repo_hook`, `read:org`
- [ ] **トークンをコピー**
- [ ] リポジトリ名・オーナー名を確認

### Google Perspective API（モデレーション用）
- [ ] Google Cloud Console でプロジェクト作成
- [ ] Perspective Comment Analyzer API 有効化
- [ ] APIキー作成
- [ ] **APIキーをコピー**

### Discord Webhook（GitHub連携用）
- [ ] #general-dev チャンネルで右クリック
- [ ] 「連携サービス」→「ウェブフックを作成」
- [ ] 名前：`GitHub Notifier`
- [ ] **Webhook URLをコピー**

## 📝 Phase 4: 環境変数設定

### .envファイル作成
- [ ] `cp .env.example .env` 実行
- [ ] ファイル権限設定：`chmod 600 .env`

### 必須項目設定
```env
# Discord（必須）
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_server_id_here

# OpenAI（必須）
OPENAI_API_KEY=your_openai_key_here

# GitHub（コードレビュー用）
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo_name

# Webhook（GitHub連携用）
GITHUB_WEBHOOK_URL=your_discord_webhook_url

# RSS（論文要約用）
ARXIV_RSS_URLS=http://export.arxiv.org/rss/cs.AI,http://export.arxiv.org/rss/cs.LG

# Moderation（オプション）
PERSPECTIVE_API_KEY=your_perspective_key
TOXICITY_THRESHOLD=0.7
```

### 設定値チェック
- [ ] DISCORD_TOKEN が `MTk` または `MTA` で始まる
- [ ] DISCORD_GUILD_ID が17-20桁の数字
- [ ] OPENAI_API_KEY が `sk-proj-` で始まる
- [ ] GITHUB_TOKEN が `ghp_` で始まる
- [ ] GITHUB_WEBHOOK_URL が `https://discord.com/api/webhooks/` で始まる

## 🧪 Phase 5: 動作テスト

### APIキーテスト
- [ ] `python test_api_keys.py` 実行
- [ ] 全てのテストが成功（✅）
- [ ] エラーがある場合は該当セクションを再確認

### Bot起動テスト
- [ ] `python start_paper_bot.py` 実行
- [ ] "Paper Summarizer Bot がログインしました！" 表示
- [ ] "要約チャンネルを見つけました: paper-summaries" 表示
- [ ] "コマンドを同期しました" 表示

### Discord機能テスト
- [ ] Discordで Bot がオンライン状態
- [ ] `/ping` コマンドが応答
- [ ] `/status` コマンドでBot情報表示
- [ ] `/check_papers` コマンドで論文要約実行

## 🚀 Phase 6: 本格運用

### 基本機能確認
- [ ] 論文要約が #paper-summaries に投稿される
- [ ] GitHub Push時にDiscordに通知が来る
- [ ] コードレビューが動作する（PRがある場合）

### 監視設定
- [ ] Bot のログ出力を確認
- [ ] エラーが発生していないか確認
- [ ] API使用量を定期的にチェック

### コミュニティ運用
- [ ] ルールを #welcome-and-rules に投稿
- [ ] メンバーを招待
- [ ] 各チャンネルの使い方を説明

## 🆘 トラブルシューティング

### よくある問題

#### Bot が起動しない
- [ ] `.env` ファイルが存在するか確認
- [ ] DISCORD_TOKEN に余分なスペースがないか確認
- [ ] Bot権限の MESSAGE CONTENT INTENT が有効か確認

#### チャンネルが見つからない
- [ ] チャンネル名が完全一致するか確認（ハイフン必須）
- [ ] Bot にチャンネル閲覧権限があるか確認
- [ ] サーバーIDが正しいか確認

#### API エラー
- [ ] OpenAI アカウントに残高があるか確認
- [ ] GitHub Token の権限が正しいか確認
- [ ] インターネット接続を確認

#### コマンドが応答しない
- [ ] Bot権限の "Use Slash Commands" が有効か確認
- [ ] Bot を一度サーバーから削除して再招待
- [ ] Bot を再起動

## 📞 サポート

### 問題が解決しない場合
1. **GitHub Issues**: https://github.com/daideguchi/ai-forge-community/issues
2. **詳細ログ**: Bot起動時のエラーメッセージをコピー
3. **設定確認**: `python test_api_keys.py` の結果を添付

### 緊急時対応
1. Bot停止: `Ctrl+C`
2. 設定リセット: `.env` ファイルを再作成
3. 完全再セットアップ: このチェックリストを最初から実行

---

## 🎉 完了確認

**全てのチェックボックスにチェックが入ったら、AI Forgeの準備完了です！**

最終確認：
- [ ] Discord で Bot がオンライン
- [ ] `/ping` コマンドが応答
- [ ] 論文要約が自動投稿される
- [ ] GitHub連携が動作する

**おめでとうございます！AI駆動開発コミュニティの運用を開始できます。** 🚀