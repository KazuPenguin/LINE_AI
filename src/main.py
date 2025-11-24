"""
AIトレンド収集・要約LINEボット
メインエントリーポイント
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from fetcher import DataFetcher
from summarizer import Summarizer
from notifier import LINENotifier


def main():
    """
    メイン処理
    1. データ収集
    2. 要約生成
    3. LINE通知
    """
    print("=" * 50)
    print("🤖 AIトレンド収集・要約LINEボット 起動")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()

    # 環境変数の読み込み
    # .envファイルが存在する場合のみ読み込み（ローカル開発用）
    # GitHub Actions等のCI環境では、Secretsから直接環境変数が設定される
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        print("📄 .envファイルから環境変数を読み込みます")
        load_dotenv(env_file)
    else:
        print("📄 環境変数は既に設定されています（CI環境）")

    # 環境変数のチェック
    required_vars = [
        "OPENAI_API_KEY",
        "LINE_CHANNEL_ACCESS_TOKEN",
        "LINE_USER_ID"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        error_msg = f"必須の環境変数が設定されていません: {', '.join(missing_vars)}"
        print(f"❌ {error_msg}")
        print(f"💡 ローカル環境: .envファイルを作成してください")
        print(f"💡 GitHub Actions: Secretsが正しく設定されているか確認してください")
        sys.exit(1)

    try:
        # ステップ1: データ収集
        print("📊 ステップ1: データ収集")
        print("-" * 50)
        fetcher = DataFetcher()
        data = fetcher.fetch_all()

        # データが空でないか確認
        total_items = len(data['papers']) + len(data['trends']) + len(data['economic'])
        print(f"\n📈 収集完了: 合計 {total_items} 件")

        if total_items == 0:
            print("⚠️ データが1件も取得できませんでした")
            # それでも通知は送る
            notifier = LINENotifier()
            notifier.send_message("📭 本日は特筆すべきAIニュースが見つかりませんでした。次回をお楽しみに！")
            print("✅ 処理完了（データなし通知を送信）")
            return

        # ステップ2: 要約生成
        print("\n" + "=" * 50)
        print("📝 ステップ2: 要約生成")
        print("-" * 50)
        summarizer = Summarizer()
        summary = summarizer.create_summary(data)

        # 要約結果をプレビュー
        print("\n--- 生成された要約（プレビュー） ---")
        preview = summary[:500] + "..." if len(summary) > 500 else summary
        print(preview)
        print(f"\n文字数: {len(summary)}文字")

        # ステップ3: LINE通知
        print("\n" + "=" * 50)
        print("📲 ステップ3: LINE通知")
        print("-" * 50)
        notifier = LINENotifier()
        success = notifier.send_message(summary)

        # 結果
        print("\n" + "=" * 50)
        if success:
            print("✅ すべての処理が正常に完了しました！")
            print("=" * 50)
        else:
            print("❌ LINE通知の送信に失敗しました")
            print("=" * 50)
            sys.exit(1)

    except Exception as e:
        error_msg = f"予期しないエラーが発生しました: {str(e)}"
        print(f"\n❌ {error_msg}")
        print("=" * 50)

        # エラー通知を試みる
        try:
            notifier = LINENotifier()
            notifier.send_error_notification(error_msg)
        except:
            pass  # エラー通知も失敗した場合は何もしない

        sys.exit(1)


if __name__ == "__main__":
    main()
