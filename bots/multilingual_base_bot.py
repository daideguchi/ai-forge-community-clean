#!/usr/bin/env python3
"""
多言語対応 Base Discord Bot
Enhanced base bot with internationalization support
"""

import os
import sys
import asyncio
import logging
import sqlite3
from typing import Optional, Dict
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 多言語対応システムを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from i18n.locales import i18n, _, get_user_language, set_user_language, SupportedLanguages

# 環境変数を読み込み
load_dotenv()

class UserLanguageDatabase:
    """ユーザー言語設定データベース"""
    
    def __init__(self, db_path: str = "user_languages.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_languages (
                user_id TEXT PRIMARY KEY,
                language_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_language(self, user_id: str) -> str:
        """ユーザーの言語設定を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT language_code FROM user_languages WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        return "ja"  # デフォルトは日本語
    
    def set_user_language(self, user_id: str, language_code: str) -> bool:
        """ユーザーの言語設定を保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_languages (user_id, language_code, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, language_code))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"言語設定保存エラー: {e}")
            return False

# グローバルデータベースインスタンス
user_lang_db = UserLanguageDatabase()

def get_user_language_from_db(user_id: str) -> str:
    """データベースからユーザーの言語設定を取得"""
    return user_lang_db.get_user_language(user_id)

def set_user_language_to_db(user_id: str, language_code: str) -> bool:
    """データベースにユーザーの言語設定を保存"""
    return user_lang_db.set_user_language(user_id, language_code)

class MultilingualBaseBotConfig:
    """多言語対応Bot の基本設定"""
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        self.guild_id = int(os.getenv('DISCORD_GUILD_ID', 0))
        self.command_prefix = '!'
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.guilds = True
        self.intents.guild_messages = True

class MultilingualBaseBot(commands.Bot):
    """多言語対応基本 Bot クラス"""
    
    def __init__(self, config: MultilingualBaseBotConfig):
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
        self.logger.info(_('bot.ready', bot_name=self.user))
        self.logger.info(_('bot.guild_id', guild_id=self.config.guild_id))
        
        # アプリケーションコマンドを同期
        try:
            if self.config.guild_id:
                guild = discord.Object(id=self.config.guild_id)
                synced = await self.tree.sync(guild=guild)
                self.logger.info(_('bot.commands_synced_guild', count=len(synced)))
            else:
                synced = await self.tree.sync()
                self.logger.info(_('bot.commands_synced_global', count=len(synced)))
        except Exception as e:
            self.logger.error(_('bot.command_sync_error', error=e))
    
    async def on_error(self, event, *args, **kwargs):
        """エラーハンドリング"""
        self.logger.error(_('bot.error_occurred', event=event), exc_info=True)
    
    def run_bot(self):
        """Bot を実行"""
        if not self.config.token:
            self.logger.error(_('bot.token_missing'))
            return
            
        try:
            self.run(self.config.token)
        except Exception as e:
            self.logger.error(_('bot.execution_error', error=e))

# 多言語対応コマンド群
class MultilingualCommands(commands.Cog):
    """多言語対応基本コマンド群"""
    
    def __init__(self, bot: MultilingualBaseBot):
        self.bot = bot
    
    @discord.app_commands.command(name="ping", description="Check bot response time / Bot の応答速度をチェック")
    async def ping(self, interaction: discord.Interaction):
        """Ping コマンド"""
        user_lang = get_user_language_from_db(str(interaction.user.id))
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(_('commands.ping.response', language=user_lang, latency=latency))
    
    @discord.app_commands.command(name="status", description="Display bot status / Bot のステータスを表示")
    async def status(self, interaction: discord.Interaction):
        """ステータスコマンド"""
        user_lang = get_user_language_from_db(str(interaction.user.id))
        embed = discord.Embed(
            title=_('commands.status.title', language=user_lang),
            color=discord.Color.green()
        )
        embed.add_field(name=_('commands.status.servers', language=user_lang), value=len(self.bot.guilds), inline=True)
        embed.add_field(name=_('commands.status.latency', language=user_lang), value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name=_('commands.status.version', language=user_lang), value="1.0.0", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="language", description="Change language settings / 言語設定を変更")
    @discord.app_commands.describe(language="Language code (ja, en, ko, zh-cn) / 言語コード")
    async def set_language(self, interaction: discord.Interaction, language: str = None):
        """言語設定コマンド"""
        current_lang = get_user_language_from_db(str(interaction.user.id))
        
        if language is None:
            # 現在の言語を表示
            lang_name = i18n.get_language_name(current_lang, current_lang)
            await interaction.response.send_message(
                _('commands.language.current', language=current_lang).format(language=lang_name)
            )
            return
        
        # サポートされている言語かチェック
        supported_langs = [lang.value for lang in SupportedLanguages]
        if language not in supported_langs:
            await interaction.response.send_message(
                _('commands.language.invalid', language=current_lang, languages=', '.join(supported_langs)),
                ephemeral=True
            )
            return
        
        # 言語を設定
        if set_user_language_to_db(str(interaction.user.id), language):
            lang_name = i18n.get_language_name(language, language)
            await interaction.response.send_message(
                _('commands.language.changed', language=language).format(language=lang_name)
            )
        else:
            await interaction.response.send_message(
                _('errors.database_error', language=current_lang, error="Failed to save language setting"),
                ephemeral=True
            )

async def setup_multilingual_bot(bot: MultilingualBaseBot):
    """多言語対応 Bot のセットアップ"""
    await bot.add_cog(MultilingualCommands(bot))
    return bot

if __name__ == "__main__":
    async def main():
        """テスト実行"""
        config = MultilingualBaseBotConfig()
        bot = MultilingualBaseBot(config)
        await setup_multilingual_bot(bot)
        bot.run_bot()
    
    asyncio.run(main())