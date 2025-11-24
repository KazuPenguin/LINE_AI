"""
LINE通知モジュール
LINE Messaging APIを使用してメッセージを送信
"""

import os
import requests
from typing import List


class LINENotifier:
    def __init__(self, access_token: str = None, user_id: str = None):
        self.access_token = access_token or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.user_id = user_id or os.getenv("LINE_USER_ID")

        if not self.access_token:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")

        if not self.user_id:
            raise ValueError("LINE_USER_ID が設定されていません")

        self.api_url = "https://api.line.me/v2/bot/message/push"
        self.max_length = 4500  # LINEの文字数制限を考慮（実際は5000文字だが余裕を持つ）

    def send_message(self, message: str) -> bool:
        """
        LINEにメッセージを送信
        長すぎる場合は自動的に分割して送信
        """
        if not message:
            print("⚠️ 送信するメッセージが空です")
            return False

        # メッセージを分割
        message_parts = self._split_message(message)

        print(f"📤 LINEにメッセージを送信中... ({len(message_parts)}件)")

        # 各パートを送信
        for i, part in enumerate(message_parts, 1):
            success = self._send_single_message(part)
            if not success:
                print(f"❌ メッセージ {i}/{len(message_parts)} の送信に失敗しました")
                return False
            print(f"✅ メッセージ {i}/{len(message_parts)} 送信完了")

        print("🎉 すべてのメッセージ送信完了\n")
        return True

    def _send_single_message(self, text: str) -> bool:
        """
        単一のメッセージを送信
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = {
            "to": self.user_id,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return True
            else:
                print(f"❌ LINE API エラー: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 送信中にエラーが発生: {e}")
            return False

    def _split_message(self, message: str) -> List[str]:
        """
        長いメッセージを適切な長さに分割
        区切り線や改行を考慮して自然な位置で分割
        """
        if len(message) <= self.max_length:
            return [message]

        parts = []
        current_part = ""
        lines = message.split("\n")

        for line in lines:
            # 次の行を追加してもmax_lengthを超えない場合
            if len(current_part) + len(line) + 1 <= self.max_length:
                current_part += line + "\n"
            else:
                # 現在のパートを保存して新しいパートを開始
                if current_part:
                    parts.append(current_part.rstrip())
                current_part = line + "\n"

        # 最後のパートを追加
        if current_part:
            parts.append(current_part.rstrip())

        return parts

    def send_error_notification(self, error_message: str) -> bool:
        """
        エラー通知を送信
        """
        notification = f"""⚠️ ボット実行エラー

エラー内容:
{error_message}

システム管理者に連絡してください。"""

        return self.send_message(notification)


if __name__ == "__main__":
    # テスト実行
    notifier = LINENotifier()

    test_message = """━━━━━━━━━━━━━━━━
📅 テストメッセージ
━━━━━━━━━━━━━━━━

🔬 これはLINE通知のテストメッセージです

✅ 正常に動作していれば、このメッセージが届いているはずです。

━━━━━━━━━━━━━━━━
💡 テスト完了
LINE通知機能は正常に動作しています！
"""

    result = notifier.send_message(test_message)
    print(f"送信結果: {'成功' if result else '失敗'}")
