"""
インテリジェントモデレーター Bot
Google Perspective API を使用してコミュニティを安全に保つ
"""

import os
import sys
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import discord
from discord.ext import commands, tasks
import aiohttp
from googleapiclient import discovery

# 親ディレクトリを import パスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_bot import BaseBot, BaseBotConfig, setup_base_bot

class ModeratorConfig(BaseBotConfig):
    """モデレーターBot の設定"""
    def __init__(self):
        super().__init__()
        self.perspective_api_key = os.getenv('PERSPECTIVE_API_KEY')
        self.toxicity_threshold = float(os.getenv('TOXICITY_THRESHOLD', '0.7'))
        self.mod_log_channel_name = 'mod-log'
        self.auto_delete_threshold = 0.9  # この値以上で自動削除
        self.warning_threshold = 0.7      # この値以上で警告

class ModerationDatabase:
    """モデレーションデータベース管理"""
    
    def __init__(self, db_path: str = "moderation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # モデレーションログテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                channel_name TEXT NOT NULL,
                message_id TEXT NOT NULL,
                message_content TEXT NOT NULL,
                toxicity_score REAL NOT NULL,
                action_taken TEXT NOT NULL,  -- 'none', 'warning', 'delete', 'timeout'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ユーザー警告テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                warning_count INTEGER DEFAULT 1,
                last_warning TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_toxicity_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 許可リストテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                user_name TEXT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_moderation(self, user_id: str, user_name: str, channel_id: str, channel_name: str,
                      message_id: str, message_content: str, toxicity_score: float, action: str):
        """モデレーションログを記録"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO moderation_logs 
            (user_id, user_name, channel_id, channel_name, message_id, message_content, toxicity_score, action_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, channel_id, channel_name, message_id, message_content, toxicity_score, action))
        
        conn.commit()
        conn.close()
    
    def add_warning(self, user_id: str, user_name: str, toxicity_score: float):
        """ユーザーに警告を追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 既存の警告をチェック
        cursor.execute('SELECT warning_count, total_toxicity_score FROM user_warnings WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            # 既存の警告を更新
            new_count = result[0] + 1
            new_total_score = result[1] + toxicity_score
            cursor.execute('''
                UPDATE user_warnings 
                SET warning_count = ?, total_toxicity_score = ?, last_warning = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_count, new_total_score, user_id))
        else:
            # 新しい警告を作成
            cursor.execute('''
                INSERT INTO user_warnings (user_id, user_name, warning_count, total_toxicity_score)
                VALUES (?, ?, 1, ?)
            ''', (user_id, user_name, toxicity_score))
        
        conn.commit()
        conn.close()
    
    def get_user_warnings(self, user_id: str) -> Dict:
        """ユーザーの警告情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT warning_count, total_toxicity_score, last_warning
            FROM user_warnings WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'warning_count': result[0],
                'total_toxicity_score': result[1],
                'last_warning': result[2]
            }
        return {'warning_count': 0, 'total_toxicity_score': 0.0, 'last_warning': None}
    
    def is_whitelisted(self, user_id: str) -> bool:
        """ユーザーが許可リストにいるかチェック"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM whitelist WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None

class PerspectiveAnalyzer:
    """Google Perspective API 分析エンジン"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.service = discovery.build(
            "commentanalyzer",
            "v1alpha1",
            developerKey=api_key,
            discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
            static_discovery=False,
        )
    
    async def analyze_message(self, message: str) -> Dict:
        """メッセージを分析"""
        if not message.strip():
            return {'TOXICITY': {'score': 0.0}}
        
        analyze_request = {
            'comment': {'text': message},
            'requestedAttributes': {
                'TOXICITY': {},
                'SEVERE_TOXICITY': {},
                'IDENTITY_ATTACK': {},
                'INSULT': {},
                'PROFANITY': {},
                'THREAT': {}
            },
            'languages': ['ja', 'en'],  # 日本語と英語をサポート
        }
        
        try:
            response = await asyncio.to_thread(
                self.service.comments().analyze(body=analyze_request).execute
            )
            
            scores = {}
            for attribute, data in response['attributeScores'].items():
                scores[attribute] = {
                    'score': data['summaryScore']['value'],
                    'span_scores': [span['score']['value'] for span in data.get('spanScores', [])]
                }
            
            return scores
            
        except Exception as e:
            print(f"Perspective API エラー: {e}")
            return {'TOXICITY': {'score': 0.0}}

class ModeratorBot(BaseBot):
    """モデレーターBot メインクラス"""
    
    def __init__(self):
        config = ModeratorConfig()
        super().__init__(config)
        
        self.db = ModerationDatabase()
        self.analyzer = PerspectiveAnalyzer(config.perspective_api_key) if config.perspective_api_key else None
        self.mod_log_channel = None
        
        # 定期的な統計レポートタスク
        if not self.daily_report_task.is_running():
            self.daily_report_task.start()
    
    async def on_ready(self):
        """Bot 起動時の処理"""
        await super().on_ready()
        
        # モデレーションログチャンネルを取得
        for guild in self.guilds:
            channel = discord.utils.get(guild.channels, name=self.config.mod_log_channel_name)
            if channel:
                self.mod_log_channel = channel
                self.logger.info(f'モデレーションログチャンネルを見つけました: {channel.name}')
                break
        
        if not self.mod_log_channel:
            self.logger.warning(f'モデレーションログチャンネル "{self.config.mod_log_channel_name}" が見つかりません')
    
    async def on_message(self, message):
        """メッセージ受信時の処理"""
        # Bot自身のメッセージは無視
        if message.author.bot:
            return
        
        # 許可リストのユーザーは無視
        if self.db.is_whitelisted(str(message.author.id)):
            return
        
        # 分析器が設定されていない場合は無視
        if not self.analyzer:
            return
        
        # メッセージを分析
        try:
            scores = await self.analyzer.analyze_message(message.content)
            toxicity_score = scores.get('TOXICITY', {}).get('score', 0.0)
            
            # 閾値チェック
            action_taken = 'none'
            
            if toxicity_score >= self.config.auto_delete_threshold:
                # 自動削除
                await message.delete()
                action_taken = 'delete'
                
                # ユーザーに警告を追加
                self.db.add_warning(str(message.author.id), message.author.display_name, toxicity_score)
                
                # 警告メッセージを送信
                warning_embed = discord.Embed(
                    title="⚠️ メッセージが削除されました",
                    description=f"{message.author.mention} あなたのメッセージは不適切な内容として削除されました。",
                    color=discord.Color.red()
                )
                warning_embed.add_field(name="理由", value="有害性スコアが高すぎます", inline=False)
                warning_embed.add_field(name="スコア", value=f"{toxicity_score:.2f}", inline=True)
                
                await message.channel.send(embed=warning_embed, delete_after=10)
                
            elif toxicity_score >= self.config.warning_threshold:
                # 警告のみ
                action_taken = 'warning'
                
                # リアクションで警告
                await message.add_reaction('⚠️')
                
                # ユーザーに警告を追加
                self.db.add_warning(str(message.author.id), message.author.display_name, toxicity_score)
            
            # ログに記録
            if toxicity_score >= self.config.warning_threshold:
                self.db.log_moderation(
                    str(message.author.id), message.author.display_name,
                    str(message.channel.id), message.channel.name,
                    str(message.id), message.content,
                    toxicity_score, action_taken
                )
                
                # モデレーションログに投稿
                await self.post_moderation_log(message, scores, action_taken)
        
        except Exception as e:
            self.logger.error(f"メッセージ分析エラー: {e}")
        
        # 他のコマンドも処理
        await self.process_commands(message)
    
    async def post_moderation_log(self, message, scores, action_taken):
        """モデレーションログを投稿"""
        if not self.mod_log_channel:
            return
        
        toxicity_score = scores.get('TOXICITY', {}).get('score', 0.0)
        
        # 色を決定
        if action_taken == 'delete':
            color = discord.Color.red()
            action_emoji = '🗑️'
        elif action_taken == 'warning':
            color = discord.Color.orange()
            action_emoji = '⚠️'
        else:
            color = discord.Color.yellow()
            action_emoji = '👀'
        
        embed = discord.Embed(
            title=f"{action_emoji} モデレーションアクション",
            color=color,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 ユーザー", value=message.author.mention, inline=True)
        embed.add_field(name="📍 チャンネル", value=message.channel.mention, inline=True)
        embed.add_field(name="🎯 アクション", value=action_taken, inline=True)
        
        embed.add_field(name="💬 メッセージ", value=message.content[:500], inline=False)
        
        # スコア詳細
        score_text = f"**毒性**: {toxicity_score:.3f}\n"
        for attr, data in scores.items():
            if attr != 'TOXICITY':
                score_text += f"**{attr}**: {data['score']:.3f}\n"
        
        embed.add_field(name="📊 分析スコア", value=score_text, inline=True)
        
        # ユーザーの警告履歴
        warnings = self.db.get_user_warnings(str(message.author.id))
        embed.add_field(
            name="📋 警告履歴",
            value=f"警告回数: {warnings['warning_count']}\n累計スコア: {warnings['total_toxicity_score']:.3f}",
            inline=True
        )
        
        await self.mod_log_channel.send(embed=embed)
    
    @tasks.loop(hours=24)  # 24時間ごとに実行
    async def daily_report_task(self):
        """日次レポートを生成"""
        if not self.mod_log_channel:
            return
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # 過去24時間の統計
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_actions,
                    COUNT(CASE WHEN action_taken = 'delete' THEN 1 END) as deletions,
                    COUNT(CASE WHEN action_taken = 'warning' THEN 1 END) as warnings,
                    AVG(toxicity_score) as avg_toxicity,
                    MAX(toxicity_score) as max_toxicity
                FROM moderation_logs 
                WHERE created_at >= datetime('now', '-1 day')
            ''')
            
            stats = cursor.fetchone()
            
            # トップ問題ユーザー
            cursor.execute('''
                SELECT user_name, COUNT(*) as violations, AVG(toxicity_score) as avg_score
                FROM moderation_logs 
                WHERE created_at >= datetime('now', '-1 day')
                GROUP BY user_id, user_name
                ORDER BY violations DESC, avg_score DESC
                LIMIT 5
            ''')
            
            top_violators = cursor.fetchall()
            conn.close()
            
            # レポート作成
            embed = discord.Embed(
                title="📊 日次モデレーションレポート",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="🎯 総アクション数", value=stats[0], inline=True)
            embed.add_field(name="🗑️ 削除数", value=stats[1], inline=True)
            embed.add_field(name="⚠️ 警告数", value=stats[2], inline=True)
            embed.add_field(name="📈 平均毒性スコア", value=f"{stats[3]:.3f}" if stats[3] else "0.000", inline=True)
            embed.add_field(name="🔥 最高毒性スコア", value=f"{stats[4]:.3f}" if stats[4] else "0.000", inline=True)
            
            if top_violators:
                violator_text = "\n".join([
                    f"{name}: {violations}回 (平均: {avg_score:.3f})"
                    for name, violations, avg_score in top_violators
                ])
                embed.add_field(name="👥 要注意ユーザー", value=violator_text, inline=False)
            
            await self.mod_log_channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"日次レポート生成エラー: {e}")

# コマンド群
class ModeratorCommands(commands.Cog):
    """モデレーション関連コマンド"""
    
    def __init__(self, bot: ModeratorBot):
        self.bot = bot
    
    @discord.app_commands.command(name="analyze_message", description="メッセージの毒性を分析")
    @discord.app_commands.describe(text="分析したいテキスト")
    async def analyze_message(self, interaction: discord.Interaction, text: str):
        """メッセージ分析コマンド"""
        await interaction.response.defer()
        
        if not self.bot.analyzer:
            await interaction.followup.send("❌ Perspective API キーが設定されていません")
            return
        
        try:
            scores = await self.bot.analyzer.analyze_message(text)
            
            embed = discord.Embed(
                title="🔍 メッセージ分析結果",
                description=f"**分析テキスト**: {text[:200]}",
                color=discord.Color.blue()
            )
            
            for attribute, data in scores.items():
                score = data['score']
                emoji = "🔴" if score > 0.7 else "🟡" if score > 0.3 else "🟢"
                embed.add_field(
                    name=f"{emoji} {attribute}",
                    value=f"{score:.3f}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ 分析エラー: {str(e)}")
    
    @discord.app_commands.command(name="user_warnings", description="ユーザーの警告履歴を表示")
    @discord.app_commands.describe(user="確認したいユーザー")
    async def user_warnings(self, interaction: discord.Interaction, user: discord.Member):
        """ユーザー警告履歴コマンド"""
        await interaction.response.defer()
        
        warnings = self.bot.db.get_user_warnings(str(user.id))
        
        embed = discord.Embed(
            title=f"📋 {user.display_name} の警告履歴",
            color=discord.Color.orange() if warnings['warning_count'] > 0 else discord.Color.green()
        )
        
        embed.add_field(name="⚠️ 警告回数", value=warnings['warning_count'], inline=True)
        embed.add_field(name="📊 累計毒性スコア", value=f"{warnings['total_toxicity_score']:.3f}", inline=True)
        
        if warnings['last_warning']:
            embed.add_field(name="📅 最終警告", value=warnings['last_warning'], inline=True)
        
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        
        await interaction.followup.send(embed=embed)
    
    @discord.app_commands.command(name="whitelist_user", description="ユーザーを許可リストに追加")
    @discord.app_commands.describe(user="許可リストに追加するユーザー", reason="理由")
    async def whitelist_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = "管理者による追加"):
        """ユーザー許可リスト追加コマンド"""
        # 管理者権限チェック
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ このコマンドを使用する権限がありません", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            conn = sqlite3.connect(self.bot.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO whitelist (user_id, user_name, reason)
                VALUES (?, ?, ?)
            ''', (str(user.id), user.display_name, reason))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ 許可リストに追加しました",
                description=f"{user.mention} を許可リストに追加しました",
                color=discord.Color.green()
            )
            embed.add_field(name="理由", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")

async def main():
    """メイン実行関数"""
    bot = ModeratorBot()
    
    # 基本機能をセットアップ
    await setup_base_bot(bot)
    
    # モデレーション関連コマンドを追加
    await bot.add_cog(ModeratorCommands(bot))
    
    # Bot を実行
    bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())