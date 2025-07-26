"""
Base Discord Bot クラス
全ての Bot で共通する機能を提供
"""

import os
import asyncio
import logging
from typing import Optional
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class BaseBotConfig:
    """Bot の基本設定"""
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        self.guild_id = int(os.getenv('DISCORD_GUILD_ID', 0))
        self.command_prefix = '!'
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.guilds = True
        self.intents.guild_messages = True

class BaseBot(commands.Bot):
    """基本 Bot クラス"""
    
    def __init__(self, config: BaseBotConfig):
        super().__init__(
            command_prefix=config.command_prefix,
            intents=config.intents,
            help_command=None
        )
        self.config = config
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """ログ設定"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def on_ready(self):
        """Bot が起動した時の処理"""
        self.logger.info(f'{self.user} がログインしました！')
        self.logger.info(f'Guild ID: {self.config.guild_id}')
        
        # アプリケーションコマンドを同期
        try:
            if self.config.guild_id:
                guild = discord.Object(id=self.config.guild_id)
                synced = await self.tree.sync(guild=guild)
                self.logger.info(f'{len(synced)} 個のコマンドを同期しました (Guild)')
            else:
                synced = await self.tree.sync()
                self.logger.info(f'{len(synced)} 個のコマンドを同期しました (Global)')
        except Exception as e:
            self.logger.error(f'コマンド同期エラー: {e}')
    
    async def on_error(self, event, *args, **kwargs):
        """エラーハンドリング"""
        self.logger.error(f'エラーが発生しました: {event}', exc_info=True)
    
    def run_bot(self):
        """Bot を実行"""
        if not self.config.token:
            self.logger.error('DISCORD_TOKEN が設定されていません')
            return
            
        try:
            self.run(self.config.token)
        except Exception as e:
            self.logger.error(f'Bot の実行中にエラーが発生しました: {e}')

# 基本的なヘルスチェックコマンド
class HealthCommands(commands.Cog):
    """基本的なコマンド群"""
    
    def __init__(self, bot: BaseBot):
        self.bot = bot
    
    @discord.app_commands.command(name="ping", description="Bot の応答速度をチェック")
    async def ping(self, interaction: discord.Interaction):
        """Ping コマンド"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'🏓 Pong! レイテンシ: {latency}ms')
    
    @discord.app_commands.command(name="status", description="Bot のステータスを表示")
    async def status(self, interaction: discord.Interaction):
        """ステータスコマンド"""
        embed = discord.Embed(
            title="🤖 Bot ステータス",
            color=discord.Color.green()
        )
        embed.add_field(name="サーバー数", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="レイテンシ", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="バージョン", value="1.0.0", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup_base_bot(bot: BaseBot):
    """基本 Bot のセットアップ"""
    await bot.add_cog(HealthCommands(bot))
    return bot