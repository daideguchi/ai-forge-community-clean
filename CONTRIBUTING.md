# AI Forge への貢献ガイド

AI Forge コミュニティへの貢献を歓迎します！このガイドでは、プロジェクトに貢献する方法を説明します。

## 🤝 貢献の種類

### 1. コード貢献
- 新機能の実装
- バグ修正
- パフォーマンス改善
- テストの追加

### 2. ドキュメント貢献
- README やガイドの改善
- コメントの追加・改善
- 翻訳

### 3. コミュニティ貢献
- バグレポート
- 機能提案
- 質問への回答
- コードレビュー

## 🚀 開発環境のセットアップ

### 1. リポジトリのフォーク
```bash
# GitHub でリポジトリをフォーク後
git clone https://github.com/YOUR_USERNAME/ai-dev-community.git
cd ai-dev-community
```

### 2. 開発環境の準備
```bash
# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# 開発用の追加パッケージをインストール
pip install pytest pytest-asyncio black flake8 pre-commit
```

### 3. 環境変数の設定
```bash
cp .env.example .env
# .env ファイルを編集して必要な値を設定
```

### 4. Pre-commit フックの設定
```bash
pre-commit install
```

## 📝 開発ワークフロー

### 1. ブランチの作成
```bash
git checkout -b feature/your-feature-name
# または
git checkout -b fix/bug-description
```

### 2. コードの実装
- 既存のコードスタイルに従う
- 適切なコメントを追加
- テストを書く

### 3. テストの実行
```bash
# 全テストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_paper_summarizer.py

# カバレッジ付きでテスト実行
pytest --cov=bots tests/
```

### 4. コードフォーマット
```bash
# Black でフォーマット
black bots/ tests/

# Flake8 でリント
flake8 bots/ tests/
```

### 5. コミット
```bash
git add .
git commit -m "feat: add paper summarization feature"
```

#### コミットメッセージの規則
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント更新
- `test:` テスト追加・修正
- `refactor:` リファクタリング
- `style:` コードスタイル修正

### 6. プルリクエストの作成
```bash
git push origin feature/your-feature-name
```

GitHub でプルリクエストを作成し、以下を含めてください：
- 変更内容の説明
- 関連する Issue 番号
- テスト結果
- スクリーンショット（UI 変更の場合）

## 🧪 テストガイドライン

### 1. テストの種類
- **単体テスト**: 個別の関数・クラスのテスト
- **統合テスト**: 複数のコンポーネント間のテスト
- **E2E テスト**: エンドツーエンドのテスト

### 2. テストの書き方
```python
import pytest
from unittest.mock import Mock, patch

class TestYourClass:
    def setup_method(self):
        """各テストの前に実行"""
        self.instance = YourClass()
    
    def test_your_method(self):
        """メソッドのテスト"""
        result = self.instance.your_method("input")
        assert result == "expected_output"
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        """非同期メソッドのテスト"""
        result = await self.instance.async_method()
        assert result is not None
```

### 3. モックの使用
外部 API や Discord API のテストには Mock を使用：
```python
@patch('openai.OpenAI')
async def test_with_mock(self, mock_openai):
    mock_client = Mock()
    mock_openai.return_value = mock_client
    # テストロジック
```

## 📋 コードスタイル

### 1. Python スタイル
- [PEP 8](https://pep8.org/) に従う
- Black でフォーマット
- 行の長さは 88 文字以内
- 型ヒントを使用

### 2. 命名規則
- 変数・関数: `snake_case`
- クラス: `PascalCase`
- 定数: `UPPER_CASE`
- プライベート: `_leading_underscore`

### 3. ドキュメント
```python
def your_function(param1: str, param2: int) -> bool:
    """
    関数の説明
    
    Args:
        param1: パラメータ1の説明
        param2: パラメータ2の説明
    
    Returns:
        戻り値の説明
    
    Raises:
        ValueError: エラーの説明
    """
    pass
```

## 🐛 バグレポート

バグを発見した場合は、以下の情報を含めて Issue を作成してください：

### テンプレート
```markdown
## バグの説明
バグの詳細な説明

## 再現手順
1. ...
2. ...
3. ...

## 期待される動作
期待していた動作の説明

## 実際の動作
実際に起こった動作の説明

## 環境
- OS: [例: macOS 14.0]
- Python バージョン: [例: 3.11.0]
- discord.py バージョン: [例: 2.3.2]

## 追加情報
スクリーンショット、ログなど
```

## 💡 機能提案

新機能の提案は以下のテンプレートを使用してください：

```markdown
## 機能の説明
提案する機能の詳細な説明

## 動機・背景
なぜこの機能が必要なのか

## 詳細な設計
実装方法の提案（任意）

## 代替案
他に考えられる解決方法（任意）

## 追加情報
参考資料、モックアップなど
```

## 🎯 優先度の高い貢献エリア

現在、以下のエリアで貢献を特に歓迎しています：

1. **テストカバレッジの向上**
2. **ドキュメントの改善**
3. **パフォーマンス最適化**
4. **新しい AI サービスの実装**
5. **国際化対応**

## 📞 サポート

質問や相談がある場合は：

1. **Discord**: `#dev-help` チャンネル
2. **GitHub Discussions**: 一般的な議論
3. **GitHub Issues**: バグレポート・機能提案

## 🏆 貢献者の認識

貢献者は以下の方法で認識されます：

- README の Contributors セクションに追加
- Discord での @Contributor ロール付与
- 月次の貢献者ハイライト

## 📜 ライセンス

このプロジェクトに貢献することで、あなたの貢献が MIT ライセンスの下で公開されることに同意したものとみなされます。

---

貢献してくださり、ありがとうございます！🚀