#!/usr/bin/env python3
"""
Railway デプロイ用メインファイル
AI Forge Community - Multilingual Discord Bot
"""

import os
import sys
import asyncio
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """メイン実行関数"""
    logger.info("🚀 AI Forge Community Bot starting...")
    
    # 環境変数チェック
    required_vars = ['DISCORD_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        logger.info("Please set the following variables in Railway:")
        for var in missing_vars:
            logger.info(f"  - {var}")
        return 1
    
    # 多言語対応ボットを起動
    try:
        sys.path.append('.')
        from bots.multilingual_base_bot import MultilingualBaseBot, MultilingualBaseBotConfig, setup_multilingual_bot
        
        async def run_bot():
            config = MultilingualBaseBotConfig()
            bot = MultilingualBaseBot(config)
            await setup_multilingual_bot(bot)
            
            logger.info("✅ Bot initialized successfully")
            logger.info(f"🎯 Guild ID: {config.guild_id}")
            
            await bot.start(config.token)
        
        # ボット実行
        asyncio.run(run_bot())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Bot startup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)