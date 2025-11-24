# AIトレンド収集・要約LINEボット

Arxiv論文、Web/SNS情報、経済ニュースから最新のAI/LLM関連情報を自動収集し、OpenAI APIで要約してLINEに通知するサーバーレスボットです。

## 特徴

- 📚 **学術論文**: Arxivから最新のAI研究論文を収集（cs.CL, cs.AI, cs.LG, cs.CV, cs.SE）
- 🌐 **Webトレンド**: DuckDuckGoで新サービス・製品リリース情報を検索
- 💰 **経済ニュース**: AI業界の投資・市場動向を追跡
- 🤖 **自動要約**: OpenAI GPT-4o-miniで読みやすく整形
- 📱 **LINE通知**: 3日に1回、自動的にLINEにダイジェストを配信
- 🔄 **完全自動化**: GitHub Actionsでサーバーレス実行（無料）
- ⚡ **高速パッケージ管理**: uvを使用した高速なセットアップと依存関係管理

## 実装前の準備（必須）

以下の3つのAPIキー・トークンを取得する必要があります。

### 1. OpenAI API キーの取得

**手順:**
1. [OpenAI Platform](https://platform.openai.com/)にアクセスしてサインアップ
2. 画面右上のアカウントメニューから「API keys」を選択
3. 「Create new secret key」をクリック
4. キー名を入力（例: LINE_AI_Bot）
5. 生成された`sk-proj-...`で始まるキーをコピーして保存
   - **重要**: このキーは1回しか表示されないため、必ずメモ帳等に保存

**課金設定:**
- 初回利用時は支払い方法の登録が必要
- `Settings` → `Billing` → `Payment methods` から登録
- 使用量に応じた従量課金（このボットは月$0.10〜0.30程度）

### 2. LINE Messaging API の設定

#### 2-1. LINE Developersでチャネル作成

**手順:**
1. [LINE Developers](https://developers.line.biz/)にアクセス
2. LINEアカウントでログイン
3. 右上の「コンソール」をクリック
4. 「プロバイダー」を作成（初回のみ）
   - プロバイダー名: 任意（例: MyAIBots）
5. 「チャネルを作成」をクリック
6. 「Messaging API」を選択
7. 必要事項を入力:
   - チャネル名: `AIトレンドボット`
   - チャネル説明: `AI情報を自動収集するボット`
   - カテゴリ: 「ニュース」または「ビジネス」
   - メールアドレス: あなたのメールアドレス
8. 利用規約に同意して「作成」

#### 2-2. Channel Access Token の取得

1. 作成したチャネルの設定画面を開く
2. 「Messaging API設定」タブを選択
3. 下にスクロールして「チャネルアクセストークン」セクションを探す
4. 「発行」ボタンをクリック
5. 生成された長いトークンをコピーして保存
   - 形式: 英数字の長い文字列（約170文字）

#### 2-3. Webhook設定（重要）

1. 同じ「Messaging API設定」タブで以下を設定:
   - **Webhook URL**: オフのまま（このボットはpush送信のみ使用）
   - **応答メッセージ**: オフに設定
   - **あいさつメッセージ**: オフに設定
   - **Webhook の再送**: オフのまま

#### 2-4. ボットを友だち追加

1. 「Messaging API設定」タブの上部にあるQRコードをスマホで読み取る
2. または、「Bot basic ID」（@で始まるID）を検索して友だち追加
3. トーク画面が開くことを確認

#### 2-5. User ID の取得

**方法1: LINE Official Account Manager を使う（推奨）**
1. [LINE Official Account Manager](https://manager.line.biz/)にアクセス
2. 作成したアカウントを選択
3. 左メニューの「分析」→「友だち」を選択
4. 友だちリストから自分のアカウントを見つける
5. User ID（`U`で始まる33文字）をコピー

**方法2: Webhook経由で取得（上級者向け）**
1. 一時的にWebhookを有効化
2. ボットにメッセージを送信
3. Webhookログから`userId`を取得
4. Webhookを再びオフにする

**方法3: LINE公式アカウントのチャットから**
1. スマホでボットに任意のメッセージを送信
2. LINE Developersコンソールの「Messaging API設定」で「統計情報」を確認
3. または、開発者モードで直接確認（技術的知識が必要）

> **注意**: User IDは`U`で始まる33文字の英数字です。間違えないようにコピーしてください。

### 3. GitHub アカウント

- [GitHub](https://github.com/)でアカウント作成（無料）
- Public リポジトリを作成すれば、GitHub Actions完全無料で使用可能

---

## セットアップ手順（実装開始）

### 1. uvのインストール

このプロジェクトはuvでパッケージ管理を行っています。まずuvをインストールしてください。

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**その他のインストール方法:**
- Homebrew: `brew install uv`
- pipx: `pipx install uv`

詳細は[uv公式ドキュメント](https://docs.astral.sh/uv/)を参照してください。

### 2. リポジトリのクローン

```bash
git clone <このリポジトリのURL>
cd LINE_AI
```

### 3. 依存関係のインストール

```bash
# 依存関係のインストールと仮想環境の自動作成
uv sync
```

uvが自動的に以下を行います:
- Python 3.11の仮想環境を作成（`.python-version`に基づく）
- `pyproject.toml`に記載された依存関係をインストール
- `uv.lock`ファイルを生成（初回のみ）

**uvの利点:**
- pipの10〜100倍高速なインストール
- 自動的な仮想環境管理
- ロックファイルによる再現可能なビルド
- Pythonバージョンの自動検出とインストール

### 4. 環境変数の設定

`.env.example`をコピーして`.env`を作成:

```bash
cp .env.example .env
```

`.env`ファイルを編集して、以下の情報を入力:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
LINE_USER_ID=Uxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. ローカルでのテスト実行

```bash
cd src
uv run python main.py
```

または、仮想環境を有効化してから実行:

```bash
# 仮想環境を有効化
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 実行
cd src
python main.py
```

正常に動作すれば、LINEにテストメッセージが届きます。

## GitHub Actionsでの自動実行設定

### 1. GitHubリポジトリの作成

1. [GitHub](https://github.com/)にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ設定:
   - Repository name: `LINE_AI` (任意)
   - Public または Private を選択
   - **重要**: 「Add a README file」のチェックは外す（すでにREADMEがあるため）
4. 「Create repository」をクリック

### 2. ローカルからプッシュ

GitHubに表示される手順に従って、以下を実行:

```bash
# Gitリポジトリの初期化
git init

# すべてのファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit: AI Trend Bot"

# メインブランチの作成
git branch -M main

# リモートリポジトリの追加（URLは自分のものに変更）
git remote add origin https://github.com/YOUR_USERNAME/LINE_AI.git

# プッシュ
git push -u origin main
```

### 3. GitHub Secretsの設定（重要）

GitHub Actionsで自動実行する際、環境変数は`.env`ファイルではなく、**GitHub Secrets**から読み込まれます。

**環境変数の仕組み:**
- **ローカル開発**: `.env`ファイルから読み込み
- **GitHub Actions**: GitHub Secretsから直接環境変数として設定
- どちらの環境でも同じコードが動作します

**手順:**
1. GitHubのリポジトリページを開く
2. 「Settings」タブをクリック（リポジトリ名の下にあるタブ）
3. 左サイドバーの「Secrets and variables」を展開
4. 「Actions」をクリック
5. 「New repository secret」ボタンをクリック

**以下の3つのSecretを追加:**

#### Secret 1: OPENAI_API_KEY
- Name: `OPENAI_API_KEY`（大文字小文字を正確に）
- Secret: OpenAIで取得した`sk-proj-...`で始まるキー
- 「Add secret」をクリック

#### Secret 2: LINE_CHANNEL_ACCESS_TOKEN
- Name: `LINE_CHANNEL_ACCESS_TOKEN`（大文字小文字を正確に）
- Secret: LINE Developersで取得した長いトークン（約170文字）
- 「Add secret」をクリック

#### Secret 3: LINE_USER_ID
- Name: `LINE_USER_ID`（大文字小文字を正確に）
- Secret: `U`で始まる33文字のUser ID
- 「Add secret」をクリック

**重要:**
- Secret名は大文字小文字を区別します
- `.env`ファイルと全く同じ名前にしてください
- Secretの値は登録後は見えなくなります（セキュリティのため）
- GitHub Actionsの実行ログにも値は表示されません（マスクされます）

**確認:**
```
✓ OPENAI_API_KEY
✓ LINE_CHANNEL_ACCESS_TOKEN
✓ LINE_USER_ID
```
上記3つが表示されていればOK

### 4. GitHub Actionsの有効化

1. リポジトリの「Actions」タブをクリック
2. 「I understand my workflows, go ahead and enable them」をクリック（初回のみ）
3. 左サイドバーに「AI Trend Collection Bot」が表示されることを確認

### 5. 手動でテスト実行

自動実行を待つ前に、まず手動でテストします:

1. 「Actions」タブを開く
2. 左サイドバーの「AI Trend Collection Bot」をクリック
3. 右側の「Run workflow」ボタンをクリック
4. ブランチが`main`になっていることを確認
5. 「Run workflow」をクリック
6. 実行が開始されるので、ステータスを確認
7. 正常終了（緑のチェックマーク）すれば、LINEにメッセージが届いているはず

**エラーが出た場合:**
- ワークフローをクリックして詳細ログを確認
- 「📄 環境変数は既に設定されています（CI環境）」と表示されるか確認
- 「❌ 必須の環境変数が設定されていません」が出た場合:
  - Secretsが正しく設定されているか再確認
  - Secret名が大文字小文字含めて正確か確認（`LINE_USER_ID` ≠ `LINE_USERID`）
  - Secretの値にスペースや改行が入っていないか確認

### 6. 自動実行スケジュール

`.github/workflows/run_bot.yml`の設定により、以下のスケジュールで自動実行されます:

```yaml
schedule:
  - cron: '0 0 */3 * *'  # 3日に1回、UTC 0:00（日本時間 9:00）
```

**スケジュール例:**
- 毎日実行: `'0 0 * * *'`
- 毎週月曜日: `'0 0 * * 1'`
- 毎月1日: `'0 0 1 * *'`

**注意事項:**
- GitHub Actionsのcronは必ずしも正確な時刻に実行されるわけではありません（混雑状況による）
- 最大10〜15分程度の遅延が発生する可能性があります
- 手動実行はいつでも可能です

## ディレクトリ構成

```
LINE_AI/
├── .github/
│   └── workflows/
│       └── run_bot.yml       # GitHub Actions設定
├── src/
│   ├── __init__.py
│   ├── main.py               # メインエントリーポイント
│   ├── fetcher.py            # データ収集（Arxiv + Web検索）
│   ├── summarizer.py         # OpenAI要約処理
│   └── notifier.py           # LINE通知
├── pyproject.toml            # プロジェクト設定とPython依存関係
├── uv.lock                   # 依存関係のロックファイル（uv syncで自動生成）
├── .python-version           # 使用するPythonバージョン
├── requirements.txt          # 互換性のため残置（pip用）
├── .env.example              # 環境変数テンプレート
└── README.md                 # このファイル
```

## モジュール詳細

### fetcher.py
- **Arxiv検索**: 過去3日間の論文を各カテゴリから最大5件取得
- **Web検索**: DuckDuckGoで新サービス・トレンド情報を検索
- **経済ニュース**: AI関連の投資・市場ニュースを取得

### summarizer.py
- 収集データをOpenAI APIに送信
- システムプロンプトで「テック業界アナリスト」として動作
- 論文3選、トレンド3選、経済ニュース2選を厳選して要約
- LINEで読みやすい形式に整形（絵文字使用）

### notifier.py
- LINE Messaging APIでPush Message送信
- 文字数制限（5000文字）を考慮して自動分割
- エラー通知機能付き

## 実装完了チェックリスト

実装が正しく完了しているか、以下のチェックリストで確認してください。

### フェーズ1: API・トークンの取得
- [ ] OpenAI API キーを取得した（`sk-proj-...`で始まる）
- [ ] OpenAIアカウントに支払い方法を登録した
- [ ] LINE Developersでチャネルを作成した
- [ ] LINE Channel Access Tokenを取得した（約170文字）
- [ ] LINE ボットを友だち追加した
- [ ] LINE User IDを取得した（`U`で始まる33文字）
- [ ] 上記3つの値をメモ帳等に保存した

### フェーズ2: ローカル環境でのテスト
- [ ] uvをインストールした
- [ ] リポジトリをクローンまたはダウンロードした
- [ ] `uv sync`で依存関係をインストールした
- [ ] `.env.example`をコピーして`.env`を作成した
- [ ] `.env`ファイルに3つのキー・トークンを記入した
- [ ] `cd src && uv run python main.py`でローカル実行した
- [ ] エラーなく実行完了した
- [ ] LINEにテストメッセージが届いた

### フェーズ3: GitHub設定
- [ ] GitHubアカウントを作成した
- [ ] 新規リポジトリを作成した（Public または Private）
- [ ] ローカルから`git push`でコードをアップロードした
- [ ] GitHub Secretsに以下の3つを登録した:
  - [ ] `OPENAI_API_KEY`
  - [ ] `LINE_CHANNEL_ACCESS_TOKEN`
  - [ ] `LINE_USER_ID`
- [ ] GitHub Actionsを有効化した
- [ ] 「Run workflow」で手動実行した
- [ ] ワークフローが緑のチェックマークで完了した
- [ ] LINEにメッセージが届いた

### フェーズ4: 自動実行の確認
- [ ] `.github/workflows/run_bot.yml`のcron設定を確認した
- [ ] 次回の自動実行日時を把握している
- [ ] （オプション）cron設定を自分の好みに変更した

### 運用開始
- [ ] すべてのチェック項目が完了している
- [ ] 定期的にGitHub Actionsの実行ログを確認する予定
- [ ] OpenAI APIの使用量を定期的に確認する予定

---

**すべてチェックが完了したら、実装完了です！**
3日に1回（または設定したスケジュール）で自動的にAI情報が届きます。

---

## トラブルシューティング

### Q: LINEにメッセージが届かない

**原因1: LINE_USER_IDが間違っている**
- User IDは`U`で始まる33文字の英数字です
- Bot IDやChannel IDではありません
- 確認方法:
  1. ボットに何かメッセージを送信
  2. LINE Developersコンソール → 「Messaging API設定」
  3. 一時的にWebhookを有効にして、ログを確認

**原因2: Channel Access Tokenが間違っている**
- トークンは約170文字の長い文字列です
- 発行時に全文コピーできているか確認
- 再発行して試してみる

**原因3: LINE側の設定が間違っている**
- 「応答メッセージ」がオフになっているか確認
- Webhookがオフになっているか確認（このボットはpush送信のみ）

**原因4: GitHub Secretsの名前が間違っている**
- Secretの名前は大文字小文字を区別します
- `LINE_USER_ID`と`LINE_USERID`は別物です
- スペルミスがないか再確認
- GitHubの`Settings` → `Secrets and variables` → `Actions`で確認

**原因5: Secretの値にスペースや改行が含まれている**
- Secret登録時に余分なスペースや改行をコピーしていないか確認
- 値を再登録してみる

### Q: OpenAI APIエラーが出る
- API Keyが有効か確認
- OpenAIアカウントに残高があるか確認
- レート制限に達していないか確認

### Q: Arxiv論文が0件
- 過去3日間に対象カテゴリの論文投稿がない可能性があります（正常動作）
- カテゴリを増やすか、検索期間を延ばすことで対応可能

### Q: Web検索でエラーが出る
- DuckDuckGoにレート制限がかかっている可能性
- `fetcher.py`の`time.sleep()`の秒数を増やして対応

### Q: LINE User IDの取得方法がわからない

**最も簡単な方法: 一時的にUser IDを表示するコードを追加**

1. `src/notifier.py`の`send_message`メソッドの最初に以下を追加:
```python
print(f"DEBUG: User ID = {self.user_id}")
```

2. ローカルで`uv run python main.py`を実行
3. コンソールに表示されるUser IDをコピー
4. `.env`ファイルの`LINE_USER_ID`に貼り付け
5. 追加したデバッグコードは削除してOK

**別の方法: Webhookを使う**

1. LINE Developersコンソールで一時的にWebhookを有効化
2. Webhook URLに一時的なURL（[ngrok](https://ngrok.com/)など）を設定
3. スマホからボットにメッセージを送信
4. Webhookログから`userId`をコピー
5. Webhookを再びオフにする

**参考:** User IDは個人を識別するIDで、ボットごとに異なります（プライバシー保護のため）

### Q: uv syncでエラーが出る

**原因1: uvがインストールされていない**
```bash
# インストール確認
uv --version

# インストールされていなければ再インストール
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**原因2: Pythonバージョンが見つからない**
```bash
# Python 3.11をuvでインストール
uv python install 3.11

# または、システムにPython 3.11をインストール
```

**原因3: ロックファイルが壊れている**
```bash
# uv.lockを削除して再生成
rm uv.lock
uv sync
```

### Q: pipを使いたい場合は？

互換性のため`requirements.txt`も残しています:

```bash
# pipで仮想環境を作成
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または venv\Scripts\activate (Windows)

# 依存関係をインストール
pip install -r requirements.txt
```

ただし、uvの方が高速で推奨されます。

## コスト見積もり

### OpenAI API
- 1回の実行あたり: 約$0.01〜0.03
- 月間（10回実行）: 約$0.10〜0.30
- gpt-4o-miniは非常に低コスト

### LINE Messaging API
- Push Message: 月500通まで無料
- このボットの送信頻度なら完全無料

### GitHub Actions
- Public リポジトリ: 完全無料
- Private リポジトリ: 月2,000分まで無料（このボットは1回5分以内）

**合計**: 月額 $0.10〜0.50 程度で運用可能

## カスタマイズ

### 実行頻度の変更
`.github/workflows/run_bot.yml`のcron設定を変更:

```yaml
# 毎日実行
- cron: '0 0 * * *'

# 毎週月曜日
- cron: '0 0 * * 1'
```

### 論文カテゴリの追加
`src/fetcher.py`の`categories`リストに追加:

```python
categories = ["cs.CL", "cs.AI", "cs.LG", "cs.CV", "cs.SE", "cs.RO"]  # cs.RO (Robotics)追加
```

### 要約形式の変更
`src/summarizer.py`の`system_prompt`を編集

### 検索期間の変更
`src/fetcher.py`の`DataFetcher`クラス:
```python
def __init__(self):
    self.ddgs = DDGS()
    self.days_back = 7  # 3から7に変更で、7日間のデータを収集
```

## よくある改善要望

### 1. 複数人に配信したい
**方法1: Broadcast APIを使う（友だち全員に送信）**
- `src/notifier.py`の`api_url`を変更:
```python
self.api_url = "https://api.line.me/v2/bot/message/broadcast"
```
- `payload`から`"to"`を削除

**方法2: 複数のUser IDに個別送信**
- `.env`に複数のUser IDを設定（カンマ区切り）
- `main.py`で複数のUser IDをループ処理

### 2. データをファイルに保存したい
- `src/main.py`に保存処理を追加
- JSON形式で`data/`ディレクトリに保存
- 過去データとの比較分析が可能に

### 3. より詳細な要約が欲しい
- `src/summarizer.py`の`max_tokens`を増やす（例: 2000 → 4000）
- `system_prompt`で「詳細に説明してください」と指示
- 注意: トークン数が増えるとコストも増加

### 4. Slackに通知したい
- `src/notifier.py`を参考に`slack_notifier.py`を作成
- Slack Incoming WebhooksまたはBolt APIを使用
- `main.py`で両方に通知する処理を追加

### 5. 特定のキーワードがある時だけ通知したい
- `src/summarizer.py`でフィルタリング処理を追加
- キーワードリスト（例: "ChatGPT", "Claude", "LLaMA"）を定義
- マッチしなければ通知をスキップ

## 次のステップ（実装後）

1. **定期的なメンテナンス**
   - 月1回、GitHub Actionsのログを確認
   - OpenAI APIの使用量をチェック
   - 不要な論文カテゴリがあれば削除

2. **カスタマイズ**
   - 自分の興味分野に合わせて検索クエリを調整
   - 要約のスタイルを好みに変更
   - 実行頻度を最適化

3. **機能拡張のアイデア**
   - 過去データの分析・トレンド可視化
   - 特定のキーワードでアラート通知
   - Webダッシュボードの追加
   - データベースへの保存（PostgreSQL, MongoDB等）

## ライセンス

MIT License

## 作成者

AI Trend Bot - 自動化されたAI情報収集システム

---

**注意**: このボットは情報収集ツールです。論文の詳細な理解や正確性の検証は、必ず原文を確認してください。
