"""
論文要約 Bot のテスト
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# テスト用にパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bots'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bots', 'paper_summarizer'))

from bots.paper_summarizer.bot import PaperSummarizer, PaperDatabase

class TestPaperDatabase:
    """PaperDatabase のテスト"""
    
    def setup_method(self):
        """各テストの前に実行"""
        self.db = PaperDatabase(":memory:")  # インメモリDB使用
    
    def test_init_database(self):
        """データベース初期化のテスト"""
        # データベースが正常に初期化されることを確認
        assert self.db.db_path == ":memory:"
    
    def test_is_paper_processed_new_paper(self):
        """新しい論文のチェック"""
        result = self.db.is_paper_processed("2024.01001")
        assert result is False
    
    def test_save_and_check_paper(self):
        """論文の保存と確認"""
        paper_data = {
            'arxiv_id': '2024.01001',
            'title': 'Test Paper',
            'authors': 'Test Author',
            'abstract': 'Test abstract',
            'published_date': '2024-01-01',
            'summary': 'Test summary'
        }
        
        # 論文を保存
        paper_id = self.db.save_paper(paper_data)
        assert paper_id > 0
        
        # 保存された論文が処理済みとして認識されることを確認
        result = self.db.is_paper_processed("2024.01001")
        assert result is True

class TestPaperSummarizer:
    """PaperSummarizer のテスト"""
    
    def setup_method(self):
        """各テストの前に実行"""
        self.summarizer = PaperSummarizer("test-api-key")
    
    @pytest.mark.asyncio
    @patch('openai.OpenAI')
    async def test_summarize_paper(self, mock_openai):
        """論文要約のテスト"""
        # OpenAI API のモックレスポンス
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "🔬 **研究概要**: テスト要約"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 要約を実行
        result = await self.summarizer.summarize_paper(
            "Test Title",
            "Test abstract content"
        )
        
        assert "🔬 **研究概要**: テスト要約" in result
    
    @pytest.mark.asyncio
    @patch('openai.OpenAI')
    async def test_summarize_paper_error(self, mock_openai):
        """API エラー時のテスト"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = await self.summarizer.summarize_paper(
            "Test Title",
            "Test abstract"
        )
        
        assert "要約生成中にエラーが発生しました" in result

@pytest.mark.asyncio
async def test_rss_feed_parsing():
    """RSS フィード解析のテスト"""
    # モックの RSS データ
    mock_feed_data = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Feed</title>
            <item>
                <title>Test Paper Title</title>
                <id>http://arxiv.org/abs/2024.01001v1</id>
                <published>2024-01-01T00:00:00Z</published>
                <summary>Test abstract content</summary>
                <author>
                    <name>Test Author</name>
                </author>
            </item>
        </channel>
    </rss>"""
    
    with patch('feedparser.parse') as mock_parse:
        # feedparser のモックレスポンス
        mock_entry = Mock()
        mock_entry.id = "http://arxiv.org/abs/2024.01001v1"
        mock_entry.title = "Test Paper Title"
        mock_entry.summary = "Test abstract content"
        mock_entry.published = "2024-01-01T00:00:00Z"
        mock_entry.authors = [Mock(name="Test Author")]
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        # RSS フィードを解析
        import feedparser
        feed = feedparser.parse("test_url")
        
        assert len(feed.entries) == 1
        assert feed.entries[0].title == "Test Paper Title"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])