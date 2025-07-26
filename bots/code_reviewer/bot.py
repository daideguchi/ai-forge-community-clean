"""
AI コードレビュー Bot
GitHub Pull Request を自動的にレビューし、改善提案を行う
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Optional
import discord
from discord.ext import commands
import openai
from github import Github
import requests
from datetime import datetime

# 親ディレクトリを import パスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_bot import BaseBot, BaseBotConfig, setup_base_bot

class CodeReviewerConfig(BaseBotConfig):
    """コードレビューBot の設定"""
    def __init__(self):
        super().__init__()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo_owner = os.getenv('GITHUB_REPO_OWNER')
        self.github_repo_name = os.getenv('GITHUB_REPO_NAME')
        self.review_channel_name = 'code-review-queue'

class GitHubManager:
    """GitHub API 管理クラス"""
    
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.github = Github(token)
        self.repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
        self.repo_owner = repo_owner
        self.repo_name = repo_name
    
    def get_pull_request(self, pr_number: int):
        """Pull Request を取得"""
        return self.repo.get_pull(pr_number)
    
    def get_pr_diff(self, pr_number: int) -> str:
        """Pull Request の差分を取得"""
        pr = self.get_pull_request(pr_number)
        
        # GitHub API で diff を取得
        headers = {
            'Authorization': f'token {self.github._Github__requester._Requester__authorizationHeader.split()[1]}',
            'Accept': 'application/vnd.github.v3.diff'
        }
        
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text
        else:
            return ""
    
    def get_pr_files(self, pr_number: int) -> List[Dict]:
        """Pull Request で変更されたファイル一覧を取得"""
        pr = self.get_pull_request(pr_number)
        files = []
        
        for file in pr.get_files():
            files.append({
                'filename': file.filename,
                'status': file.status,
                'additions': file.additions,
                'deletions': file.deletions,
                'changes': file.changes,
                'patch': file.patch if hasattr(file, 'patch') else None
            })
        
        return files
    
    def post_review_comment(self, pr_number: int, body: str, commit_sha: str = None):
        """Pull Request にレビューコメントを投稿"""
        pr = self.get_pull_request(pr_number)
        
        if commit_sha is None:
            commit_sha = pr.head.sha
        
        # レビューを作成
        pr.create_review(
            body=body,
            event="COMMENT"
        )

class AICodeReviewer:
    """AI コードレビューエンジン"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def review_code_diff(self, diff: str, pr_info: Dict) -> str:
        """コード差分をレビュー"""
        prompt = f"""
あなたは経験豊富なシニアソフトウェアエンジニアです。以下のPull Requestをレビューしてください。

## Pull Request 情報
- タイトル: {pr_info.get('title', 'N/A')}
- 説明: {pr_info.get('body', 'N/A')}
- 変更ファイル数: {pr_info.get('changed_files', 0)}
- 追加行数: {pr_info.get('additions', 0)}
- 削除行数: {pr_info.get('deletions', 0)}

## コード差分
```diff
{diff[:8000]}  # 長すぎる場合は切り詰め
```

以下の観点でレビューを行い、日本語で回答してください：

### 🔍 **コード品質**
- コードの可読性と保守性
- 命名規則の適切性
- 関数・クラスの設計

### 🐛 **潜在的な問題**
- バグの可能性
- エラーハンドリング
- エッジケースの考慮

### 🚀 **パフォーマンス**
- 効率性の改善点
- メモリ使用量
- 計算量の最適化

### 🔒 **セキュリティ**
- セキュリティ上の懸念
- 入力値検証
- 権限管理

### 💡 **改善提案**
- より良い実装方法
- リファクタリングの提案
- ベストプラクティスの適用

良い点も含めて、建設的なフィードバックを提供してください。
重大な問題がある場合は ⚠️ で、軽微な改善点は 💡 で示してください。
"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",  # より高品質なレビューのためGPT-4を使用
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3  # 一貫性のあるレビューのため低めに設定
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ レビュー生成中にエラーが発生しました: {str(e)}"
    
    async def review_specific_file(self, file_content: str, filename: str) -> str:
        """特定のファイルをレビュー"""
        prompt = f"""
ファイル `{filename}` の変更内容をレビューしてください。

```
{file_content[:4000]}
```

このファイルの変更について、簡潔で具体的なフィードバックを日本語で提供してください。
"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ ファイルレビュー中にエラーが発生しました: {str(e)}"

