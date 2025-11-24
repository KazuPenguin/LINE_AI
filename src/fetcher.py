"""
データ収集モジュール
Arxivからの論文収集とDuckDuckGoを使ったWeb検索
"""

import arxiv
from datetime import datetime, timedelta
from ddgs import DDGS
from typing import List, Dict
import time


class DataFetcher:
    def __init__(self):
        self.ddgs = DDGS()
        self.days_back = 3

    def fetch_arxiv_papers(self) -> List[Dict]:
        """
        Arxivから過去3日間のAI/LLM関連論文を取得
        カテゴリ: cs.CL, cs.AI, cs.LG, cs.CV, cs.SE
        """
        categories = ["cs.CL", "cs.AI", "cs.LG", "cs.CV", "cs.SE"]
        papers = []
        seen_ids = set()

        # 過去3日間の日付を計算
        cutoff_date = datetime.now() - timedelta(days=self.days_back)

        print(f"🔍 Arxiv論文を検索中... (過去{self.days_back}日間)")

        # arxiv Clientを使用
        client = arxiv.Client()

        for category in categories:
            try:
                # 各カテゴリから検索
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=10,  # 余裕を持って取得
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )

                count = 0
                for result in client.results(search):
                    # 提出日が3日以内かチェック
                    if result.published.replace(tzinfo=None) < cutoff_date:
                        continue

                    # 重複チェック
                    if result.entry_id in seen_ids:
                        continue

                    seen_ids.add(result.entry_id)
                    papers.append({
                        "title": result.title,
                        "abstract": result.summary,
                        "url": result.entry_id,
                        "published": result.published.strftime("%Y-%m-%d"),
                        "category": category
                    })

                    count += 1
                    if count >= 5:  # 各カテゴリから最大5件
                        break

                print(f"  - {category}: {count}件取得")
                time.sleep(1)  # APIに負荷をかけないよう待機

            except Exception as e:
                print(f"  ⚠️ {category}の取得中にエラー: {e}")
                continue

        print(f"✅ 合計 {len(papers)}件の論文を取得しました\n")
        return papers

    def fetch_web_trends(self) -> List[Dict]:
        """
        DuckDuckGoでAI関連の新サービス・トレンド情報を検索
        """
        queries = [
            "AI new tool launch 2025",
            "LLM service announcement",
            "ChatGPT alternative new",
            "Generative AI product launch"
        ]

        results = []
        seen_urls = set()

        print("🌐 Web上の新サービス・トレンドを検索中...")

        for query in queries:
            try:
                # DuckDuckGo検索実行
                search_results = self.ddgs.text(
                    query,
                    max_results=3
                )

                for item in search_results:
                    if item["href"] in seen_urls:
                        continue

                    seen_urls.add(item["href"])
                    results.append({
                        "title": item["title"],
                        "snippet": item["body"],
                        "url": item["href"]
                    })

                time.sleep(2)  # レート制限対策

            except Exception as e:
                print(f"  ⚠️ 検索エラー ({query}): {e}")
                continue

        print(f"✅ {len(results)}件のトレンド情報を取得しました\n")
        return results[:10]  # 最大10件

    def fetch_economic_news(self) -> List[Dict]:
        """
        AI業界の経済・ビジネスニュースを検索
        """
        queries = [
            "OpenAI funding news 2025",
            "NVIDIA AI stock market",
            "AI startup investment",
            "Microsoft AI partnership"
        ]

        results = []
        seen_urls = set()

        print("💰 経済・ビジネスニュースを検索中...")

        for query in queries:
            try:
                search_results = self.ddgs.text(
                    query,
                    max_results=2
                )

                for item in search_results:
                    if item["href"] in seen_urls:
                        continue

                    seen_urls.add(item["href"])
                    results.append({
                        "title": item["title"],
                        "snippet": item["body"],
                        "url": item["href"]
                    })

                time.sleep(2)

            except Exception as e:
                print(f"  ⚠️ 検索エラー ({query}): {e}")
                continue

        print(f"✅ {len(results)}件の経済ニュースを取得しました\n")
        return results[:8]  # 最大8件

    def fetch_all(self) -> Dict:
        """
        すべてのデータを収集して返す
        """
        return {
            "papers": self.fetch_arxiv_papers(),
            "trends": self.fetch_web_trends(),
            "economic": self.fetch_economic_news()
        }


if __name__ == "__main__":
    # テスト実行
    fetcher = DataFetcher()
    data = fetcher.fetch_all()

    print("\n=== 取得結果サマリー ===")
    print(f"論文: {len(data['papers'])}件")
    print(f"トレンド: {len(data['trends'])}件")
    print(f"経済ニュース: {len(data['economic'])}件")
