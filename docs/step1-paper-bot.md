# Step 1: Paper Summarizer Bot セットアップガイド

このガイドでは、AI Forge の最初の機能である **Paper Summarizer Bot** を段階的にセットアップします。

## 🎯 このステップで実現すること

- arXiv から最新のAI論文を自動取得
- OpenAI GPT を使って論文を日本語で要約
- Discord の `#paper-summaries` チャンネルに自動投稿
- 手動での論文チェック機能

## 📋 前提条件

- Python 3.8 以上
- Discord アカウント
- OpenAI API アカウント

## 🚀 セットアップ手順

### 1. 環境確認

```bash
# セットアップスクリプトを実行
python setup_step1.py
```

このスクリプトが以下をチェックします：
- Python バージョン
- 必要なファイルの存在
- 依存関係のインストール状況

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. Discord Bot の作成

#### 3.1 Discord Developer Portal での設定

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. "New Application" をクリック
3. アプリケーション名を入力（例: "AI Forge Bot"）
4. 左サイドバーの "Bot" をクリック
5. "Add Bot" をクリック
6. **Token** をコピー（これが `DISCORD_TOKEN` になります）

#### 3.2 Bot の権限設定

1. "OAuth2" → "URL Generator" に移動
2. **Scopes** で以下を選択：
   - `bot`
   - `applications.commands`
3. **Bot Permissions** で以下を選択：
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
   - Add Reactions
4. 生成されたURLでBotをサーバーに招待

### 4. Discord サーバーの準備

#### 4.1 必要なチャンネルを作成

```
📚 AI RESEARCH & DISCUSSION
├── #paper-summaries  ← 重要！Paper Botが使用
├── #model-showcase
└── #ai-ethics
```

#### 4.2 サーバーIDの取得

1. Discord で開発者モードを有効化（設定 → 詳細設定 → 開発者モード）
2. サーバー名を右クリック → "IDをコピー"
3. これが `DISCORD_GUILD_ID` になります

### 5. OpenAI API の設定

1. [OpenAI Platform](https://platform.openai.com/) にアクセス
2. API キーを作成
3. これが `OPENAI_API_KEY` になります

### 6. 環境変数の設定

```bash
# .env ファイルを作成
cp .env.example .env
```

`.env` ファイルを編集：

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_server_id_here

# AI API Keys
OPENAI_API_KEY=your_openai_api_key_here

# RSS Feeds for Paper Summarizer
ARXIV_RSS_URLS=http://export.arxiv.org/rss/cs.AI,http://export.arxiv.org/rss/cs.LG
```

## 🧪 テスト実行

### 1. 基本機能テスト

```bash
python test_paper_bot.py
```

このテストで以下を確認：
- データベース機能
- RSS フィード取得
- AI 要約生成
- Discord Embed 形式

### 2. Bot 起動

```bash
python start_paper_bot.py
```

または直接：

```bash
python bots/paper_summarizer/bot.py
```

### 3. Discord でのテスト

Bot が起動したら、Discord で以下のコマンドをテスト：

```
/ping          # Bot の応答確認
/status        # Bot のステータス確認
/check_papers  # 手動で論文チェック
```

## 📊 動作確認

### 正常な動作の確認項目

1. **Bot がオンライン状態**
   - Discord でBot のステータスが緑色

2. **コマンドが応答**
   - `/ping` で応答が返る
   - `/status` でBot情報が表示される

3. **論文要約機能**
   - `/check_papers` で新しい論文が投稿される
   - `#paper-summaries` チャンネルに要約が表示される

4. **自動実行**
   - 6時間ごとに自動で新しい論文をチェック

### 期待される出力例

```
📄 新しい論文: Attention Is All You Need
🔗 https://arxiv.org/abs/1706.03762

🔬 研究概要: Transformerアーキテクチャを提案し、注意機構のみで...
💡 技術的貢献: RNNやCNNを使わずに注意機構だけで...
🚀 実用性: 自然言語処理タスクで高い性能を実現...
📊 結果: BLEU スコアで既存手法を上回る性能...

📝 著者: Ashish Vaswani, Noam Shazeer, ...
🔗 arXiv ID: 1706.03762
📅 公開日: 2017-06-12
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. Bot が起動しない

**症状**: `DISCORD_TOKEN が設定されていません`

**解決方法**:
- `.env` ファイルが存在するか確認
- Discord Developer Portal でトークンを再確認
- トークンに余分なスペースがないか確認

#### 2. 論文要約が生成されない

**症状**: `/check_papers` でエラーが発生

**解決方法**:
- OpenAI API キーが正しく設定されているか確認
- API の利用制限に達していないか確認
- インターネット接続を確認

#### 3. チャンネルが見つからない

**症状**: `要約チャンネル "paper-summaries" が見つかりません`

**解決方法**:
- Discord サーバーに `#paper-summaries` チャンネルを作成
- Bot にチャンネルへの書き込み権限があるか確認
- チャンネル名のスペルを確認

#### 4. RSS フィードエラー

**症状**: `RSS フィード処理エラー`

**解決方法**:
- インターネット接続を確認
- arXiv サーバーの状態を確認
- RSS URL が正しいか確認

## 📈 次のステップ

Paper Summarizer Bot が正常に動作したら：

1. **動作を観察**
   - 数時間〜1日動作させて安定性を確認
   - 論文要約の品質をチェック
   - コミュニティメンバーの反応を観察

2. **設定の調整**
   - RSS フィードの追加（他の分野の論文）
   - 要約の頻度調整
   - 要約の品質向上

3. **Step 2 への準備**
   - GitHub リポジトリの準備
   - Code Reviewer Bot のセットアップ

## 📚 参考資料

- [Discord.py ドキュメント](https://discordpy.readthedocs.io/)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [arXiv RSS フィード](https://arxiv.org/help/rss)

---

**🎉 おめでとうございます！**

Paper Summarizer Bot が動作すれば、AI Forge の最初の重要な機能が完成です。コミュニティメンバーは自動的に最新のAI研究動向を把握できるようになります。