class CodeReviewerBot(BaseBot):
    """コードレビューBot メインクラス"""
    
    def __init__(self):
        config = CodeReviewerConfig()
        super().__init__(config)
        
        self.github_manager = None
        self.ai_reviewer = None
        self.review_channel = None
        
        # GitHub と AI の初期化
        if config.github_token and config.github_repo_owner and config.github_repo_name:
            self.github_manager = GitHubManager(
                config.github_token,
                config.github_repo_owner,
                config.github_repo_name
            )
        
        if config.openai_api_key:
            self.ai_reviewer = AICodeReviewer(config.openai_api_key)
    
    async def on_ready(self):
        """Bot 起動時の処理"""
        await super().on_ready()
        
        # レビューチャンネルを取得
        for guild in self.guilds:
            channel = discord.utils.get(guild.channels, name=self.config.review_channel_name)
            if channel:
                self.review_channel = channel
                self.logger.info(f'レビューチャンネルを見つけました: {channel.name}')
                break
        
        if not self.review_channel:
            self.logger.warning(f'レビューチャンネル "{self.config.review_channel_name}" が見つかりません')
    
    async def review_pull_request(self, pr_number: int) -> Dict:
        """Pull Request をレビュー"""
        if not self.github_manager or not self.ai_reviewer:
            return {"error": "GitHub または OpenAI の設定が不完全です"}
        
        try:
            # PR 情報を取得
            pr = self.github_manager.get_pull_request(pr_number)
            pr_info = {
                'title': pr.title,
                'body': pr.body or "",
                'changed_files': pr.changed_files,
                'additions': pr.additions,
                'deletions': pr.deletions,
                'author': pr.user.login,
                'url': pr.html_url
            }
            
            # 差分を取得
            diff = self.github_manager.get_pr_diff(pr_number)
            
            if not diff:
                return {"error": "差分を取得できませんでした"}
            
            # AI レビューを実行
            review_result = await self.ai_reviewer.review_code_diff(diff, pr_info)
            
            return {
                "success": True,
                "pr_info": pr_info,
                "review": review_result
            }
            
        except Exception as e:
            self.logger.error(f"PR レビューエラー: {e}")
            return {"error": str(e)}
    
    async def post_review_to_discord(self, review_data: Dict):
        """レビュー結果を Discord に投稿"""
        if not self.review_channel:
            return
        
        if "error" in review_data:
            embed = discord.Embed(
                title="❌ レビューエラー",
                description=review_data["error"],
                color=discord.Color.red()
            )
            await self.review_channel.send(embed=embed)
            return
        
        pr_info = review_data["pr_info"]
        review = review_data["review"]
        
        # メインのレビュー結果
        embed = discord.Embed(
            title=f"🔍 コードレビュー: {pr_info['title'][:100]}",
            url=pr_info['url'],
            description=f"**作成者**: {pr_info['author']}\n**変更**: +{pr_info['additions']} -{pr_info['deletions']} ({pr_info['changed_files']} files)",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # レビュー内容を分割して表示（Discord の制限対応）
        review_chunks = [review[i:i+1024] for i in range(0, len(review), 1024)]
        
        for i, chunk in enumerate(review_chunks[:3]):  # 最大3つのフィールド
            embed.add_field(
                name=f"📝 レビュー結果 ({i+1})" if len(review_chunks) > 1 else "📝 レビュー結果",
                value=chunk,
                inline=False
            )
        
        embed.set_footer(text="AI Code Reviewer")
        
        await self.review_channel.send(embed=embed)

# コマンド群
class CodeReviewCommands(commands.Cog):
    """コードレビュー関連コマンド"""
    
    def __init__(self, bot: CodeReviewerBot):
        self.bot = bot
    
    @discord.app_commands.command(name="review_pr", description="Pull Request をレビュー")
    @discord.app_commands.describe(pr_number="レビューする PR 番号")
    async def review_pr(self, interaction: discord.Interaction, pr_number: int):
        """Pull Request レビューコマンド"""
        await interaction.response.defer()
        
        if not self.bot.github_manager or not self.bot.ai_reviewer:
            await interaction.followup.send("❌ GitHub または OpenAI の設定が不完全です")
            return
        
        await interaction.followup.send(f"🔍 PR #{pr_number} をレビュー中...")
        
        # レビューを実行
        review_data = await self.bot.review_pull_request(pr_number)
        
        # Discord に結果を投稿
        await self.bot.post_review_to_discord(review_data)
        
        if "error" in review_data:
            await interaction.followup.send(f"❌ レビューに失敗しました: {review_data['error']}")
        else:
            await interaction.followup.send(f"✅ PR #{pr_number} のレビューが完了しました！")
    
    @discord.app_commands.command(name="review_latest", description="最新の PR をレビュー")
    async def review_latest(self, interaction: discord.Interaction):
        """最新の PR をレビュー"""
        await interaction.response.defer()
        
        if not self.bot.github_manager:
            await interaction.followup.send("❌ GitHub の設定が不完全です")
            return
        
        try:
            # 最新の PR を取得
            pulls = self.bot.github_manager.repo.get_pulls(state='open')
            latest_pr = next(iter(pulls), None)
            
            if not latest_pr:
                await interaction.followup.send("📭 オープンな PR が見つかりません")
                return
            
            await interaction.followup.send(f"🔍 最新の PR #{latest_pr.number} をレビュー中...")
            
            # レビューを実行
            review_data = await self.bot.review_pull_request(latest_pr.number)
            
            # Discord に結果を投稿
            await self.bot.post_review_to_discord(review_data)
            
            if "error" in review_data:
                await interaction.followup.send(f"❌ レビューに失敗しました: {review_data['error']}")
            else:
                await interaction.followup.send(f"✅ PR #{latest_pr.number} のレビューが完了しました！")
                
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")
    
    @discord.app_commands.command(name="list_prs", description="オープンな PR 一覧を表示")
    async def list_prs(self, interaction: discord.Interaction):
        """PR 一覧表示コマンド"""
        await interaction.response.defer()
        
        if not self.bot.github_manager:
            await interaction.followup.send("❌ GitHub の設定が不完全です")
            return
        
        try:
            pulls = list(self.bot.github_manager.repo.get_pulls(state='open'))
            
            if not pulls:
                await interaction.followup.send("📭 オープンな PR が見つかりません")
                return
            
            embed = discord.Embed(
                title="📋 オープンな Pull Request 一覧",
                color=discord.Color.green()
            )
            
            for pr in pulls[:10]:  # 最大10件表示
                embed.add_field(
                    name=f"#{pr.number} {pr.title[:50]}",
                    value=f"👤 {pr.user.login} | 📅 {pr.created_at.strftime('%Y-%m-%d')}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}")

async def main():
    """メイン実行関数"""
    bot = CodeReviewerBot()
    
    # 基本機能をセットアップ
    await setup_base_bot(bot)
    
    # コードレビュー関連コマンドを追加
    await bot.add_cog(CodeReviewCommands(bot))
    
    # Bot を実行
    bot.run_bot()

if __name__ == "__main__":
    asyncio.run(main())