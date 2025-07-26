#!/usr/bin/env python3
"""
API キー動作テストスクリプト
全てのAPIキーが正しく設定されているかテスト
"""

import os
import asyncio
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class APITester:
    """API テストクラス"""
    
    def __init__(self):
        self.results = {}
    
    def test_discord_token(self):
        """Discord Bot Token テスト"""
        print("🤖 Discord Bot Token テスト中...")
        
        token = os.getenv('DISCORD_TOKEN')
        guild_id = os.getenv('DISCORD_GUILD_ID')
        
        if not token:
            self.results['discord'] = "❌ DISCORD_TOKEN が設定されていません"
            return False
        
        if not guild_id:
            self.results['discord'] = "❌ DISCORD_GUILD_ID が設定されていません"
            return False
        
        # トークン形式チェック
        if not token.startswith(('Bot ', 'MTk', 'MTA', 'MTI')):
            self.results['discord'] = "⚠️  Discord Token の形式が正しくない可能性があります"
            return False
        
        # Guild ID形式チェック
        try:
            int(guild_id)
            if len(guild_id) < 17 or len(guild_id) > 20:
                self.results['discord'] = "⚠️  Guild ID の形式が正しくない可能性があります"
                return False
        except ValueError:
            self.results['discord'] = "❌ Guild ID は数値である必要があります"
            return False
        
        self.results['discord'] = "✅ Discord設定OK（実際の接続は起動時に確認）"
        return True
    
    async def test_openai_api(self):
        """OpenAI API テスト"""
        print("🧠 OpenAI API テスト中...")
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            self.results['openai'] = "⚠️  OPENAI_API_KEY が設定されていません（論文要約機能は無効）"
            return False
        
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            # 簡単なテストリクエスト
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self.results['openai'] = "✅ OpenAI API 接続成功"
            return True
            
        except ImportError:
            self.results['openai'] = "❌ openai パッケージがインストールされていません"
            return False
        except Exception as e:
            self.results['openai'] = f"❌ OpenAI API エラー: {str(e)}"
            return False
    
    def test_github_token(self):
        """GitHub Token テスト"""
        print("🐙 GitHub Token テスト中...")
        
        token = os.getenv('GITHUB_TOKEN')
        repo_owner = os.getenv('GITHUB_REPO_OWNER')
        repo_name = os.getenv('GITHUB_REPO_NAME')
        
        if not token:
            self.results['github'] = "⚠️  GITHUB_TOKEN が設定されていません（コードレビュー機能は無効）"
            return False
        
        if not repo_owner or not repo_name:
            self.results['github'] = "⚠️  GITHUB_REPO_OWNER/GITHUB_REPO_NAME が設定されていません"
            return False
        
        try:
            from github import Github
            g = Github(token)
            
            # ユーザー情報取得テスト
            user = g.get_user()
            
            # リポジトリアクセステスト
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            
            self.results['github'] = f"✅ GitHub API 接続成功（ユーザー: {user.login}）"
            return True
            
        except ImportError:
            self.results['github'] = "❌ PyGithub パッケージがインストールされていません"
            return False
        except Exception as e:
            self.results['github'] = f"❌ GitHub API エラー: {str(e)}"
            return False
    
    async def test_perspective_api(self):
        """Google Perspective API テスト"""
        print("🛡️  Google Perspective API テスト中...")
        
        api_key = os.getenv('PERSPECTIVE_API_KEY')
        
        if not api_key:
            self.results['perspective'] = "⚠️  PERSPECTIVE_API_KEY が設定されていません（モデレーション機能は無効）"
            return False
        
        try:
            from googleapiclient import discovery
            
            service = discovery.build(
                "commentanalyzer",
                "v1alpha1",
                developerKey=api_key,
                discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                static_discovery=False,
            )
            
            # 簡単なテストリクエスト
            analyze_request = {
                'comment': {'text': 'Hello world'},
                'requestedAttributes': {'TOXICITY': {}},
                'languages': ['en'],
            }
            
            response = await asyncio.to_thread(
                service.comments().analyze(body=analyze_request).execute
            )
            
            self.results['perspective'] = "✅ Google Perspective API 接続成功"
            return True
            
        except ImportError:
            self.results['perspective'] = "❌ google-api-python-client パッケージがインストールされていません"
            return False
        except Exception as e:
            self.results['perspective'] = f"❌ Perspective API エラー: {str(e)}"
            return False
    
    def test_webhook_url(self):
        """Discord Webhook URL テスト"""
        print("🔗 Discord Webhook URL テスト中...")
        
        webhook_url = os.getenv('GITHUB_WEBHOOK_URL')
        
        if not webhook_url:
            self.results['webhook'] = "⚠️  GITHUB_WEBHOOK_URL が設定されていません（GitHub連携は無効）"
            return False
        
        # URL形式チェック
        if not webhook_url.startswith('https://discord.com/api/webhooks/'):
            self.results['webhook'] = "❌ Discord Webhook URL の形式が正しくありません"
            return False
        
        self.results['webhook'] = "✅ Discord Webhook URL 形式OK"
        return True
    
    def test_rss_urls(self):
        """RSS URL テスト"""
        print("📡 RSS URL テスト中...")
        
        rss_urls = os.getenv('ARXIV_RSS_URLS', '')
        
        if not rss_urls:
            self.results['rss'] = "⚠️  ARXIV_RSS_URLS が設定されていません（デフォルトを使用）"
            return False
        
        urls = rss_urls.split(',')
        valid_urls = []
        
        for url in urls:
            url = url.strip()
            if url.startswith('http://export.arxiv.org/rss/'):
                valid_urls.append(url)
        
        if not valid_urls:
            self.results['rss'] = "❌ 有効なarXiv RSS URLがありません"
            return False
        
        self.results['rss'] = f"✅ RSS URL設定OK（{len(valid_urls)}個のフィード）"
        return True
    
    def test_optional_apis(self):
        """オプションAPI テスト"""
        print("🔧 オプションAPI テスト中...")
        
        optional_results = []
        
        # Anthropic Claude
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            optional_results.append("✅ Anthropic API キー設定済み")
        else:
            optional_results.append("⚠️  Anthropic API キー未設定（オプション）")
        
        # Database URL
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            optional_results.append("✅ Database URL設定済み")
        else:
            optional_results.append("⚠️  Database URL未設定（SQLiteを使用）")
        
        self.results['optional'] = "\n   ".join(optional_results)
        return True
    
    async def run_all_tests(self):
        """全テストを実行"""
        print("🧪 AI Forge API キーテスト開始")
        print("=" * 50)
        
        # 各テストを実行
        tests = [
            ('discord', self.test_discord_token),
            ('openai', self.test_openai_api),
            ('github', self.test_github_token),
            ('perspective', self.test_perspective_api),
            ('webhook', self.test_webhook_url),
            ('rss', self.test_rss_urls),
            ('optional', self.test_optional_apis)
        ]
        
        success_count = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                if result:
                    success_count += 1
                    
            except Exception as e:
                self.results[test_name] = f"❌ テスト実行エラー: {str(e)}"
        
        # 結果表示
        print("\n" + "=" * 50)
        print("📊 テスト結果")
        print("=" * 50)
        
        for test_name, result in self.results.items():
            print(f"\n{test_name.upper()}:")
            if '\n' in result:
                for line in result.split('\n'):
                    print(f"   {line}")
            else:
                print(f"   {result}")
        
        print("\n" + "=" * 50)
        print(f"📈 成功率: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
        
        # 推奨アクション
        print("\n🎯 次のステップ:")
        
        if 'discord' in self.results and '✅' in self.results['discord']:
            print("   1. python start_paper_bot.py でBot起動テスト")
        else:
            print("   1. Discord設定を完了してください（DISCORD_SETUP.md参照）")
        
        if 'openai' in self.results and '✅' in self.results['openai']:
            print("   2. /check_papers コマンドで論文要約テスト")
        else:
            print("   2. OpenAI APIキーを設定してください（API_KEYS_SETUP.md参照）")
        
        if success_count >= total_tests * 0.7:
            print("   3. 🎉 基本機能は利用可能です！")
        else:
            print("   3. ⚠️  重要な設定が不足しています")
        
        return success_count >= total_tests * 0.5

async def main():
    """メイン実行関数"""
    tester = APITester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ テスト完了：AI Forgeを起動できます")
        return 0
    else:
        print("\n❌ テスト失敗：設定を確認してください")
        return 1

if __name__ == "__main__":
    import sys
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️  テストを中断しました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        sys.exit(1)