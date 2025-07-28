"""
多言語対応システム - AI Forge Community
Internationalization (i18n) system for multi-language support
"""

import os
import json
from typing import Dict, Any, Optional
from enum import Enum

class SupportedLanguages(Enum):
    """サポートされている言語"""
    JAPANESE = "ja"
    ENGLISH = "en"
    KOREAN = "ko"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"

class I18nManager:
    """多言語対応マネージャー"""
    
    def __init__(self, default_language: str = "ja"):
        self.default_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()
    
    def load_translations(self):
        """翻訳ファイルを読み込み"""
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
        
        # 翻訳ディレクトリが存在しない場合は作成
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)
        
        # 各言語の翻訳ファイルを読み込み
        for lang in SupportedLanguages:
            lang_file = os.path.join(translations_dir, f"{lang.value}.json")
            
            if os.path.exists(lang_file):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang.value] = json.load(f)
                except Exception as e:
                    print(f"翻訳ファイル読み込みエラー ({lang.value}): {e}")
                    self.translations[lang.value] = {}
            else:
                self.translations[lang.value] = {}
    
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """翻訳テキストを取得"""
        if language is None:
            language = self.default_language
        
        # 指定された言語の翻訳を取得
        lang_translations = self.translations.get(language, {})
        
        # ネストされたキーを処理（例: "bot.ready"）
        keys = key.split('.')
        text = lang_translations
        
        for k in keys:
            if isinstance(text, dict) and k in text:
                text = text[k]
            else:
                # キーが見つからない場合はデフォルト言語を試す
                if language != self.default_language:
                    default_translations = self.translations.get(self.default_language, {})
                    text = default_translations
                    for k2 in keys:
                        if isinstance(text, dict) and k2 in text:
                            text = text[k2]
                        else:
                            text = key
                            break
                else:
                    text = key
                break
        
        # テキストが辞書の場合はキーをそのまま返す
        if isinstance(text, dict):
            text = key
        
        # プレースホルダーを置換
        try:
            return str(text).format(**kwargs)
        except (KeyError, ValueError):
            return str(text)
    
    def get_language_name(self, language_code: str, display_language: str = None) -> str:
        """言語名を取得"""
        if display_language is None:
            display_language = self.default_language
        
        language_names = {
            "ja": {
                "ja": "日本語", "en": "英語", "ko": "韓国語",
                "zh-cn": "中国語（簡体字）", "zh-tw": "中国語（繁体字）",
                "es": "スペイン語", "fr": "フランス語", "de": "ドイツ語"
            },
            "en": {
                "ja": "Japanese", "en": "English", "ko": "Korean",
                "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)",
                "es": "Spanish", "fr": "French", "de": "German"
            }
        }
        
        return language_names.get(display_language, {}).get(language_code, language_code)
    
    def detect_language_from_text(self, text: str) -> str:
        """テキストから言語を検出（簡易版）"""
        # 日本語文字（ひらがな、カタカナ、漢字）の検出
        japanese_chars = sum(1 for char in text if '\u3040' <= char <= '\u309F' or 
                           '\u30A0' <= char <= '\u30FF' or 
                           '\u4E00' <= char <= '\u9FAF')
        
        # 韓国語文字（ハングル）の検出
        korean_chars = sum(1 for char in text if '\uAC00' <= char <= '\uD7AF')
        
        # 中国語文字（漢字のみ、日本語と重複するため簡易判定）
        chinese_chars = sum(1 for char in text if '\u4E00' <= char <= '\u9FAF')
        
        total_chars = len(text)
        if total_chars == 0:
            return self.default_language
        
        # 日本語の判定（ひらがな・カタカナがあれば日本語）
        if japanese_chars > 0 and (japanese_chars / total_chars) > 0.1:
            return "ja"
        
        # 韓国語の判定
        if korean_chars > 0 and (korean_chars / total_chars) > 0.1:
            return "ko"
        
        # 中国語の判定（漢字のみで日本語文字がない場合）
        if chinese_chars > 0 and japanese_chars == 0 and (chinese_chars / total_chars) > 0.3:
            return "zh-cn"
        
        # デフォルトは英語
        return "en"

# グローバルインスタンス
i18n = I18nManager()

def _(key: str, language: str = None, **kwargs) -> str:
    """翻訳テキスト取得のショートカット関数"""
    return i18n.get_text(key, language, **kwargs)

def get_user_language(user_id: str) -> str:
    """ユーザーの言語設定を取得（将来的にデータベースから）"""
    # 現在は日本語をデフォルトとして返す
    # 将来的にはユーザー設定をデータベースから取得
    return "ja"

def set_user_language(user_id: str, language: str) -> bool:
    """ユーザーの言語設定を保存（将来的にデータベースに）"""
    # 現在は何もしない（将来的にデータベースに保存）
    return True