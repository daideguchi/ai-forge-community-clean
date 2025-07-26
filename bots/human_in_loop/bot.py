"""
Human-in-the-Loop Bot
コミュニティメンバーからのフィードバックを収集してAIモデルを改善
RLHF (Reinforcement Learning from Human Feedback) の基盤
"""

import os
import sys
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import discord
from discord.ext import commands, tasks
import openai
import random

# 親ディレクトリを import パスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_bot import BaseBot, BaseBotConfig, setup_base_bot

class HumanInLoopConfig(BaseBotConfig):
    """Human-in-the-Loop Bot の設定"""
    def __init__(self):
        super().__init__()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.feedback_channel_name = 'ai-training'
        self.min_responses_per_prompt = 3  # プロンプトあたりの最小応答数
        self.feedback_collection_hours = 24  # フィードバック収集時間

class FeedbackDatabase:
    """フィードバックデータベース管理"""
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # プロンプトテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_text TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                discord_message_id TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # AI応答テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                response_text TEXT NOT NULL,
                model_name TEXT NOT NULL,
                temperature REAL DEFAULT 0.7,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id)
            )
        ''')
        
        # 人間フィードバックテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS human_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                response_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL,  -- 'like', 'dislike', 'comment'
                feedback_value TEXT,  -- リアクション名やコメント内容
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id),
                FOREIGN KEY (response_id) REFERENCES ai_responses (id)
            )
        ''')
        
        # 学習データテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_text TEXT NOT NULL,
                chosen_response TEXT NOT NULL,
                rejected_responses TEXT NOT NULL,  -- JSON形式
                feedback_score REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prompt(self, prompt_text: str, category: str, discord_message_id: str = None) -> int:
        """プロンプトを保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prompts (prompt_text, category, discord_message_id)
            VALUES (?, ?, ?)
        ''', (prompt_text, category, discord_message_id))
        
        prompt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prompt_id
    
    def save_ai_response(self, prompt_id: int, response_text: str, model_name: str, temperature: float = 0.7) -> int:
        """AI応答を保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_responses (prompt_id, response_text, model_name, temperature)
            VALUES (?, ?, ?, ?)
        ''', (prompt_id, response_text, model_name, temperature))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return response_id
    
    def save_feedback(self, prompt_id: int, response_id: int, user_id: str, user_name: str, 
                     feedback_type: str, feedback_value: str = None):
        """フィードバックを保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO human_feedback (prompt_id, response_id, user_id, user_name, feedback_type, feedback_value)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (prompt_id, response_id, user_id, user_name, feedback_type, feedback_value))
        
        conn.commit()
        conn.close()
    
    def get_feedback_summary(self, prompt_id: int) -> Dict:
        """プロンプトのフィードバック集計"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ar.id, ar.response_text, ar.model_name,
                   COUNT(CASE WHEN hf.feedback_type = 'like' THEN 1 END) as likes,
                   COUNT(CASE WHEN hf.feedback_type = 'dislike' THEN 1 END) as dislikes,
                   COUNT(CASE WHEN hf.feedback_type = 'comment' THEN 1 END) as comments
            FROM ai_responses ar
            LEFT JOIN human_feedback hf ON ar.id = hf.response_id
            WHERE ar.prompt_id = ?
            GROUP BY ar.id
            ORDER BY likes DESC, dislikes ASC
        ''', (prompt_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        responses = []
        for row in results:
            responses.append({
                'response_id': row[0],
                'response_text': row[1],
                'model_name': row[2],
                'likes': row[3],
                'dislikes': row[4],
                'comments': row[5],
                'score': row[3] - row[4]  # 簡単なスコア計算
            })
        
        return responses
    
    def generate_training_data(self, prompt_id: int):
        """学習データを生成"""
        responses = self.get_feedback_summary(prompt_id)
        
        if len(responses) < 2:
            return None
        
        # 最高スコアの応答を選択
        chosen = max(responses, key=lambda x: x['score'])
        rejected = [r for r in responses if r['response_id'] != chosen['response_id']]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # プロンプトテキストを取得
        cursor.execute('SELECT prompt_text FROM prompts WHERE id = ?', (prompt_id,))
        prompt_text = cursor.fetchone()[0]
        
        # 学習データを保存
        cursor.execute('''
            INSERT INTO training_data (prompt_text, chosen_response, rejected_responses, feedback_score)
            VALUES (?, ?, ?, ?)
        ''', (
            prompt_text,
            chosen['response_text'],
            json.dumps([r['response_text'] for r in rejected]),
            chosen['score']
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'prompt': prompt_text,
            'chosen': chosen['response_text'],
            'rejected': [r['response_text'] for r in rejected],
            'score': chosen['score']
        }

class AIResponseGenerator:
    """AI応答生成エンジン"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.models = ['gpt-3.5-turbo', 'gpt-4']
        self.temperatures = [0.3, 0.7, 1.0]
    
    async def generate_responses(self, prompt: str, num_responses: int = 3) -> List[Dict]:
        """複数の応答を生成"""
        responses = []
        
        for i in range(num_responses):
            model = random.choice(self.models)
            temperature = random.choice(self.temperatures)
            
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=temperature
                )
                
                responses.append({
                    'text': response.choices[0].message.content.strip(),
                    'model': model,
                    'temperature': temperature
                })
                
                # レート制限対策
                await asyncio.sleep(1)
                
            except Exception as e:
                responses.append({
                    'text': f"応答生成エラー: {str(e)}",
                    'model': model,
                    'temperature': temperature
                })
        
        return responses

class HumanInLoopBot(BaseBot):
    """Human-in-the-Loop Bot メインクラス"""
    
    def __init__(self):
        config = HumanInLoopConfig()
        super().__init__(config)
        
        self.db = FeedbackDatabase()
        self.ai_generator = AIResponseGenerator(config.openai_api_key) if config.openai_api_key else None
        self.feedback_channel = None
        
        # 定期的なフィードバック収集タスク
        if not self.collect_feedback_task.is_running():
            self.collect_feedback_task.start()
    
    async def on_ready(self):
        """Bot 起動時の処理"""
        await super().on_ready()
        
        # フィードバックチャンネルを取得
        for guild in self.guilds:
            channel = discord.utils.get(guild.channels, name=self.config.feedback_channel_name)
            if channel:
                self.feedback_channel = channel
                self.logger.info(f'フィードバックチャンネルを見つけました: {channel.name}')
                break
        
        if not self.feedback_channel:
            self.logger.warning(f'フィードバックチャンネル "{self.config.feedback_channel_name}" が見つかりません')
    
    async def on_reaction_add(self, reaction, user):
        """リアクション追加時の処理"""
        if user.bot or not self.feedback_channel:
            return
        
        # フィードバックチャンネルでのリアクションのみ処理
        if reaction.message.channel != self.feedback_channel:
            return
        
        # Bot のメッセージへのリアクションのみ処理
        if reaction.message.author != self.user:
            return
        
        # メッセージからプロンプトIDと応答IDを抽出
        embed = reaction.message.embeds[0] if reaction.message.embeds else None
        if not embed or not embed.footer or not embed.footer.text:
            return
        
        try:
            # フッターから ID を抽出 (例: "Prompt: 1 | Response: 2")
            footer_parts = embed.footer.text.split(' | ')
            prompt_id = int(footer_parts[0].split(': ')[1])
            response_id = int(footer_parts[1].split(': ')[1])
            
            # フィードバックを保存
            feedback_type = 'like' if str(reaction.emoji) in ['👍', '❤️', '🔥'] else 'dislike'
            self.db.save_feedback(
                prompt_id, response_id, str(user.id), user.display_name,
                feedback_type, str(reaction.emoji)
            )
            
            self.logger.info(f'フィードバックを記録: {user.display_name} -> {reaction.emoji}')
            
        except Exception as e:
            self.logger.error(f'リアクション処理エラー: {e}')
    
    async def post_training_prompt(self, prompt: str, category: str = "general"):
        """学習用プロンプトを投稿"""
        if not self.ai_generator or not self.feedback_channel:
            return None
        
        # プロンプトをデータベースに保存
        prompt_id = self.db.save_prompt(prompt, category)
        
        # AI応答を生成
        responses = await self.ai_generator.generate_responses(prompt, 3)
        
        # 各応答をデータベースに保存し、Discordに投稿
        for i, response_data in enumerate(responses):
            response_id = self.db.save_ai_response(
                prompt_id, response_data['text'], 
                response_data['model'], response_data['temperature']
            )
            
            # Discord Embed を作成
            embed = discord.Embed(
                title=f"🧠 AI学習プロンプト: {category}",
                description=f"**プロンプト**: {prompt}",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name=f"🤖 AI応答 {i+1}",
                value=response_data['text'][:1024],  # Discord制限
                inline=False
            )
            
            embed.add_field(
                name="⚙️ 生成設定",
                value=f"モデル: {response_data['model']}\n温度: {response_data['temperature']}",
                inline=True
            )
            
            embed.set_footer(text=f"Prompt: {prompt_id} | Response: {response_id}")
            
            # メッセージを投稿
            message = await self.feedback_channel.send(embed=embed)
            
            # リアクションボタンを追加
            await message.add_reaction('👍')  # 良い
            await message.add_reaction('👎')  # 悪い
            await message.add_reaction('❤️')  # 素晴らしい
            await message.add_reaction('🤔')  # 微妙
            
            await asyncio.sleep(2)  # 投稿間隔
        
        return prompt_id
    
    @tasks.loop(hours=6)  # 6時間ごとに実行
    async def collect_feedback_task(self):
        """定期的なフィードバック収集とデータ生成"""
        if not self.feedback_channel:
            return
        
        self.logger.info('フィードバック収集タスクを実行中...')
        
        # ランダムなプロンプトを生成して投稿
        sample_prompts = [
            ("Pythonでファイルを読み込む最良の方法を教えてください", "programming"),
            ("機械学習の過学習を防ぐ方法は？", "ml"),
            ("効率的なコードレビューのコツを教えて", "development"),
            ("RESTful APIの設計原則について説明して", "api"),
            ("Gitのブランチ戦略でおすすめは？", "git")
        ]
        
        prompt, category = random.choice(sample_prompts)
        await self.post_training_prompt(prompt, category)

# コマンド群
class HumanInLoopCommands(commands.Cog):
    """Human-in-the-Loop 関連コマンド"""
    
    def __init__(self, bot: HumanInLoopBot):
        self.bot = bot
    
    @discord.app_commands.command(name="train_ai", description="AI学習用のプロンプトを投稿")
    @discord.app_commands.describe(
        prompt="AIに学習させたいプロンプト",
        category="カテゴリ（programming, ml, development など）"
    )
    async def train_ai(self, interaction: discord.Interaction, prompt: str, category: str = "general"):
        """AI学習プロンプト投稿コマンド"""
        await interaction.response.defer()
        
        if not self.bot.ai_generator:
            await interaction.followup.send("❌ OpenAI API キーが設定されていません")
            return
        
        await interaction.followup.send(f"🧠 AI学習プロンプトを生成中: `{prompt[:50]}...`")
        
        try:
            prompt_id = await self.bot.post_training_prompt(prompt, category)
            if prompt_id:
                await interaction.followup.send(f"✅ 学習プロンプト（ID: {prompt_id}）を投稿しました！\nフィードバックをお待ちしています 👍👎")
            else:
                await interaction.followup.send("❌ プロンプトの投稿に失敗しました")
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")
    
    @discord.app_commands.command(name="feedback_stats", description="フィードバック統計を表示")
    async def feedback_stats(self, interaction: discord.Interaction):
        """フィードバック統計表示コマンド"""
        await interaction.response.defer()
        
        try:
            conn = sqlite3.connect(self.bot.db.db_path)
            cursor = conn.cursor()
            
            # 統計データを取得
            cursor.execute('SELECT COUNT(*) FROM prompts')
            total_prompts = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM ai_responses')
            total_responses = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM human_feedback')
            total_feedback = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM training_data')
            training_samples = cursor.fetchone()[0]
            
            # カテゴリ別統計
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM prompts 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            ''')
            category_stats = cursor.fetchall()
            
            conn.close()
            
            embed = discord.Embed(
                title="📊 AI学習フィードバック統計",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📝 総プロンプト数", value=total_prompts, inline=True)
            embed.add_field(name="🤖 AI応答数", value=total_responses, inline=True)
            embed.add_field(name="👥 フィードバック数", value=total_feedback, inline=True)
            embed.add_field(name="🎯 学習データ", value=training_samples, inline=True)
            
            if category_stats:
                categories = "\n".join([f"{cat}: {count}" for cat, count in category_stats[:5]])
                embed.add_field(name="📂 カテゴリ別", value=categories, inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ 統計取得エラー: {str(e)}")
    
    @discord.app_commands.command(name="export_training_data", description="学習データをエクスポート")
    async def export_training_data(self, interaction: discord.Interaction):
        """学習データエクスポートコマンド"""
        await interaction.response.defer()
        
        try:
            conn = sqlite3.connect(self.bot.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT prompt_text, chosen_response, rejected_responses, feedback_score, created_at
                FROM training_data
                ORDER BY created_at DESC
                LIMIT 100
            ''')
            
            training_data = cursor.fetchall()
            conn.close()
            
            if not training_data:
                await interaction.followup.send("📭 エクスポートする学習データがありません")
                return
            
            # JSONファイルとして保存
            export_data = []
            for row in training_data:
                export_data.append({
                    'prompt': row[0],
                    'chosen': row[1],
                    'rejected': json.loads(row[2]),
                    'score': row[3],
                    'created_at': row[4]
                })
            
            # ファイルに書き込み
            filename = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Discordにファイルを送信
            with open(filename, 'rb') as f:
                file = discord.File(f, filename)
                await interaction.followup.send(
                    f"📤 学習データをエクスポートしました（{len(export_data)}件）",
                    file=file
                )
            
            # 一時ファイルを削除
            os.remove(filename)
            
        except Exception as e:
            await interaction.followup.send(f"❌ エクスポートエラー: {str(e)}")

async def main():
    """メイン実行関数"""
    bot = HumanInLoopBot()
    
    # 基本機能をセットアップ
    await setup_base_bot(bot)
    
    # Human-in-the-Loop 関連コマンドを追加
    await bot.add_cog(HumanInLoopCommands(bot))
    
    # Bot を実行
    bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())