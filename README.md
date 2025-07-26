# AI Forge - AI駆動開発コミュニティ

Discord と Git を連携させた AI 駆動開発コミュニティの構築プロジェクトです。

## 🚀 プロジェクト概要

このプロジェクトは段階的に以下の機能を実装していきます：

### Phase 1: 基盤構築 ✅
- [x] プロジェクト構造の作成
- [x] GitHub → Discord Webhook 通知
- [x] 基本的な Discord Bot セットアップ

### Phase 2: AI サービス ✅
- [x] 論文要約 RSS Bot
- [x] AI コードレビュー Bot
- [x] インテリジェントモデレーター
- [x] Human-in-the-Loop Bot (RLHF基盤)

### Phase 3: 高度な自動化
- [ ] IssueOps システム
- [ ] ペアプログラミング・マッチャー
- [ ] ハッカソン管理 Bot

### Phase 4: 未来のビジョン
- [ ] 分散型 AI ネットワーク
- [ ] RLHF コミュニティモデル
- [ ] AI エージェント実験場

## 📁 プロジェクト構造

```
ai-dev-community/
├── bots/                    # Discord Bot 実装
│   ├── paper-summarizer/    # 論文要約 Bot
│   ├── code-reviewer/       # コードレビュー Bot
│   └── moderator/          # モデレーション Bot
├── webhooks/               # Webhook 設定とスクリプト
├── github-actions/         # GitHub Actions ワークフロー
├── docs/                   # ドキュメント
└── config/                 # 設定ファイル
```

## 🛠️ 技術スタック

- **Discord Bot**: Python (discord.py)
- **AI/ML**: OpenAI API, Anthropic Claude
- **データベース**: SQLite (開発), PostgreSQL (本番)
- **CI/CD**: GitHub Actions
- **インフラ**: Docker, Railway/Heroku

## ⚡ 即座セットアップ（5分で完了）

**サンプル設定**で、APIキー設定後にDiscord設定のみで動作！

```bash
# 1. リポジトリをクローン
git clone https://github.com/daideguchi/ai-forge-community.git
cd ai-forge-community

# 2. 依存関係をインストール
pip install -r requirements.txt

# 3. サンプル設定をコピー
cp .env.ready .env

# 4. Discord Bot作成 & 設定（INSTANT_SETUP.md参照）
# - Bot Token取得
# - 必須チャンネル作成（#paper-summaries等）
# - .envにToken/ServerID設定

# 5. 即座起動
python test_api_keys.py  # 設定確認
python start_paper_bot.py  # Bot起動
```

## 🚀 通常セットアップ

```bash
# 設定ガイド確認
python quick_start.py

# Discord & API設定（重要！）
# 📖 DISCORD_SETUP.md - Discord完全設定
# 🔑 API_KEYS_SETUP.md - APIキー取得

# 設定テスト & Bot起動
python test_api_keys.py
python start_paper_bot.py
```

## 📚 セットアップガイド

| ガイド | 内容 | 所要時間 | 推奨度 |
|--------|------|----------|--------|
| [⚡ INSTANT_SETUP.md](INSTANT_SETUP.md) | **即座セットアップ（APIキー設定済み）** | **5分** | **推奨** |
| [✅ COMPLETE_SETUP_CHECKLIST.md](COMPLETE_SETUP_CHECKLIST.md) | 完全チェックリスト | 30分 | 初心者向け |
| [📖 DISCORD_SETUP.md](DISCORD_SETUP.md) | Discord Bot作成・サーバー設定 | 15分 | 必須 |
| [🔑 API_KEYS_SETUP.md](API_KEYS_SETUP.md) | 全APIキー取得方法 | 20分 | 自分で設定する場合 |
| [🚀 DEPLOYMENT.md](DEPLOYMENT.md) | 本番環境デプロイ | 60分 | 本格運用時 |

## 🌐 リポジトリ

**GitHub**: https://github.com/daideguchi/ai-forge-community

## 🎯 2つの選択肢

### ⚡ 即座に試したい場合
- **INSTANT_SETUP.md** を使用
- サンプル設定で5分で動作
- APIキー + Discord設定が必要
- **実際のキーは個別に取得が必要**

### 🔧 完全に理解して設定したい場合  
- **COMPLETE_SETUP_CHECKLIST.md** を使用
- 全工程を理解しながら設定
- 自分のAPIキーで完全構築

## ⚠️ 重要な注意

**Discord設定は必須です！**
- Bot作成・招待
- 必須チャンネル作成（#paper-summaries等）
- サーバーID取得

これを飛ばすとBotは動きません。

## 📋 詳細セットアップ

- **Step 1**: [Paper Summarizer Bot](docs/step1-paper-bot.md)
- **Step 2**: [Code Reviewer Bot](docs/setup-guide.md)
- **Step 3**: [Human-in-the-Loop Bot](docs/setup-guide.md)
- **Step 4**: [Moderator Bot](docs/setup-guide.md)

## 🤝 コントリビューション

このプロジェクトはコミュニティ駆動で開発されています。貢献方法については [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。