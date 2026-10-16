#!/usr/bin/env python3
"""Build the static portfolio from the single extensible data/projects.json catalog."""
import argparse, html
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter
from project_data import load, KINDS, validate

BASE = Path(__file__).resolve().parent.parent
DEFAULT_URL = 'https://broaming-tech.github.io/ryusei-apps/'
CONTACT_EMAIL = 'support.broaming@gmail.com'

def h(text): return html.escape(str(text), quote=True)


def card(app):
    kind = KINDS[app['category']]
    is_website = app['category'] == 'website'
    artwork = None if is_website else f"assets/icons/{app['id']}.png"
    image = (f'<img src="{h(artwork)}" alt="" width="80" height="80" loading="lazy" decoding="async" />'
             if artwork else '')
    website_preview = (f'<div class="website-preview"><img src="{h(app["image"])}" '
                       f'alt="{h(app["name"])}の実際の画面" loading="lazy" decoding="async" /></div>'
                       if is_website and app.get('image') else '')
    url_label = 'Webサイトを見る' if is_website else 'App Storeで見る'
    # Text is safely escaped, URLs and CSS colors are checked by project_data.validate.
    return f'''\n    <article class="card" data-kind="{h(app['category'])}" aria-labelledby="work-{h(app['id'])}">
      <div class="card-top">
        <div class="app-icon" style="background-color:{h(app['color'])}" aria-hidden="true">
          <span class="fallback">{h(app['name'][:1].upper())}</span>
          {image}
        </div>
        <div class="card-name">
          <div class="card-type">{kind} · {h(app['label'])}</div>
          <h3 id="work-{h(app['id'])}">{h(app['name'])}</h3>
          <p class="tagline">{h(app['tagline'])}</p>
        </div>
      </div>
      {website_preview}
      <p class="description">{h(app['description'])}</p>
      <div class="card-bottom">
        <span class="category-pill">{kind}</span>
        <a class="store-link" href="{h(app['url'])}" target="_blank" rel="noopener noreferrer" aria-label="{h(app['name'])}を{h(url_label)}（新しいタブ）">{h(url_label)} <span aria-hidden="true">↗</span></a>
      </div>
    </article>'''

def page(apps, base_url):
    cards=''.join(card(a) for a in apps)
    counts=Counter(a['category'] for a in apps)
    has_websites=bool(counts['website'])
    kinds_present='アプリ・ゲーム・Webサイト' if has_websites else 'iOSアプリ・ゲーム'
    hero_intro='iOSアプリやゲーム、Webサイトを個人で作っています。' if has_websites else 'iOSアプリやゲームを個人で作っています。'
    filter_buttons='\n'.join(f'<button type="button" class="filter" data-filter="{h(k)}" aria-pressed="false">{h(KINDS[k])} ({counts[k]})</button>' for k in KINDS if counts[k] > 0)
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f8f8f1">
<meta name="color-scheme" content="light">
<meta name="description" content="りゅうせいが個人開発した{kinds_present}{len(apps)}作品をまとめたポートフォリオ。作品の紹介と公式ページへのリンクをご覧いただけます。">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{h(base_url)}">
<link rel="icon" type="image/png" href="assets/images/favicon.png">
<link rel="apple-touch-icon" href="assets/images/favicon.png">
<link rel="preload" as="image" href="assets/images/avatar.webp" type="image/webp">
<link rel="stylesheet" href="styles.css">
<meta property="og:type" content="website">
<meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="りゅうせい | Apps">
<meta property="og:title" content="りゅうせい | Apps — 思いつきを、アプリに。">
<meta property="og:description" content="個人開発した{kinds_present}{len(apps)}作品をまとめたページです。">
<meta property="og:url" content="{h(base_url)}">
<meta property="og:image" content="{h(base_url)}assets/images/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="りゅうせいのアプリ作品集">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="りゅうせい | Apps">
<meta name="twitter:description" content="思いつきを、アプリに。個人開発した{kinds_present}の作品集。">
<meta name="twitter:image" content="{h(base_url)}assets/images/og.jpg">
<title>りゅうせい | Apps — 個人開発した{kinds_present}</title>
<script defer src="scripts.js"></script>
</head>
<body>
<a class="skip" href="#works">作品一覧へ移動</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="#top" aria-label="りゅうせい Apps トップへ"><img src="assets/images/avatar.webp" width="38" height="38" alt=""><span>りゅうせい <small>APPS</small></span></a>
    <nav class="header-right" aria-label="メインナビゲーション">
      <a class="nav-link" href="#works">作品一覧</a>
      <a class="nav-link x-link" href="https://x.com/broaming_app" target="_blank" rel="noopener noreferrer" aria-label="Xのアカウントを開く（新しいタブ）"><span aria-hidden="true">𝕏</span> Xを見る <span class="arr" aria-hidden="true">↗</span></a>
    </nav>
  </div>
