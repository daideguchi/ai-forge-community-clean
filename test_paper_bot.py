#!/usr/bin/env python3
"""
Paper Summarizer Bot の単体テスト・動作確認スクリプト
実際のDiscordに接続する前に基本機能をテスト
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# パスを追加
sys.path.append('bots')
sys.path.append('bots/paper_summarizer')

from bots.paper_summarizer.bot import PaperDatabase, PaperSummarizer, AICodeReviewer

async def test_database():
    """データベース機能のテスト"""
    print("🗄️  データベーステスト開始...")
    
    db = PaperDatabase("test_papers.db")
    
    # テストデータ
    test_paper = {
        'arxiv_id': '2024.00001',
        'title': 'Test Paper: A Novel Approach to Testing',
        'authors': 'Test Author, Another Author',
        'abstract': 'This is a test abstract for testing purposes.',
        'published_date': '2024-01-01',
        'summary': 'This is a test summary.'
    }
    
    # 論文を保存
    paper_id = db.save_paper(test_paper)
    print(f"✅ 論文を保存しました (ID: {paper_id})")
    
    # 重複チェック
    is_processed = db.is_paper_processed('2024.00001')
    print(f"✅ 重複チェック: {is_processed}")
    
    # 新しい論文のチェック
    is_new = db.is_paper_processed('2024.00002')
    print(f"✅ 新しい論文チェック: {not is_new}")
    
    # テストファイルを削除
    os.remove("test_papers.db")
    print("🗑️  テストデータベースを削除しました")

async def test_summarizer():
    """AI要約機能のテスト"""
    print("\n🧠 AI要約テスト開始...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY が設定されていません")
        return
    
    summarizer = PaperSummarizer(api_key)
    
    # テスト用の論文情報
    test_title = "Attention Is All You Need"
    test_abstract = """
    The dominant sequence transduction models are based on complex recurrent or 
    convolutional neural networks that include an encoder and a decoder. The best 
    performing models also connect the encoder and decoder through an attention 
    mechanism. We propose a new simple network architecture, the Transformer, 
    based solely on attention mechanisms, dispensing with recurrence and convolutions 
    entirely.
    """
    
    try:
        summary = await summarizer.summarize_paper(test_title, test_abstract)
        print("✅ 要約生成成功:")
        print(f"📝 {summary[:200]}...")
    except Exception as e:
        print(f"❌ 要約生成エラー: {e}")

async def test_rss_parsing():
    """RSS解析のテスト"""
    print("\n📡 RSS解析テスト開始...")
    
    import feedparser
    
    # arXiv CS.AI のRSSフィードをテスト
    rss_url = "http://export.arxiv.org/rss/cs.AI"
    
    try:
        print(f"🔍 RSS フィードを取得中: {rss_url}")
        feed = await asyncio.to_thread(feedparser.parse, rss_url)
        
        if feed.entries:
            print(f"✅ {len(feed.entries)} 件のエントリを取得")
            
            # 最初のエントリの詳細を表示
            first_entry = feed.entries[0]
            print(f"📄 最新論文:")
            print(f"   タイトル: {first_entry.title[:80]}...")
            print(f"   ID: {first_entry.id.split('/')[-1]}")
            print(f"   公開日: {first_entry.published}")
            print(f"   著者数: {len(first_entry.authors) if hasattr(first_entry, 'authors') else 'N/A'}")
        else:
            print("❌ エントリが見つかりませんでした")
            
    except Exception as e:
        print(f"❌ RSS解析エラー: {e}")

async def test_discord_embed():
    """Discord Embed形式のテスト"""
    print("\n💬 Discord Embed テスト開始...")
    
    # Embedの構造をシミュレート
    embed_data = {
        'title': 'Test Paper: A Novel Approach to Testing',
        'url': 'https://arxiv.org/abs/2024.00001',
        'description': '🔬 **研究概要**: テスト用の論文です\n💡 **技術的貢献**: 新しいテスト手法\n🚀 **実用性**: 開発者向け',
        'color': 0x0099ff,
        'fields': [
            {'name': '📝 著者', 'value': 'Test Author, Another Author'},
            {'name': '🔗 arXiv ID', 'value': '2024.00001'},
            {'name': '📅 公開日', 'value': '2024-01-01'}
        ]
    }
    
    print("✅ Discord Embed 構造:")
    print(f"   タイトル: {embed_data['title']}")
    print(f"   URL: {embed_data['url']}")
    print(f"   説明: {embed_data['description'][:50]}...")
    print(f"   フィールド数: {len(embed_data['fields'])}")

async def main():
    """メインテスト関数"""
    print("🚀 Paper Summarizer Bot テスト開始\n")
    
    # 各機能を順番にテスト
    await test_database()
    await test_rss_parsing()
    await test_discord_embed()
    await test_summarizer()  # API キーが必要なので最後
    
    print("\n✅ 全てのテストが完了しました！")
    print("\n次のステップ:")
    print("1. .env ファイルに必要なAPIキーを設定")
    print("2. Discord Bot を作成してトークンを取得")
    print("3. Discord サーバーに #paper-summaries チャンネルを作成")
    print("4. python bots/paper_summarizer/bot.py で実行")

if __name__ == "__main__":
    asyncio.run(main())