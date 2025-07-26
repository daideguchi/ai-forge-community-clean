#!/usr/bin/env python3
"""
GitHub Actions で実行される AI コードレビュースクリプト
Pull Request を自動的にレビューして GitHub にコメントを投稿
"""

import os
import sys
import asyncio
import openai
from github import Github
import requests

class GitHubActionReviewer:
    """GitHub Actions 用の AI レビューアー"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('REPO_OWNER')
        self.repo_name = os.getenv('REPO_NAME')
        self.pr_number = int(os.getenv('PR_NUMBER'))
        
        if not all([self.openai_key, self.github_token, self.repo_owner, self.repo_name]):
            raise ValueError("必要な環境変数が設定されていません")
        
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        self.openai_client = openai.OpenAI(api_key=self.openai_key)
    
    def get_pr_diff(self) -> str:
        """PR の差分を取得"""
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3.diff'
        }
        
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{self.pr_number}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"差分取得エラー: {response.status_code}")
            return ""
    
    def get_pr_files(self):
        """PR で変更されたファイルを取得"""
        pr = self.repo.get_pull(self.pr_number)
        return list(pr.get_files())
    
    async def review_code(self, diff: str, pr_info: dict) -> str:
        """コードをレビュー"""
        # 差分が長すぎる場合は切り詰め
        if len(diff) > 12000:
            diff = diff[:12000] + "\n... (差分が長いため切り詰められました)"
        
        prompt = f"""
あなたは経験豊富なソフトウェアエンジニアです。以下のPull Requestをレビューしてください。

## PR情報
- タイトル: {pr_info.get('title', 'N/A')}
- 作成者: {pr_info.get('author', 'N/A')}
- 変更ファイル数: {pr_info.get('changed_files', 0)}

## 差分
```diff
{diff}
```

以下の観点でレビューを行い、GitHub のコメント形式で回答してください：

### 🔍 コード品質
- 可読性と保守性
- 命名規則
- 設計パターン

### 🐛 潜在的な問題
- バグの可能性
- エラーハンドリング
- エッジケース

### 🚀 改善提案
- パフォーマンス
- セキュリティ
- ベストプラクティス

良い点も含めて建設的なフィードバックを提供してください。
重要な問題には ⚠️、改善提案には 💡 を使用してください。
"""
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ AI レビュー生成エラー: {str(e)}"
    
    def post_review_comment(self, review_text: str):
        """GitHub PR にレビューコメントを投稿"""
        pr = self.repo.get_pull(self.pr_number)
        
        # AI レビューのヘッダーを追加
        comment_body = f"""## 🤖 AI Code Review

{review_text}

---
*このレビューは AI によって自動生成されました。参考程度にご利用ください。*
"""
        
        try:
            pr.create_review(
                body=comment_body,
                event="COMMENT"
            )
            print("✅ レビューコメントを投稿しました")
        except Exception as e:
            print(f"❌ コメント投稿エラー: {e}")
    
    async def run_review(self):
        """レビューを実行"""
        print(f"🔍 PR #{self.pr_number} をレビュー中...")
        
        # PR 情報を取得
        pr = self.repo.get_pull(self.pr_number)
        pr_info = {
            'title': pr.title,
            'author': pr.user.login,
            'changed_files': pr.changed_files,
            'additions': pr.additions,
            'deletions': pr.deletions
        }
        
        # 差分を取得
        diff = self.get_pr_diff()
        if not diff:
            print("❌ 差分を取得できませんでした")
            return
        
        # 変更が小さすぎる場合はスキップ
        if pr_info['additions'] + pr_info['deletions'] < 5:
            print("📝 変更が小さいためレビューをスキップします")
            return
        
        # AI レビューを実行
        review_result = await self.review_code(diff, pr_info)
        
        # GitHub にコメントを投稿
        self.post_review_comment(review_result)
        
        print("✅ AI レビューが完了しました")

async def main():
    """メイン実行関数"""
    try:
        reviewer = GitHubActionReviewer()
        await reviewer.run_review()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())