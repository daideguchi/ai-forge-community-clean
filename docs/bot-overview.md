# 🤖 AI Forge Bot エコシステム概要

AI Forge は複数の専門化されたBotが協調して動作するエコシステムです。各Botは独立して動作しながら、コミュニティの異なる側面を支援します。

## 🧠 Bot アーキテクチャ

### 基盤クラス: `BaseBot`
全てのBotが継承する共通基盤
- Discord接続管理
- 基本コマンド（ping, status）
- エラーハンドリング
- ログ管理

## 📚 実装済みBot一覧

### 1. 📄 Paper Summarizer Bot
**目的**: 最新のAI研究動向をコミュニティに提供

**主な機能**:
- arXiv RSS フィードの自動監視
- 新しい論文の AI 要約生成
- `#paper-summaries` チャンネルへの自動投稿
- 手動チェック機能（`/check_papers`）

**技術スタック**:
- OpenAI GPT-3.5-turbo (要約生成)
- feedparser (RSS解析)
- SQLite (重複防止)

**設定**:
```env
OPENAI_API_KEY=your_key
ARXIV_RSS_URLS=http://export.arxiv.org/rss/cs.AI,http://export.arxiv.org/rss/cs.LG
```

### 2. 🔍 Code Reviewer Bot
**目的**: Pull Request の自動レビューで開発品質向上

**主な機能**:
- GitHub PR の差分解析
- AI による包括的コードレビュー
- Discord での結果共有
- GitHub Actions 連携

**技術スタック**:
- OpenAI GPT-4 (高品質レビュー)
- PyGithub (GitHub API)
- GitHub Actions (自動トリガー)

**コマンド**:
- `/review_pr <番号>` - 特定PRをレビュー
- `/review_latest` - 最新PRをレビュー
- `/list_prs` - オープンPR一覧

### 3. 🧠 Human-in-the-Loop Bot
**目的**: コミュニティ主導のAIモデル改善（RLHF基盤）

**主な機能**:
- AI応答の複数生成（異なるモデル・温度）
- コミュニティからのフィードバック収集
- 学習データの自動生成
- 統計レポート機能

**ワークフロー**:
1. プロンプト投稿 → 複数AI応答生成
2. コミュニティがリアクション（👍👎❤️🤔）
3. フィードバック集計 → 学習データ化
4. エクスポート機能でモデル学習に活用

**コマンド**:
- `/train_ai <プロンプト>` - 学習プロンプト投稿
- `/feedback_stats` - フィードバック統計
- `/export_training_data` - 学習データエクスポート

### 4. 🛡️ Moderator Bot
**目的**: コミュニティの安全性維持

**主な機能**:
- Google Perspective API による毒性検出
- 自動メッセージ削除（高毒性）
- 警告システム（累積管理）
- 許可リスト機能
- 日次レポート生成

**閾値設定**:
- `0.9以上`: 自動削除 + 警告
- `0.7以上`: 警告リアクション
- `0.7未満`: 監視のみ

**コマンド**:
- `/analyze_message <テキスト>` - 毒性分析
- `/user_warnings <ユーザー>` - 警告履歴
- `/whitelist_user <ユーザー>` - 許可リスト追加

## 🔄 Bot間の連携

### データ共有
- 各Botは独立したSQLiteデータベースを使用
- 本番環境では共通PostgreSQLに接続可能

### チャンネル分担
```
#paper-summaries     → Paper Summarizer
#code-review-queue   → Code Reviewer  
#ai-training         → Human-in-the-Loop
#mod-log            → Moderator
```

### イベント連携
- GitHub Webhook → Code Reviewer → Discord通知
- 定期タスク → Paper Summarizer → 新論文通知
- メッセージ監視 → Moderator → 安全性確保

## 🚀 デプロイメント

### 開発環境
```bash
# 個別Bot起動
python bots/paper_summarizer/bot.py
python bots/code_reviewer/bot.py
python bots/human_in_loop/bot.py
python bots/moderator/bot.py
```

### 本番環境
```bash
# Docker Compose で全Bot起動
docker-compose up -d
```

## 📊 監視・メトリクス

### ログ出力
- 各Botは構造化ログを出力
- エラー・警告・情報レベルで分類
- 本番環境では集約ログシステムに送信

### ヘルスチェック
- `/ping` - 基本応答確認
- `/status` - Bot状態詳細
- Docker healthcheck 対応

## 🔮 将来の拡張

### Phase 3: 高度な自動化
- **IssueOps Bot**: Git駆動のコミュニティ管理
- **Pair Programming Matcher**: 開発パートナー自動マッチング
- **Hackathon Manager**: イベント運営自動化

### Phase 4: 未来のビジョン
- **分散型AIネットワーク**: Petals統合
- **コミュニティ所有モデル**: RLHF完全実装
- **AIエージェント実験場**: LangChain統合

## 🛠️ 開発ガイドライン

### 新しいBot追加手順
1. `bots/new_bot/` ディレクトリ作成
2. `BaseBot` を継承したメインクラス実装
3. `Dockerfile` 作成
4. `docker-compose.yml` にサービス追加
5. テスト実装
6. ドキュメント更新

### コード品質
- Black フォーマッター使用
- 型ヒント必須
- 非同期処理推奨
- エラーハンドリング徹底

この設計により、AI Forge は段階的に成長し、最終的にはコミュニティ自体がAIを共同創造する「真のAI鍛冶場」となります。