# AI Forge セットアップガイド

このガイドでは、AI駆動開発コミュニティを段階的にセットアップする方法を説明します。

## 📋 前提条件

- Python 3.8 以上
- Discord アカウント
- GitHub アカウント
- OpenAI API キー (論文要約機能用)

## 🚀 Phase 1: 基本セットアップ

### 1. Discord Bot の作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. "New Application" をクリックして新しいアプリケーションを作成
3. アプリケーション名を入力（例: "AI Forge Bot"）
4. 左サイドバーの "Bot" をクリック
5. "Add Bot" をクリックしてボットユーザーを作成
6. "Token" をコピーして保存（これが `DISCORD_TOKEN` になります）

### 2. Discord サーバーの準備

1. Discord サーバーを作成または既存のサーバーを使用
2. 以下のチャンネルを作成：
   ```
   📋 ONBOARDING & INFO
   ├── #welcome-and-rules
   ├── #announcements
   └── #introduce-yourself
   
   💻 CORE DEVELOPMENT  
   ├── #general-dev
   ├── #dev-help
   ├── #code-review-queue
   └── #pair-programming
   
   🧠 AI RESEARCH & DISCUSSION
   ├── #paper-summaries  ← 重要！
   ├── #model-showcase
   ├── #dataset-discussion
   └── #ai-ethics
   ```

3. サーバー ID を取得：
   - Discord で開発者モードを有効化
   - サーバー名を右クリック → "ID をコピー"

### 3. Bot の権限設定

1. Discord Developer Portal で "OAuth2" → "URL Generator" に移動
2. Scopes で "bot" と "applications.commands" を選択
3. Bot Permissions で以下を選択：
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
   - Add Reactions
4. 生成された URL でボットをサーバーに招待

### 4. 環境設定

1. プロジェクトをクローン：
   ```bash
   git clone <your-repo-url>
   cd ai-dev-community
   ```

2. 仮想環境を作成：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 依存関係をインストール：
   ```bash
   pip install -r requirements.txt
   ```

4. 環境変数を設定：
   ```bash
   cp .env.example .env
   ```
   
   `.env` ファイルを編集して以下を設定：
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   DISCORD_GUILD_ID=your_server_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 5. 論文要約 Bot の起動

```bash
cd bots/paper_summarizer
python bot.py
```

Bot が正常に起動すると、以下のメッセージが表示されます：
```
INFO - PaperSummarizerBot がログインしました！
INFO - 要約チャンネルを見つけました: paper-summaries
INFO - 2 個のコマンドを同期しました (Guild)
```

## 🔗 Phase 2: GitHub 連携

### 1. GitHub Personal Access Token の作成

1. GitHub Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)" をクリック
3. 以下のスコープを選択：
   - `repo` (フルアクセス)
   - `admin:repo_hook` (Webhook 管理)
4. トークンをコピーして `.env` に追加

### 2. Discord Webhook の作成

1. Discord で通知を受け取りたいチャンネルを右クリック
2. "連携サービス" → "ウェブフックを作成"
3. 名前を設定（例: "GitHub Notifier"）
4. Webhook URL をコピーして `.env` に追加

### 3. GitHub Webhook の設定

```bash
cd webhooks
python github_setup.py
```

スクリプトを実行して "1. 新しい Webhook を作成" を選択

## 🧪 テスト

### 1. Bot のテスト

Discord で以下のコマンドを実行：
- `/ping` - Bot の応答をテスト
- `/status` - Bot のステータスを確認
- `/check_papers` - 手動で論文チェックを実行

### 2. GitHub 連携のテスト

1. リポジトリに何かをプッシュ
2. Discord チャンネルに通知が届くことを確認

## 🔧 トラブルシューティング

### Bot が起動しない場合

1. `.env` ファイルの設定を確認
2. Discord Token が正しいか確認
3. Bot がサーバーに招待されているか確認

### 論文要約が動作しない場合

1. OpenAI API キーが正しいか確認
2. `#paper-summaries` チャンネルが存在するか確認
3. Bot にチャンネルへの書き込み権限があるか確認

### GitHub 通知が届かない場合

1. Webhook URL が正しいか確認
2. GitHub Token の権限を確認
3. Discord チャンネルの権限を確認

## 📚 次のステップ

基本セットアップが完了したら、以下の機能を追加できます：

1. **AI コードレビュー Bot** - Pull Request を自動レビュー
2. **インテリジェントモデレーター** - 不適切なメッセージを検出
3. **ペアプログラミング・マッチャー** - 開発パートナーを自動マッチング

各機能の詳細な実装方法は、対応するドキュメントを参照してください。

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. ログファイルでエラーメッセージを確認
2. Discord Developer Portal でボットのステータスを確認
3. GitHub リポジトリの Issues で既知の問題を確認

それでも解決しない場合は、コミュニティの `#dev-help` チャンネルで質問してください！