</header>
<main id="top">
  <section class="hero" aria-labelledby="hero-title">
    <div class="wrap">
      <div class="hero-main">
        <div class="hero-text">
          <div class="overline"><span class="line"></span>INDIE APP DEVELOPER</div>
          <h1 id="hero-title">思いつきを、<br><span class="accent">アプリに。</span></h1>
          <p class="hero-caption">こんにちは、りゅうせいです。<br>{hero_intro}</p>
          <div class="hero-actions"><a class="primary" href="#works">つくったものを見る <span aria-hidden="true">↓</span></a><span class="mini-meta">{h(kinds_present)} · {len(apps)} works</span></div>
        </div>
        <div class="portrait"><img src="assets/images/avatar.webp" alt="りゅうせいのイラストアイコン" width="640" height="640" fetchpriority="high"><span class="portrait-sparkle"><span class="spark" aria-hidden="true">✦</span> Building apps</span></div>
      </div>
      <div class="artband"><img src="assets/images/banner.webp" alt="デスクでアプリを作る開発者と2匹のうさぎ、ハリネズミのイラスト" width="2000" height="667" decoding="async"><span class="artband-tag">MADE WITH CURIOSITY ✳</span></div>
    </div>
  </section>
  <section class="works" id="works" aria-labelledby="works-title">
    <div class="wrap">
      <div class="works-heading"><div><div class="section-kicker">MY CREATIONS</div><h2 id="works-title">つくったもの<span aria-hidden="true"> ✳</span></h2><p>日常をちょっと便利に。ときどき、ちょっと楽しく。</p></div><span class="count"><strong>{len(apps):02d}</strong> 作品</span></div>
      <div class="filters" role="group" aria-label="作品の種類で絞り込み">
        <button type="button" class="filter" data-filter="all" aria-pressed="true">すべて ({len(apps)})</button>
        {filter_buttons}
      </div>
      <noscript><style>.filters{{display:none}}</style></noscript>
      <span id="filter-result" class="visually-hidden" role="status" aria-live="polite">{len(apps)}作品を表示中</span>
      <div class="cards">{cards}
      </div>
    </div>
  </section>
  <section class="outro wrap" aria-labelledby="outro-title"><div><div class="foot-kicker">LET'S CONNECT</div><h2 id="outro-title">これからも、いろいろ作ります。</h2><p>制作過程や新しいアプリのことはXで。<br>アプリ・サイトに関するお問い合わせはメールで受け付けています。</p></div><div class="contact-actions"><a class="social-link" href="https://x.com/broaming_app" target="_blank" rel="noopener noreferrer" aria-label="Xでりゅうせいをフォローする（新しいタブ）"><span aria-hidden="true">𝕏</span> Xを見に行く <span aria-hidden="true">↗</span></a><a class="social-link contact-link" href="mailto:{CONTACT_EMAIL}" aria-label="メールでお問い合わせ（メールアプリを開く）"><span aria-hidden="true">✉</span> お問い合わせ</a></div></section>
</main>
<footer class="footer"><div class="wrap"><span>© 2026 りゅうせい · Made with curiosity.</span><div class="footer-links"><a href="mailto:{CONTACT_EMAIL}" aria-label="メールでお問い合わせ">お問い合わせ</a><a href="site-policy.html">このサイトについて</a><a href="#top">ページ上部へ ↑</a></div></div></footer>
</body></html>
'''

POLICY = '''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f8f8f1"><meta name="robots" content="noindex,follow"><title>このサイトについて | りゅうせい Apps</title><link rel="icon" href="assets/images/favicon.png"><link rel="stylesheet" href="styles.css"></head><body><a class="skip" href="#content">内容へ移動</a><header class="site-header"><div class="wrap"><a href="index.html" class="logo"><img src="assets/images/avatar.webp" alt="" width="38" height="38"><span>りゅうせい <small>APPS</small></span></a><a class="nav-link" href="index.html">← 作品一覧へ</a></div></header><main class="policy" id="content"><div class="section-kicker">ABOUT THIS WEBSITE</div><h1>このサイトについて</h1><p>「りゅうせい | Apps」は、個人開発したアプリ・ゲーム・Webサイトをまとめたポートフォリオサイトです。</p><h2>個人情報の取り扱い</h2><p>このサイトにはアカウント登録・問い合わせフォームはなく、独自のアクセス解析・広告・トラッキングCookieを設置していません。静的サイト配信事業者が技術的なアクセスログを取得する場合があります。ログの扱いは配信事業者の方針をご確認ください。</p><h2>外部リンク</h2><p>App Store、公開したWebサイトおよびXへのリンクを掲載しています。移動先のサイトには、それぞれの利用規約やプライバシーポリシーが適用されます。</p><h2>作品について</h2><p>作品の機能、利用条件、プライバシー情報は各配信先・掲載先をご確認ください。このサイトには公開済み作品のみを掲載しています。</p><h2>お問い合わせ</h2><p>アプリ・ゲーム・Webサイトに関するご連絡は、<a href="mailto:__CONTACT_EMAIL__">__CONTACT_EMAIL__</a> までお願いします。リンクを選択するとメールアプリが開きます。</p><p><a href="index.html">← アプリ一覧へ戻る</a></p></main><footer class="footer"><div class="wrap"><span>© 2026 りゅうせい</span></div></footer></body></html>'''
NOT_FOUND='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>ページが見つかりません | りゅうせい Apps</title><link rel="stylesheet" href="styles.css"><link rel="icon" href="assets/images/favicon.png"></head><body><main class="not-found wrap"><div class="section-kicker">PAGE NOT FOUND</div><h1>404</h1><p>お探しのページは見つかりませんでした。</p><p><a class="primary" href="./">作品一覧に戻る →</a></p></main></body></html>'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--base-url',default=DEFAULT_URL)
    args=p.parse_args()
    url=args.base_url.rstrip('/')+'/'
    u=urlparse(url);assert u.scheme=='https' and u.hostname
    apps=load()
    site=BASE/'site';site.mkdir(exist_ok=True)
    (site/'index.html').write_text(page(apps,url),'utf-8')
    (site/'site-policy.html').write_text(POLICY.replace('__CONTACT_EMAIL__', CONTACT_EMAIL),'utf-8')
    (site/'404.html').write_text(NOT_FOUND,'utf-8')
    (site/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {url}sitemap.xml\n','utf-8')
    (site/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+f' <url><loc>{h(url)}</loc></url>\n'+'</urlset>\n','utf-8')
    (site/'.nojekyll').write_text('','utf-8')
    print(f'Generated: {len(apps)} published works (apps/games/websites), SEO, filters and static pages.')
if __name__=='__main__':main()
