"""
要約・整形モジュール
OpenAI APIを使用して収集データをLINE向けに要約・整形
"""

import os
import json
from openai import OpenAI
from typing import Dict


class Summarizer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"

    def create_summary(self, data: Dict) -> str:
        """
        収集データをLINE用の読みやすい要約テキストに変換
        """
        papers = data.get("papers", [])
        trends = data.get("trends", [])
        economic = data.get("economic", [])

        # データが少なすぎる場合のチェック
        if len(papers) == 0 and len(trends) == 0 and len(economic) == 0:
            return "📭 本日は特筆すべきAIニュースが見つかりませんでした。次回をお楽しみに！"

        # プロンプト用のデータ整形
        papers_text = self._format_papers(papers)
        trends_text = self._format_trends(trends)
        economic_text = self._format_economic(economic)

        # システムプロンプト
        system_prompt = """あなたはテック業界の専門アナリストです。
渡された「論文リスト」「Webニュースリスト」「経済ニュースリスト」から、
エンジニアが知っておくべき重要な情報を厳選し、LINEで読みやすい形式に要約してください。

出力フォーマット:
━━━━━━━━━━━━━━━━
📅 [日付]のAIダイジェスト
━━━━━━━━━━━━━━━━

🔬 注目の論文 (3選)
━━━━━━━━━━━━━━━━
1. [論文タイトルの日本語要約]
   📝 [1行での要約]
   🔗 [URL]

2. [論文タイトルの日本語要約]
   📝 [1行での要約]
   🔗 [URL]

3. [論文タイトルの日本語要約]
   📝 [1行での要約]
   🔗 [URL]

🚀 話題のサービス・トレンド (3選)
━━━━━━━━━━━━━━━━
1. [サービス名/トピック]
   📝 [概要]
   🔗 [URL]

2. [サービス名/トピック]
   📝 [概要]
   🔗 [URL]

3. [サービス名/トピック]
   📝 [概要]
   🔗 [URL]

💰 経済・ビジネスニュース (2選)
━━━━━━━━━━━━━━━━
1. [ニュース内容の要約]
   🔗 [URL]

2. [ニュース内容の要約]
   🔗 [URL]

━━━━━━━━━━━━━━━━
💡 総評
[1〜2文で全体的なトレンドをコメント]

注意事項:
- 各セクションは必ず指定された件数を選出すること（データが足りない場合は可能な範囲で）
- タイトルや概要は簡潔に、要点を押さえること
- 専門用語は適度に使いつつも、読みやすさを優先
- URLは必ず含めること
- 絵文字を適切に使用して視認性を高めること
"""

        # ユーザープロンプト
        user_prompt = f"""以下のデータから、AIエンジニア向けのダイジェストを作成してください。

【論文リスト】
{papers_text}

【Webトレンド・新サービス】
{trends_text}

【経済・ビジネスニュース】
{economic_text}

上記の情報から、最も重要で興味深いものを厳選して要約してください。
"""

        print("🤖 OpenAI APIで要約を生成中...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            summary = response.choices[0].message.content
            print("✅ 要約生成完了\n")
            return summary

        except Exception as e:
            print(f"❌ OpenAI APIエラー: {e}")
            return f"⚠️ 要約の生成中にエラーが発生しました: {str(e)}"

    def _format_papers(self, papers: list) -> str:
        """論文データをテキスト形式に整形"""
        if not papers:
            return "（論文データなし）"

        formatted = []
        for i, paper in enumerate(papers[:10], 1):  # 最大10件
            formatted.append(f"""
論文 {i}:
タイトル: {paper['title']}
カテゴリ: {paper['category']}
投稿日: {paper['published']}
概要: {paper['abstract'][:300]}...
URL: {paper['url']}
""")
        return "\n".join(formatted)

    def _format_trends(self, trends: list) -> str:
        """トレンドデータをテキスト形式に整形"""
        if not trends:
            return "（トレンドデータなし）"

        formatted = []
        for i, item in enumerate(trends[:10], 1):
            formatted.append(f"""
トレンド {i}:
タイトル: {item['title']}
内容: {item['snippet']}
URL: {item['url']}
""")
        return "\n".join(formatted)

    def _format_economic(self, economic: list) -> str:
        """経済ニュースをテキスト形式に整形"""
        if not economic:
            return "（経済ニュースなし）"

        formatted = []
        for i, item in enumerate(economic[:8], 1):
            formatted.append(f"""
ニュース {i}:
タイトル: {item['title']}
内容: {item['snippet']}
URL: {item['url']}
""")
        return "\n".join(formatted)


if __name__ == "__main__":
    # テスト用のダミーデータ
    test_data = {
        "papers": [
            {
                "title": "Test Paper",
                "abstract": "This is a test abstract",
                "url": "https://arxiv.org/abs/test",
                "published": "2025-01-01",
                "category": "cs.AI"
            }
        ],
        "trends": [
            {
                "title": "New AI Tool Launched",
                "snippet": "A revolutionary AI tool...",
                "url": "https://example.com"
            }
        ],
        "economic": [
            {
                "title": "AI Market Growth",
                "snippet": "AI market continues to grow...",
                "url": "https://example.com"
            }
        ]
    }

    summarizer = Summarizer()
    summary = summarizer.create_summary(test_data)
    print(summary)
