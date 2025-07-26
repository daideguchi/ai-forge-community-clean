#!/usr/bin/env python3
"""
Paper Summarizer Bot 起動スクリプト
エラーハンドリングとログ出力を含む安全な起動
"""

import asyncio
import sys
import os
from pathlib import Path

# パスを追加
sys.path.append('bots')

def check_environment():
    """環境チェック"""
    print("🔍 環境チェック中...")
    
    # 必要なファイルの確認
    required_files = [
        '.env',
        'bots/base_bot.py',
        'bots/paper_summarizer/bot.py'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ 必要なファイルが見つかりません: {file_path}")
            return False
    
    # 環境変数の確認
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DISCORD_TOKEN', 'DISCORD_GUILD_ID', 'OPENAI_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ 環境変数が設定されていません: {var}")
            return False
    
    print("✅ 環境チェック完了")
    return True

async def start_bot():
    """Bot を起動"""
    try:
        from bots.paper_summarizer.bot import main
        print("🚀 Paper Summarizer Bot を起動中...")
        await main()
    except KeyboardInterrupt:
        print("\n⏹️  Bot を停止しています...")
    except Exception as e:
        print(f"❌ Bot 起動エラー: {e}")
        import traceback
        traceback.print_exc()

def main():
    """メイン関数"""
    print("📄 AI Forge - Paper Summarizer Bot")
    print("=" * 40)
    
    # 環境チェック
    if not check_environment():
        print("\n❌ 環境設定を確認してください")
        print("ヘルプ: python setup_step1.py")
        return
    
    print("\n🎯 Bot を起動します...")
    print("停止するには Ctrl+C を押してください\n")
    
    # Bot を起動
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot を停止しました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")

if __name__ == "__main__":
    main()