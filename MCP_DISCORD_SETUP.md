# 🔗 Discord MCP 連携セットアップ

AI ForgeコミュニティでDiscord MCPを使用して、私（AI）が直接Discordサーバーを操作できるようにする設定です。

## 🎯 機能

- **send-message**: Discordチャンネルにメッセージを送信
- **read-messages**: チャンネルの最新メッセージを読み取り
- **自動サーバー・チャンネル検出**
- **エラーハンドリング完備**

## 📋 前提条件

- Node.js 16.x 以上
- Discord Bot Token
- Kiro IDE（MCP対応）

## 🚀 セットアップ手順

### 1. Discord MCP のビルド

```bash
cd discordmcp
npm install
npm run build
```

### 2. Discord Bot Token 設定

`.kiro/settings/mcp.json` ファイルで設定：

```json
{
  "mcpServers": {
    "discord": {
      "command": "node",
      "args": ["/path/to/ai-dev-community/discordmcp/build/index.js"],
      "env": {
        "DISCORD_TOKEN": "YOUR_ACTUAL_DISCORD_BOT_TOKEN"
      },
      "disabled": false,
      "autoApprove": ["read-messages"]
    }
  }
}
```

### 3. Bot権限設定

Discord Botに以下の権限が必要：

```
✅ Read Messages/View Channels
✅ Send Messages  
✅ Read Message History
✅ Use Slash Commands
✅ Embed Links
✅ Add Reactions
```

### 4. Kiro IDE 再起動

MCP設定を反映するため、Kiro IDEを再起動してください。

## 🛠️ 使用方法

### メッセージ送信
```
チャンネル #general に「Hello from AI Forge!」というメッセージを送信してください
```

### メッセージ読み取り
```
#paper-summaries チャンネルの最新10件のメッセージを読み取ってください
```

### サーバー指定（複数サーバーの場合）
```
「AI Forge Community」サーバーの #announcements チャンネルにお知らせを投稿してください
```

## 🔧 利用可能なツール

### send-message
- **server** (オプション): サーバー名またはID
- **channel**: チャンネル名（例: "general"）またはID  
- **message**: 送信するメッセージ内容

### read-messages
- **server** (オプション): サーバー名またはID
- **channel**: チャンネル名（例: "general"）またはID
- **limit** (オプション): 取得するメッセージ数（デフォルト: 50、最大: 100）

## 🎯 AI Forge での活用例

### 1. コミュニティ管理
- 新メンバーへの歓迎メッセージ
- 重要なお知らせの投稿
- イベント告知

### 2. 開発サポート
- コードレビュー結果の共有
- 論文要約の投稿
- エラー報告とサポート

### 3. 自動化
- 定期的な統計レポート
- Bot稼働状況の報告
- コミュニティ活動の分析

## 🔒 セキュリティ

- **メッセージ送信は承認が必要**（autoApproveに含まれていない）
- **メッセージ読み取りは自動承認**（読み取り専用のため安全）
- **Bot権限は最小限に制限**
- **トークンは環境変数で管理**

## 🚨 トラブルシューティング

### Bot が応答しない
1. Discord Bot Token が正しく設定されているか確認
2. Bot がサーバーに招待されているか確認
3. Bot に必要な権限があるか確認

### チャンネルが見つからない
1. チャンネル名のスペルを確認
2. Bot がそのチャンネルにアクセス権限を持っているか確認
3. チャンネルIDを使用してみる

### MCP接続エラー
1. Kiro IDEを再起動
2. mcp.jsonの設定を確認
3. Node.jsのパスが正しいか確認

## 📞 サポート

問題が発生した場合：
1. Kiro IDEのMCP Server viewでステータス確認
2. Discord Developer PortalでBot設定確認
3. GitHub Issuesで報告

---

**🎉 これで私がDiscordサーバーを直接操作できるようになります！**

コミュニティの運営、メンバーサポート、自動化タスクなど、様々な場面で活用できます。