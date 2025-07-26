# 🤖 Discord完全セットアップガイド

AI Forgeを実際に動かすための**完全なDiscord設定手順**です。この手順を飛ばすとBotは動きません。

## 🎯 必要なもの

- Discordアカウント
- 管理者権限のあるDiscordサーバー（または新規作成）
- 30分程度の時間

## 📋 Step 1: Discord Developer PortalでのBot作成

### 1.1 アプリケーション作成

1. **Discord Developer Portal**にアクセス
   ```
   https://discord.com/developers/applications
   ```

2. **「New Application」**をクリック

3. **アプリケーション名**を入力
   ```
   AI Forge Bot
   ```

4. **「Create」**をクリック

### 1.2 Bot設定

1. 左サイドバーの**「Bot」**をクリック

2. **「Add Bot」**をクリック

3. **重要：Botトークンをコピー**
   - 「Token」セクションの**「Copy」**をクリック
   - このトークンを`.env`ファイルの`DISCORD_TOKEN`に設定
   - ⚠️ **絶対に他人に教えないでください**

4. **Bot設定を調整**
   ```
   ✅ PUBLIC BOT: オン（他の人がBotを招待可能）
   ✅ REQUIRES OAUTH2 CODE GRANT: オフ
   ✅ MESSAGE CONTENT INTENT: オン（重要！）
   ✅ SERVER MEMBERS INTENT: オン
   ✅ PRESENCE INTENT: オン
   ```

## 📋 Step 2: Bot権限設定

### 2.1 OAuth2設定

1. 左サイドバーの**「OAuth2」** → **「URL Generator」**をクリック

2. **Scopes**で以下を選択：
   ```
   ✅ bot
   ✅ applications.commands
   ```

3. **Bot Permissions**で以下を選択：
   ```
   General Permissions:
   ✅ Manage Roles
   ✅ Manage Channels
   ✅ View Channels
   ✅ Send Messages
   ✅ Manage Messages
   ✅ Embed Links
   ✅ Attach Files
   ✅ Read Message History
   ✅ Add Reactions
   ✅ Use Slash Commands
   
   Text Permissions:
   ✅ Send Messages in Threads
   ✅ Create Public Threads
   ✅ Create Private Threads
   ✅ Send TTS Messages
   ✅ Use External Emojis
   ✅ Use External Stickers
   ```

4. **生成されたURL**をコピー
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8589934592&scope=bot%20applications.commands
   ```

## 📋 Step 3: Discordサーバー準備

### 3.1 サーバー作成（新規の場合）

1. Discord左下の**「+」**をクリック
2. **「サーバーを作成」**を選択
3. **「自分用」**を選択
4. サーバー名を入力：
   ```
   AI Forge Community
   ```

### 3.2 必須チャンネル作成

以下のチャンネル構造を**完全に再現**してください：

```
🏠 WELCOME & INFO
├── 📋 welcome-and-rules
├── 📢 announcements  
└── 👋 introduce-yourself

💻 CORE DEVELOPMENT
├── 💬 general-dev
├── 🆘 dev-help
├── 🔍 code-review-queue    ← Code Reviewer Bot用
└── 👥 pair-programming

🧠 AI RESEARCH & DISCUSSION  
├── 📄 paper-summaries      ← Paper Summarizer Bot用（重要！）
├── 🎨 model-showcase
├── 📊 dataset-discussion
└── ⚖️ ai-ethics

🤖 AI TRAINING & FEEDBACK
├── 🧠 ai-training          ← Human-in-the-Loop Bot用
├── 📈 feedback-stats
└── 🎯 training-results

🛡️ MODERATION & LOGS
├── 📋 mod-log              ← Moderator Bot用
├── ⚠️ warnings
└── 🔒 admin-only

