# 新しいアプリ・ゲーム・Webサイトの追加方法

この作品集は、**公開済みの作品を増やすときも画面のコードを編集する必要がない**構造です。
公開していないものをうっかり載せないよう、追加と公開は別操作にしています。

## 方法A：ChatGPTに依頼して更新する（おすすめ）

このプロジェクトの最新版ZIPと、次の情報を渡してください。

- アプリ名またはWebサイト名
- 種類：アプリ／ゲーム／Webサイト
- 実際の公開先URL（App StoreのURLまたはWebサイトURL）
- 紹介文（分からなければChatGPTが草案を提案）
- Webサイトなら実際のロゴ・スクリーンショット（画像なしでも掲載可能）

「この作品を公開作品として追加して」と依頼すれば、既存作品を保持しつつ`data/projects.json`だけ更新できます。既存のGitHubにアップロードした状態の最新版を基準にするのが安全です。

## 方法B：同梱ツールで直接追加する

プロジェクトの最上位フォルダで実行します。Python 3.10以降が必要です。

### 1. 新しいiOSアプリを下書き登録する

```bash
python tools/manage_projects.py add \
  --kind app \
  --name '新しいアプリ名' \
  --url 'https://apps.apple.com/jp/app/your-app/id1234567890' \
  --label '暮らし' \
  --tagline 'ひと言キャッチコピー' \
  --description '実際に公開したアプリの概要'
```

上のURLは**説明用の例**で、実際には公開済みのApp Storeリンクに置き換えてください。`game` を指定するとゲームになります。App Store IDは公開URLから自動抽出します。

### 2. 新しいWebサイトを下書き登録する

```bash
python tools/manage_projects.py add \
  --kind website \
  --id my-new-website \
  --name '新しく作ったサイト' \
  --url 'https://your-actual-site.example.jp/' \
  --label 'Webサービス' \
  --tagline '便利なWebサイト' \
  --description '何ができるサイトかを簡潔に説明'
```

Webサイトに**実際の画面のスクリーンショット（16:9推奨）**を載せたい場合は `site/assets/projects/` に `my-new-website.webp` などの実物画像を保存し、追加コマンドに `--image assets/projects/my-new-website.webp` を付けてください。未指定ならイニシャル表示です。Webサイト画像はカード内に横長で表示され、アプリアイコンと混同しません。

### 3. 公開する

```bash
python tools/manage_projects.py list
python tools/manage_projects.py publish my-new-website
python tools/build_site.py
python -m unittest discover -s tests -v
```

iOSアプリの場合は `publish` の後ろに数値App Store IDを指定します。**初期状態は必ず `draft`** です。`publish` を実行すると公開対象になり、次のデプロイ時に一覧へ現れます。Webサイト作品の追加時は、「Webサイト」ボタンも自動的に出現します。

### 4. 一時非公開・再公開

```bash
python tools/manage_projects.py draft my-new-website
python tools/manage_projects.py archive my-new-website
python tools/manage_projects.py publish my-new-website
```

`draft` と `archive` は表示されなくなりますが、作品の情報はJSONに残ります。誤った公開をした場合は、`draft` に戻してデプロイしてください。

## 作品の修正・表示順

`data/projects.json` が唯一のデータファイルです。作品名、説明、URL、ジャンル、並び順（数値の `sort`。小さい順）などを編集できます。JSON文法を壊すと公開ビルドは停止します。公開状態 `published` のURLは必ず実際に動作しているものを使ってください。

## GitHub Pagesでの反映

`main` ブランチにファイルを保存・Pushすると `.github/workflows/pages.yml` が自動実行されます。手動で反映したい場合は Actions → Deploy Ryusei Apps portfolio → Run workflow を使います。GitHub PagesがGitHub Actionsからデプロイするよう設定されている必要があります。

サイト本体は `site/` に出力されます。**既存の別リポジトリやプライバシーポリシーを上書きしないこと。**

### 重要

- App StoreアイコンはAppleから実データを取得するため、GitHub Actionsのネットワークアクセスが必要です。
- 初回ZIPには本物のApp Storeアイコンが入っていない場合があります。Appleと通信できないローカルプレビューでは、文字だけの代替アイコンが見えます。公開ビルドでは正規画像が取得できないと処理を停止します。
- 公開URLはGitHubリポジトリを作成し、Pages設定・デプロイしたあとに確定します。
- セキュリティ上、URL・JSONを編集するために公開サイト上の管理画面やログインは設けていません。
