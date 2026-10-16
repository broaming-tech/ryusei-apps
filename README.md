# りゅうせい | Apps — ポートフォリオサイト

**現在の掲載内容：App Storeで公開済みの7作品。** 将来的な新アプリ・ゲーム・Webサイトの追加に対応する、GitHub Pages向け静的サイトです。

## 構造

- `data/projects.json`：作品の全データ（唯一の管理元）
- `tools/manage_projects.py`：追加、公開、アーカイブ
- `tools/project_data.py`：種類・公開状態・URL等の検証
- `tools/build_site.py`：HTML、SEO、サイトマップ等を静的生成
- `tools/fetch_icons.py`：Apple公式メタデータから**公開済みアプリ**のアイコンだけ取得
- `site/`：公開対象のHTML/CSS/JS/イラスト、今後Webサイトのロゴやスクリーンショットもここへ
- `tests/test_static.py`：初期7作品維持、Webサイト追加、未公開除外、リンク・SEO・不正入力等のユニットテスト
- `.github/workflows/pages.yml`：GitHub Pagesへ自動公開
- `MASTER_SPEC_1.0_FROZEN.md`：当初の凍結仕様
- `MASTER_SPEC_1.0_2_FROZEN.md`：ユーザー承認の拡張仕様（基準仕様の明示的改訂）
- `MASTER_SPEC_1.0_3_FROZEN.md`：共通お問い合わせメールの確定追加仕様
- `ADDING_PROJECTS.md`：今後の作品追加の手順

## 初回公開

1. GitHubアカウントで新しい公開リポジトリ `ryusei-apps` を作成する。
2. このプロジェクトの中身をリポジトリの最上位に配置する（**既存の別アプリ用リポジトリを上書きしない**）。
3. GitHub → Settings → Pages → Build and deployment → **Source: GitHub Actions** を指定する。
4. Actionsで `Deploy Ryusei Apps portfolio` を実行するか、mainへPushする。
5. 実際に配信された `https://<GitHubユーザー名>.github.io/ryusei-apps/` を開き、公式アイコン・全リンク・スマホ表示を点検する。
6. Xプロフィールの「ウェブサイト」欄に、確認した**実際の公開URL**を設定する。

> この環境では外部のGitHubリポジトリが確認できず、ユーザー権限による公開／GitHub Pages設定は行っていません。初回公開後のオンライン動作確認は別途必要です。

## ローカルでの確認

```bash
python tools/build_site.py --base-url https://broaming-tech.github.io/ryusei-apps/
python -m unittest discover -s tests -v
python -m http.server 8000 --directory site
```

ブラウザで `http://localhost:8000/` を開いてください。公式アイコンを表示するには、インターネット接続時に `pip install -r requirements-deploy.txt` → `python tools/fetch_icons.py` を実行します。

## 将来の作品追加

`ADDING_PROJECTS.md` を参照してください。1件追加しただけで掲載数・カテゴリボタン・メタデータが連動し、未公開は自動的に非表示となります。

## お問い合わせ

公式窓口は **support.broaming@gmail.com** です。ホーム下部の「お問い合わせ」ボタン、フッター、「このサイトについて」の3か所に `mailto:` リンクを設定しました。メールアプリで送信し、サイト自体にはフォームやメール保存機能を設置しません。

## 運用とプライバシー

登録フォーム、認証、広告、外部解析、追跡Cookieはありません。作品は外部リンクでApp Storeまたは制作者のWebサイトへ案内します。ホスティング事業者側のアクセスログの扱いは事業者の規約によります。

## 既知の外部依存／未検証

- Apple Lookup APIから正規アートワークが取得できること（公開ビルドで失敗時停止。現在のプレビュー／ZIPにはApple公式アイコン画像を同梱していません）
- App Storeページの到達性、所有者メタデータ（実際のネットワークがある環境で確認）
- GitHub Pagesでの本番デプロイ、公開URL、実機iOS Safariの表示
- お問い合わせをタップした際の各端末メールアプリ起動。ローカルでブラウザ自動検証を試しましたが、この実行環境でネットワーク／ファイルURLアクセスがブロックされました

これらが確認できるまでは**公開完了／全項目検証済みとはしません**。
