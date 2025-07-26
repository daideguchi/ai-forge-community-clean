# ⚡ AI Forge 即座セットアップガイド

**サンプル設定**で、APIキー設定後にDiscord設定のみで動作可能！

## 🎯 必要な作業（5分で完了）

### 1. Discord Bot作成（2分）

1. **Discord Developer Portal**にアクセス
   ```
   https://discord.com/developers/applications
   ```

2. **「New Application」** → 名前：`AI Forge Bot`

3. **「Bot」タブ** → **「Add Bot」**

4. **重要設定**：
   ```
   ✅ MESSAGE CONTENT INTENT: オン
   ✅ SERVER MEMBERS INTENT: オン  
   ✅ PRESENCE INTENT: オン
   ```

5. **Tokenをコピー**（後で使用）

### 2. Bot権限設定（1分）

1. **OAuth2** → **URL Generator**

2. **Scopes**: `bot`, `applications.commands`

3. **Bot Permissions**: 以下を全て選択
   ```
   ✅ Manage Roles        ✅ Send Messages
   ✅ Manage Channels      ✅ Embed Links  
   ✅ View Channels        ✅ Add Reactions
   ✅ Use Slash Commands   ✅ Read Message History
   ```

4. **生成されたURL**でBotを招待

### 3. Discord サーバー設定（2分）

**必須チャンネル**を作成：
```
📄 paper-summaries      ← 論文要約Bot用（重要！）
🔍 code-review-queue    ← コードレビューBot用
🧠 ai-training          ← AI学習Bot用
📋 mod-log              ← モデレーションBot用
```

**サーバーID取得**：
- 開発者モード有効化
- サーバー名右クリック → 「IDをコピー」

## 🚀 即座起動手順

### 1. 設定ファイル準備
```bash
# サンプル設定をコピー
cp .env.ready .env

# APIキー & Discord設定を編集
nano .env
```

### 2. 必要な設定を追加
`.env`ファイルで以下を変更：
```env
# Discord設定（必須）
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
DISCORD_GUILD_ID=YOUR_SERVER_ID_HERE

# APIキー設定（機能を使う場合）
OPENAI_API_KEY=your_actual_openai_key_here
PERSPECTIVE_API_KEY=your_actual_perspective_key_here
```

**💡 実際のAPIキーは API_KEYS_SETUP.md を参照して取得**

### 3. 即座起動
```bash
# 設定テスト
python test_api_keys.py

# Bot起動
python start_paper_bot.py
```

## ✅ 動作確認

Discord で以下をテスト：
```
/ping          # Bot応答確認
/status        # Bot情報表示
/check_papers  # 論文要約テスト
```

## 🎉 完了！

**これだけで AI Forge が完全動作します！**

### 利用可能な機能
- ✅ **論文要約Bot**: arXiv最新論文を自動要約
- ✅ **AIモデレーター**: 有害コンテンツ自動検出
- ✅ **Human-in-the-Loop**: コミュニティAI学習
- ⚠️ **コードレビューBot**: GitHub Token設定で有効化

### GitHub連携（オプション）
コードレビュー機能を使う場合：
1. GitHub Settings → Personal access tokens
2. `repo`, `admin:repo_hook` 権限でトークン作成
3. `.env`の`GITHUB_TOKEN`に設定

## 🆘 トラブル時

### Bot が起動しない
- Discord Token が正しいか確認
- MESSAGE CONTENT INTENT が有効か確認

### チャンネルエラー
- `#paper-summaries` チャンネルが存在するか確認
- Bot にチャンネル権限があるか確認

### API エラー
- `python test_api_keys.py` でエラー診断
- インターネット接続を確認

---

**🔥 サンプル設定を参考に、実際のAPIキーを設定すれば即座に動作します！**

**📝 実際のAPIキーは API_KEYS_SETUP.md を参照して取得してください**