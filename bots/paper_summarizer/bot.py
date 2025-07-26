"""
論文要約 RSS Bot
arXiv などの RSS フィードを監視し、新しい論文を要約して Discord に投稿
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
import openai
import discord
from discord.ext import commands, tasks
import os
import sys

# 親ディレクトリを import パスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_bot import BaseBot, BaseBotConfig, setup_base_bot

class PaperSummarizerConfig(BaseBotConfig):
    """論文要約 Bot の設定"""
    def __init__(self):
        super().__init__()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.rss_urls = os.getenv('ARXIV_RSS_URLS', '').split(',')
        self.summary_channel_name = 'paper-summaries'
        self.check_interval_hours = 6  # 6時間ごとにチェック

class PaperDatabase:
    """論文データベース管理"""
    
    def __init__(self, db_path: str = "papers.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arxiv_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                authors TEXT NOT NULL,
                abstract TEXT NOT NULL,
                published_date TEXT NOT NULL,
                summary TEXT,
                discord_message_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_paper_processed(self, arxiv_id: str) -> bool:
        """論文が既に処理済みかチェック"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM papers WHERE arxiv_id = ?', (arxiv_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def save_paper(self, paper_data: Dict) -> int:
        """論文データを保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO papers (arxiv_id, title, authors, abstract, published_date, summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            paper_data['arxiv_id'],
            paper_data['title'],
            paper_data['authors'],
            paper_data['abstract'],
            paper_data['published_date'],
            paper_data['summary']
        ))
        
        paper_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return paper_id

class PaperSummarizer:
    """論文要約エンジン"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def summarize_paper(self, title: str, abstract: str) -> str:
        """論文を要約"""
        prompt = f"""
以下の AI/ML 論文のタイトルとアブストラクトを日本語で簡潔に要約してください。
開発者コミュニティ向けに、技術的なポイントと実用性を重視して説明してください。

タイトル: {title}

アブストラクト: {abstract}

要約は以下の形式で出力してください：
🔬 **研究概要**: [1-2文で研究の核心を説明]
💡 **技術的貢献**: [新しい手法や改善点を説明]
🚀 **実用性**: [開発者にとっての意義や応用可能性]
📊 **結果**: [主要な実験結果や性能向上]
"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"要約生成中にエラーが発生しました: {str(e)}"

class PaperSummarizerBot(BaseBot):
    """論文要約 Bot メインクラス"""
    
    def __init__(self):
        config = PaperSummarizerConfig()
        super().__init__(config)
        
        self.db = PaperDatabase()
        self.summarizer = PaperSummarizer(config.openai_api_key) if config.openai_api_key else None
        self.summary_channel = None
        
        # RSS チェックタスクを開始
        if not self.check_rss_feeds.is_running():
            self.check_rss_feeds.start()
    
    async def on_ready(self):
        """Bot 起動時の処理"""
        await super().on_ready()
        
        # 要約チャンネルを取得
        for guild in self.guilds:
            channel = discord.utils.get(guild.channels, name=self.config.summary_channel_name)
            if channel:
                self.summary_channel = channel
                self.logger.info(f'要約チャンネルを見つけました: {channel.name}')
                break
        
        if not self.summary_channel:
            self.logger.warning(f'要約チャンネル "{self.config.summary_channel_name}" が見つかりません')
    
    @tasks.loop(hours=6)  # 6時間ごとに実行
    async def check_rss_feeds(self):
        """RSS フィードをチェックして新しい論文を処理"""
        if not self.summarizer or not self.summary_channel:
            self.logger.warning('要約機能またはチャンネルが設定されていません')
            return
        
        self.logger.info('RSS フィードをチェック中...')
        
        for rss_url in self.config.rss_urls:
            if not rss_url.strip():
                continue
                
            try:
                await self.process_rss_feed(rss_url.strip())
                # フィード間で少し待機
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f'RSS フィード処理エラー ({rss_url}): {e}')
    
    @check_rss_feeds.before_loop
    async def before_check_rss_feeds(self):
        """RSS チェックタスク開始前の待機"""
        await self.wait_until_ready()
        # Bot起動後、少し待ってからタスクを開始
        await asyncio.sleep(30)
    
    async def process_rss_feed(self, rss_url: str):
        """単一の RSS フィードを処理"""
        try:
            # RSS フィードを非同期で取得
            feed = await asyncio.to_thread(feedparser.parse, rss_url)
            
            if not hasattr(feed, 'entries') or not feed.entries:
                self.logger.warning(f'RSS フィードにエントリがありません: {rss_url}')
                return
            
            self.logger.info(f'RSS フィードから {len(feed.entries)} 件のエントリを取得: {rss_url}')
            new_papers_count = 0
            
            for entry in feed.entries[:3]:  # 最新3件のみ処理（負荷軽減）
                try:
                    # arXiv ID を抽出
                    if not hasattr(entry, 'id') or not entry.id:
                        continue
                    
                    arxiv_id = entry.id.split('/')[-1].split('v')[0]  # バージョン番号を除去
                    
                    # 既に処理済みかチェック
                    if self.db.is_paper_processed(arxiv_id):
                        continue
                    
                    # 必要なフィールドの存在確認
                    if not all([hasattr(entry, attr) for attr in ['title', 'summary', 'published']]):
                        self.logger.warning(f'必要なフィールドが不足: {arxiv_id}')
                        continue
                    
                    # 著者情報を安全に取得
                    authors = "Unknown"
                    if hasattr(entry, 'authors') and entry.authors:
                        try:
                            authors = ', '.join([author.name for author in entry.authors])
                        except:
                            authors = str(entry.authors)
                    
                    # 論文データを準備
                    paper_data = {
                        'arxiv_id': arxiv_id,
                        'title': entry.title.strip(),
                        'authors': authors,
                        'abstract': entry.summary.strip(),
                        'published_date': entry.published,
                        'summary': ''
                    }
                    
                    # 要約を生成
                    self.logger.info(f'論文要約を生成中: {paper_data["title"][:50]}...')
                    summary = await self.summarizer.summarize_paper(
                        paper_data['title'], 
                        paper_data['abstract']
                    )
                    paper_data['summary'] = summary
                    
                    # データベースに保存
                    paper_id = self.db.save_paper(paper_data)
                    
                    # Discord に投稿
                    await self.post_paper_summary(paper_data)
                    
                    new_papers_count += 1
                    self.logger.info(f'新しい論文を処理しました: {paper_data["title"][:50]}...')
                    
                    # レート制限を避けるため少し待機
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    self.logger.error(f'論文処理エラー ({arxiv_id if "arxiv_id" in locals() else "unknown"}): {e}')
                    continue
            
            if new_papers_count > 0:
                self.logger.info(f'{new_papers_count} 件の新しい論文を処理しました')
            else:
                self.logger.info('新しい論文はありませんでした')
                
        except Exception as e:
            self.logger.error(f'RSS フィード処理エラー ({rss_url}): {e}')
    
    async def post_paper_summary(self, paper_data: Dict):
        """論文要約を Discord に投稿"""
        try:
            # タイトルの長さ制限
            title = paper_data['title'][:250] + "..." if len(paper_data['title']) > 250 else paper_data['title']
            
            # 要約の長さ制限
            summary = paper_data['summary'][:2000] + "..." if len(paper_data['summary']) > 2000 else paper_data['summary']
            
            embed = discord.Embed(
                title=title,
                url=f"https://arxiv.org/abs/{paper_data['arxiv_id']}",
                description=summary,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # 著者情報（長すぎる場合は切り詰め）
            authors = paper_data['authors'][:500] + "..." if len(paper_data['authors']) > 500 else paper_data['authors']
            embed.add_field(
                name="📝 著者", 
                value=authors, 
                inline=False
            )
            
            embed.add_field(
                name="🔗 arXiv ID", 
                value=paper_data['arxiv_id'], 
                inline=True
            )
            
            # 公開日の安全な処理
            try:
                pub_date = paper_data['published_date'][:10] if paper_data['published_date'] else "不明"
            except:
                pub_date = "不明"
            
            embed.add_field(
                name="📅 公開日", 
                value=pub_date, 
                inline=True
            )
            
            embed.set_footer(text="AI Forge Paper Summarizer")
            
            message = await self.summary_channel.send(embed=embed)
            
            # リアクションを追加（ユーザーフィードバック用）
            await message.add_reaction('👍')  # 有用
            await message.add_reaction('🤔')  # 微妙
            await message.add_reaction('❤️')  # 素晴らしい
            
            self.logger.info(f'Discord に投稿完了: {paper_data["arxiv_id"]}')
            
        except discord.HTTPException as e:
            self.logger.error(f'Discord HTTP エラー: {e}')
        except Exception as e:
            self.logger.error(f'Discord 投稿エラー: {e}')

# コマンド群
class PaperCommands(commands.Cog):
    """論文関連コマンド"""
    
    def __init__(self, bot: PaperSummarizerBot):
        self.bot = bot
    
    @discord.app_commands.command(name="check_papers", description="手動で RSS フィードをチェック")
    async def check_papers(self, interaction: discord.Interaction):
        """手動で論文チェックを実行"""
        await interaction.response.defer()
        
        if not self.bot.summarizer:
            await interaction.followup.send("❌ OpenAI API キーが設定されていません")
            return
        
        await interaction.followup.send("🔍 RSS フィードをチェック中...")
        
        try:
            await self.bot.check_rss_feeds()
            await interaction.followup.send("✅ RSS フィードのチェックが完了しました")
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")

async def main():
    """メイン実行関数"""
    bot = PaperSummarizerBot()
    
    # 基本機能をセットアップ
    await setup_base_bot(bot)
    
    # 論文関連コマンドを追加
    await bot.add_cog(PaperCommands(bot))
    
    # Bot を実行
    bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())