"""
GitHub Webhook セットアップスクリプト
GitHub リポジトリに Discord Webhook を自動設定
"""

import os
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class GitHubWebhookManager:
    """GitHub Webhook 管理クラス"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER')
        self.repo_name = os.getenv('GITHUB_REPO_NAME')
        self.discord_webhook_url = os.getenv('GITHUB_WEBHOOK_URL')
        
        if not all([self.github_token, self.repo_owner, self.repo_name, self.discord_webhook_url]):
            raise ValueError("必要な環境変数が設定されていません")
        
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
    
    def create_webhook(self, events: List[str] = None) -> Dict:
        """Discord Webhook を作成"""
        if events is None:
            events = [
                'push',
                'pull_request',
                'issues',
                'issue_comment',
                'pull_request_review',
                'release'
            ]
        
        # Discord Webhook URL に /github を追加
        discord_url = self.discord_webhook_url
        if not discord_url.endswith('/github'):
            discord_url += '/github'
        
        webhook_data = {
            'name': 'web',
            'active': True,
            'events': events,
            'config': {
                'url': discord_url,
                'content_type': 'json',
                'insecure_ssl': '0'
            }
        }
        
        response = requests.post(
            f'{self.base_url}/hooks',
            headers=self.headers,
            json=webhook_data
        )
        
        if response.status_code == 201:
            print("✅ Webhook が正常に作成されました！")
            return response.json()
        else:
            print(f"❌ Webhook 作成エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return {}
    
    def list_webhooks(self) -> List[Dict]:
        """既存の Webhook を一覧表示"""
        response = requests.get(
            f'{self.base_url}/hooks',
            headers=self.headers
        )
        
        if response.status_code == 200:
            webhooks = response.json()
            print(f"📋 既存の Webhook 数: {len(webhooks)}")
            
            for i, webhook in enumerate(webhooks, 1):
                print(f"{i}. ID: {webhook['id']}")
                print(f"   URL: {webhook['config'].get('url', 'N/A')}")
                print(f"   Events: {', '.join(webhook['events'])}")
                print(f"   Active: {webhook['active']}")
                print()
            
            return webhooks
        else:
            print(f"❌ Webhook 取得エラー: {response.status_code}")
            return []
    
    def delete_webhook(self, webhook_id: int) -> bool:
        """Webhook を削除"""
        response = requests.delete(
            f'{self.base_url}/hooks/{webhook_id}',
            headers=self.headers
        )
        
        if response.status_code == 204:
            print(f"✅ Webhook (ID: {webhook_id}) が削除されました")
            return True
        else:
            print(f"❌ Webhook 削除エラー: {response.status_code}")
            return False
    
    def test_webhook(self, webhook_id: int) -> bool:
        """Webhook をテスト"""
        response = requests.post(
            f'{self.base_url}/hooks/{webhook_id}/test',
            headers=self.headers
        )
        
        if response.status_code == 204:
            print(f"✅ Webhook (ID: {webhook_id}) のテストが送信されました")
            return True
        else:
            print(f"❌ Webhook テストエラー: {response.status_code}")
            return False

def main():
    """メイン実行関数"""
    try:
        manager = GitHubWebhookManager()
        
        print("🚀 GitHub Webhook セットアップツール")
        print(f"リポジトリ: {manager.repo_owner}/{manager.repo_name}")
        print()
        
        while True:
            print("選択してください:")
            print("1. 新しい Webhook を作成")
            print("2. 既存の Webhook を一覧表示")
            print("3. Webhook を削除")
            print("4. Webhook をテスト")
            print("5. 終了")
            
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == '1':
                print("\n📝 Webhook を作成中...")
                result = manager.create_webhook()
                if result:
                    print(f"Webhook ID: {result.get('id')}")
                    print(f"URL: {result.get('config', {}).get('url')}")
            
            elif choice == '2':
                print("\n📋 既存の Webhook を取得中...")
                manager.list_webhooks()
            
            elif choice == '3':
                webhooks = manager.list_webhooks()
                if webhooks:
                    try:
                        webhook_id = int(input("削除する Webhook ID を入力: "))
                        manager.delete_webhook(webhook_id)
                    except ValueError:
                        print("❌ 無効な ID です")
                else:
                    print("削除する Webhook がありません")
            
            elif choice == '4':
                webhooks = manager.list_webhooks()
                if webhooks:
                    try:
                        webhook_id = int(input("テストする Webhook ID を入力: "))
                        manager.test_webhook(webhook_id)
                    except ValueError:
                        print("❌ 無効な ID です")
                else:
                    print("テストする Webhook がありません")
            
            elif choice == '5':
                print("👋 終了します")
                break
            
            else:
                print("❌ 無効な選択です")
            
            print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()