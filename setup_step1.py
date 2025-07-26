#!/usr/bin/env python3
"""
AI Forge セットアップ Step 1: Paper Summarizer Bot
段階的セットアップの最初のステップ
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """必要な要件をチェック"""
    print("🔍 要件チェック中...")
    
    # Python バージョンチェック
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 以上が必要です")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # 必要なディレクトリの存在確認
    required_dirs = [
        "bots",
        "bots/paper_summarizer",
        "docs"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ ディレクトリが見つかりません: {dir_path}")
            return False
        print(f"✅ {dir_path}")
    
    # 必要なファイルの存在確認
    required_files = [
        "requirements.txt",
        ".env.example",
        "bots/base_bot.py",
        "bots/paper_summarizer/bot.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ ファイルが見つかりません: {file_path}")
            return False
        print(f"✅ {file_path}")
    
    return True

def setup_environment():
    """環境設定"""
    print("\n🔧 環境設定中...")
    
    # .env ファイルの確認
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("📝 .env.example から .env を作成してください:")
            print("   cp .env.example .env")
            print("   その後、.env ファイルを編集して必要な値を設定してください")
        else:
            print("❌ .env.example ファイルが見つかりません")
        return False
    
    # 環境変数の確認
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'DISCORD_TOKEN': 'Discord Bot のトークン',
        'DISCORD_GUILD_ID': 'Discord サーバーの ID',
        'OPENAI_API_KEY': 'OpenAI API キー (論文要約用)'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(f"{var}: {description}")
            print(f"❌ {var} が設定されていません")
        else:
            print(f"✅ {var} (設定済み)")
    
    if missing_vars:
        print("\n📝 以下の環境変数を .env ファイルに設定してください:")
        for var in missing_vars:
            print(f"   {var}")
        return False
    
    return True

def install_dependencies():
    """依存関係のインストール"""
    print("\n📦 依存関係のインストール...")
    
    try:
        import discord
        print("✅ discord.py がインストール済み")
    except ImportError:
        print("❌ discord.py がインストールされていません")
        print("   pip install -r requirements.txt を実行してください")
        return False
    
    try:
        import openai
        print("✅ openai がインストール済み")
    except ImportError:
        print("❌ openai がインストールされていません")
        return False
    
    try:
        import feedparser
        print("✅ feedparser がインストール済み")
    except ImportError:
        print("❌ feedparser がインストールされていません")
        return False
    
    return True

def create_discord_guide():
    """Discord セットアップガイドを表示"""
    print("\n🤖 Discord Bot セットアップガイド:")
    print("="*50)
    print("1. Discord Developer Portal にアクセス:")
    print("   https://discord.com/developers/applications")
    print()
    print("2. 'New Application' をクリック")
    print("   名前: AI Forge Bot (または任意の名前)")
    print()
    print("3. 左サイドバーの 'Bot' をクリック")
    print("   'Add Bot' をクリック")
    print()
    print("4. Token をコピーして .env の DISCORD_TOKEN に設定")
    print("   ⚠️  トークンは秘密情報です。共有しないでください")
    print()
    print("5. Bot Permissions (OAuth2 > URL Generator):")
    print("   Scopes: bot, applications.commands")
    print("   Bot Permissions:")
    print("   - Send Messages")
    print("   - Use Slash Commands") 
    print("   - Embed Links")
    print("   - Read Message History")
    print("   - Add Reactions")
    print()
    print("6. 生成されたURLでBotをサーバーに招待")
    print()
    print("7. Discord サーバーに以下のチャンネルを作成:")
    print("   #paper-summaries (論文要約Bot用)")
    print()
    print("8. サーバーIDを取得:")
    print("   Discord で開発者モードを有効化")
    print("   サーバー名を右クリック > 'IDをコピー'")
    print("   .env の DISCORD_GUILD_ID に設定")

def main():
    """メイン実行関数"""
    print("🚀 AI Forge セットアップ - Step 1: Paper Summarizer Bot")
    print("="*60)
    
    # 要件チェック
    if not check_requirements():
        print("\n❌ 要件チェックに失敗しました")
        return
    
    # 依存関係チェック
    if not install_dependencies():
        print("\n❌ 依存関係のインストールが必要です")
        print("実行してください: pip install -r requirements.txt")
        return
    
    # 環境設定チェック
    if not setup_environment():
        print("\n❌ 環境設定が不完全です")
        create_discord_guide()
        return
    
    print("\n✅ Step 1 の準備が完了しました！")
    print("\n🎯 次のステップ:")
    print("1. テスト実行: python test_paper_bot.py")
    print("2. Bot 起動: python bots/paper_summarizer/bot.py")
    print("3. Discord で /ping コマンドをテスト")
    print("4. Discord で /check_papers コマンドをテスト")
    print("\n📚 詳細なガイド: docs/setup-guide.md")

if __name__ == "__main__":
    main()