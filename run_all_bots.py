#!/usr/bin/env python3
"""
全Bot統合起動スクリプト
全てのBotを同時に起動・管理
"""

import asyncio
import sys
import os
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

# パスを追加
sys.path.append('bots')

class BotManager:
    """Bot管理クラス"""
    
    def __init__(self):
        self.bots = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def check_environment(self):
        """環境チェック"""
        print("🔍 環境チェック中...")
        
        # 必要なファイルの確認
        required_files = [
            '.env',
            'bots/base_bot.py',
            'bots/paper_summarizer/bot.py',
            'bots/code_reviewer/bot.py',
            'bots/human_in_loop/bot.py',
            'bots/moderator/bot.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ 以下のファイルが見つかりません:")
            for file in missing_files:
                print(f"   {file}")
            return False
        
        # 環境変数の確認
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['DISCORD_TOKEN', 'DISCORD_GUILD_ID']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print("❌ 以下の環境変数が設定されていません:")
            for var in missing_vars:
                print(f"   {var}")
            return False
        
        print("✅ 環境チェック完了")
        return True
    
    async def start_bot(self, bot_name: str, bot_module: str):
        """個別Botを起動"""
        try:
            print(f"🚀 {bot_name} を起動中...")
            
            # 動的にモジュールをインポート
            module = __import__(bot_module, fromlist=['main'])
            await module.main()
            
        except Exception as e:
            print(f"❌ {bot_name} 起動エラー: {e}")
    
    async def start_all_bots(self):
        """全Botを並行起動"""
        self.running = True
        
        # 起動するBot一覧
        bots_to_start = [
            ("Paper Summarizer", "bots.paper_summarizer.bot"),
            ("Code Reviewer", "bots.code_reviewer.bot"),
            ("Human-in-the-Loop", "bots.human_in_loop.bot"),
            ("Moderator", "bots.moderator.bot")
        ]
        
        # 利用可能なBotのみ起動
        available_bots = []
        for bot_name, bot_module in bots_to_start:
            try:
                __import__(bot_module, fromlist=['main'])
                available_bots.append((bot_name, bot_module))
                print(f"✅ {bot_name} - 利用可能")
            except ImportError as e:
                print(f"⚠️  {bot_name} - スキップ (モジュールなし)")
            except Exception as e:
                print(f"❌ {bot_name} - エラー: {e}")
        
        if not available_bots:
            print("❌ 起動可能なBotがありません")
            return
        
        print(f"\n🎯 {len(available_bots)} 個のBotを並行起動します...")
        
        # 並行実行
        tasks = []
        for bot_name, bot_module in available_bots:
            task = asyncio.create_task(self.start_bot(bot_name, bot_module))
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n⏹️  全Botを停止中...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        print(f"\n📡 シグナル {signum} を受信しました")
        self.running = False

async def main():
    """メイン実行関数"""
    print("🤖 AI Forge - 全Bot統合起動システム")
    print("=" * 50)
    
    manager = BotManager()
    
    # シグナルハンドラを設定
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    # 環境チェック
    if not manager.check_environment():
        print("\n❌ 環境設定を確認してください")
        print("ヘルプ: python setup_step1.py")
        return
    
    print("\n🎯 全Botを起動します...")
    print("停止するには Ctrl+C を押してください\n")
    
    try:
        await manager.start_all_bots()
    except KeyboardInterrupt:
        print("\n👋 全Botを停止しました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了しました")