🎉 COMMUNITY & EVENTS
├── 💭 random
├── 💼 career-advice
├── 📢 job-postings
└── 🎪 events
```

### 3.3 チャンネル作成手順

1. **カテゴリ作成**
   - サーバー名を右クリック → 「カテゴリを作成」
   - 名前を入力（例：🧠 AI RESEARCH & DISCUSSION）

2. **チャンネル作成**
   - カテゴリを右クリック → 「チャンネルを作成」
   - 「テキストチャンネル」を選択
   - 名前を入力（例：paper-summaries）

### 3.4 サーバーID取得

1. **開発者モードを有効化**
   - Discord設定 → 詳細設定 → 開発者モード：オン

2. **サーバーIDをコピー**
   - サーバー名を右クリック → 「IDをコピー」
   - このIDを`.env`ファイルの`DISCORD_GUILD_ID`に設定

## 📋 Step 4: Botをサーバーに招待

### 4.1 招待実行

1. **Step 2.1で生成したURL**をブラウザで開く

2. **サーバーを選択**
   - 作成したサーバーを選択

3. **権限を確認**
   - 全ての権限にチェックが入っていることを確認

4. **「認証」**をクリック

5. **reCAPTCHA**を完了

### 4.2 招待確認

1. **Botがサーバーに参加**していることを確認
2. **Botがオフライン状態**であることを確認（まだ起動していないため）

## 📋 Step 5: Webhook設定（GitHub連携用）

### 5.1 Discord Webhook作成

1. **通知を受け取りたいチャンネル**（例：general-dev）を右クリック

2. **「連携サービス」**をクリック

3. **「ウェブフックを作成」**をクリック

4. **Webhook設定**
   ```
   名前: GitHub Notifier
   チャンネル: #general-dev
   ```

5. **「ウェブフックURLをコピー」**
   - このURLを`.env`ファイルの`GITHUB_WEBHOOK_URL`に設定

### 5.2 GitHub Repository設定

1. **GitHubリポジトリ**の「Settings」→「Webhooks」

2. **「Add webhook」**をクリック

3. **Webhook設定**
   ```
   Payload URL: [Discord WebhookURL]/github
   Content type: application/json
   Secret: （空白でOK）
   Events: Send me everything
   ```

4. **「Add webhook」**をクリック

## 📋 Step 6: 環境変数設定

### 6.1 .envファイル作成

```bash
cp .env.example .env
```

### 6.2 必須項目設定

```env
# Discord Bot Configuration（必須）
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
DISCORD_GUILD_ID=YOUR_SERVER_ID_HERE

# AI API Keys（機能を使う場合）
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub Configuration（Code Reviewer用）
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo_name

# Webhook URLs（GitHub連携用）
GITHUB_WEBHOOK_URL=your_discord_webhook_url_here

# RSS Feeds（Paper Summarizer用）
ARXIV_RSS_URLS=http://export.arxiv.org/rss/cs.AI,http://export.arxiv.org/rss/cs.LG

# Moderation Settings（Moderator用）
PERSPECTIVE_API_KEY=your_google_perspective_api_key
TOXICITY_THRESHOLD=0.7
```

## 📋 Step 7: 動作テスト

### 7.1 Bot起動

```bash
python start_paper_bot.py
```

### 7.2 Discord確認

1. **Botがオンライン**になることを確認
2. **任意のチャンネルで以下をテスト**：
   ```
   /ping
   /status
   ```

### 7.3 機能テスト

```
/check_papers     # Paper Summarizer
/review_latest    # Code Reviewer  
/train_ai         # Human-in-the-Loop
/analyze_message  # Moderator
```

## 🚨 トラブルシューティング

### Bot が起動しない

**症状**: `DISCORD_TOKEN が設定されていません`
**解決**: 
1. `.env`ファイルが存在するか確認
2. トークンが正しくコピーされているか確認
3. 余分なスペースがないか確認

### Bot がオフラインのまま

**症状**: Botがサーバーに表示されるがオフライン
**解決**:
1. Bot権限の「MESSAGE CONTENT INTENT」を確認
2. Botトークンを再生成
3. サーバーから一度Botを削除して再招待

### コマンドが応答しない

**症状**: `/ping`などが反応しない
**解決**:
1. Bot権限の「Use Slash Commands」を確認
2. サーバーIDが正しいか確認
3. Botを再起動

### チャンネルが見つからない

**症状**: `チャンネル "paper-summaries" が見つかりません`
**解決**:
1. チャンネル名のスペルを確認（ハイフン必須）
2. Botにチャンネル閲覧権限があるか確認
3. チャンネルが正しいサーバーにあるか確認

## ✅ 完了チェックリスト

- [ ] Discord Developer PortalでBot作成
- [ ] Botトークンを`.env`に設定
- [ ] Bot権限（MESSAGE CONTENT INTENT等）を有効化
- [ ] 必要なチャンネルを全て作成
- [ ] サーバーIDを`.env`に設定
- [ ] Botをサーバーに招待
- [ ] Webhook設定（GitHub連携用）
- [ ] 環境変数を全て設定
- [ ] Bot起動テスト成功
- [ ] `/ping`コマンドテスト成功

**🎉 全てチェックできたら、AI Forgeの準備完了です！**

---

**重要**: この設定を飛ばすとBotは絶対に動きません。一つずつ確実に実行してください。