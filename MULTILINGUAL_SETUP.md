# 🌍 多言語対応セットアップガイド
# Multilingual Support Setup Guide

AI Forge Community は現在、以下の言語をサポートしています：
AI Forge Community now supports the following languages:

- 🇯🇵 日本語 (Japanese) - `ja`
- 🇺🇸 英語 (English) - `en` 
- 🇰🇷 韓国語 (Korean) - `ko`
- 🇨🇳 中文简体 (Chinese Simplified) - `zh-cn`

## 🚀 クイックスタート / Quick Start

### 言語設定コマンド / Language Setting Commands

```bash
# 現在の言語を確認 / Check current language
/language

# 言語を変更 / Change language
/language ja    # 日本語
/language en    # English
/language ko    # 한국어
/language zh-cn # 中文简体
```

## 🛠️ 技術仕様 / Technical Specifications

### ファイル構造 / File Structure

```
i18n/
├── locales.py              # 多言語システムコア
├── translations/
│   ├── ja.json            # 日本語翻訳
│   ├── en.json            # English translations
│   ├── ko.json            # 한국어 번역
│   └── zh-cn.json         # 中文简体翻译
```

### 対応ボット / Supported Bots

✅ **Base Bot** - 基本機能 / Basic functions
- Ping/Status commands
- Language settings
- Error messages

✅ **Paper Bot** - 論文要約 / Paper summarization
- Multi-language paper summaries
- Localized notifications

✅ **Moderator Bot** - モデレーション / Moderation
- Multi-language toxicity analysis
- Localized warning messages

🔄 **Code Review Bot** - コードレビュー / Code review (準備中 / In progress)

## 📝 開発者向け / For Developers

### 翻訳テキストの追加 / Adding Translation Text

1. `i18n/translations/` の各言語ファイルに翻訳を追加
   Add translations to each language file in `i18n/translations/`

2. コードで使用 / Use in code:
```python
from i18n.locales import _

# 基本的な使用 / Basic usage
message = _('bot.ready', language='ja', bot_name='MyBot')

# ユーザーの言語設定を使用 / Use user's language setting
user_lang = get_user_language(str(user.id))
message = _('commands.ping.response', language=user_lang, latency=42)
```

### 新しい言語の追加 / Adding New Languages

1. `i18n/locales.py` の `SupportedLanguages` に追加
2. `i18n/translations/[language_code].json` ファイルを作成
3. 翻訳を追加

## 🔧 設定 / Configuration

### 自動言語検出 / Automatic Language Detection

システムは以下の方法で言語を検出します：
The system detects language using:

- ユーザーの明示的な設定 / User's explicit setting
- テキスト内容からの自動検出 / Auto-detection from text content
- デフォルト言語（日本語）/ Default language (Japanese)

### データベース / Database

ユーザーの言語設定は `user_languages.db` に保存されます。
User language preferences are stored in `user_languages.db`.

## 🎯 使用例 / Usage Examples

### ユーザー向け / For Users

```bash
# 言語を英語に変更 / Change to English
/language en

# ボットの状態確認 / Check bot status
/status

# Ping テスト / Ping test
/ping
```

### 管理者向け / For Administrators

```bash
# モデレーション分析 / Moderation analysis
/analyze_message "This is a test message"

# ユーザー警告履歴 / User warning history
/user_warnings @username

# 許可リストに追加 / Add to whitelist
/whitelist_user @username "Trusted user"
```

## 🐛 トラブルシューティング / Troubleshooting

### よくある問題 / Common Issues

1. **翻訳が表示されない / Translations not showing**
   - 翻訳ファイルの JSON 形式を確認
   - Check JSON format in translation files

2. **言語設定が保存されない / Language setting not saved**
   - データベースの権限を確認
   - Check database permissions

3. **新しい言語が認識されない / New language not recognized**
   - `SupportedLanguages` enum に追加されているか確認
   - Check if added to `SupportedLanguages` enum

## 📚 参考資料 / References

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Python i18n Best Practices](https://docs.python.org/3/library/gettext.html)
- [JSON Format Guide](https://www.json.org/)

## 🤝 貢献 / Contributing

新しい言語の翻訳や改善提案は大歓迎です！
New language translations and improvement suggestions are welcome!

1. Fork the repository
2. Add your translations
3. Test with the multilingual system
4. Submit a pull request

---

**サポート / Support**: [GitHub Issues](https://github.com/daideguchi/ai-forge-community-clean/issues)