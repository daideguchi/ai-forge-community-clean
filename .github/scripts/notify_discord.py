#!/usr/bin/env python3
"""
GitHub Actions から Discord に通知を送信するスクリプト
"""

import os
import json
import requests
from datetime import datetime

def send_discord_notification():
    """Discord に PR レビュー完了通知を送信"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    pr_number = os.getenv('PR_NUMBER')
    pr_title = os.getenv('PR_TITLE')
    pr_author = os.getenv('PR_AUTHOR')
    pr_url = os.getenv('PR_URL')
    
    if not webhook_url:
        print("Discord Webhook URL が設定されていません")
        return
    
    # Discord Embed を作成
    embed = {
        "title": f"🤖 AI コードレビュー完了",
        "description": f"**PR #{pr_number}**: {pr_title}",
        "color": 0x00ff00,  # 緑色
        "fields": [
            {
                "name": "👤 作成者",
                "value": pr_author,
                "inline": True
            },
            {
                "name": "🔗 リンク",
                "value": f"[Pull Request を見る]({pr_url})",
                "inline": True
            }
        ],
        "footer": {
            "text": "AI Code Reviewer"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("✅ Discord 通知を送信しました")
        else:
            print(f"❌ Discord 通知エラー: {response.status_code}")
    except Exception as e:
        print(f"❌ Discord 通知送信エラー: {e}")

if __name__ == "__main__":
    send_discord_notification()