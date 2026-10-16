#!/usr/bin/env python3
"""Headless Chromium smoke + accessibility-like functional and viewport tests."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
import threading, json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'site'
httpd=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(SITE)))
threading.Thread(target=httpd.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{httpd.server_port}/'
report=[]
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox','--disable-dev-shm-usage'])
    for w,h in [(320,780),(375,812),(390,844),(768,1024),(1280,900)]:
        ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,locale='ja-JP')
        pg=ctx.new_page()
        js_errors=[]
        pg.on('pageerror',lambda e:js_errors.append(str(e)))
        response=pg.goto(url,wait_until='load')
        pg.wait_for_timeout(400)
        assert response.status==200,(w,response.status)
        assert pg.locator('.card').count()==7,(w,'total card count')
        assert pg.locator('.card:visible').count()==7,(w,'initial visible')
        page_width=pg.evaluate('document.documentElement.scrollWidth')
        assert page_width<=w,(w,'horizontal overflow',page_width)
        pg.get_by_role('button',name='ゲーム (3)').click()
        assert pg.locator('.card:visible').count()==3,(w,'game filter')
        assert pg.get_by_role('button',name='ゲーム (3)').get_attribute('aria-pressed')=='true'
        pg.get_by_role('button',name='アプリ (4)').click()
        assert pg.locator('.card:visible').count()==4,(w,'app filter')
        pg.get_by_role('button',name='すべて (7)').click()
        assert pg.locator('.card:visible').count()==7
        assert not js_errors,(w,js_errors)
        assert pg.locator('a.store-link').count()==7
        email_links=pg.locator('a[href="mailto:support.broaming@gmail.com"]')
        assert email_links.count()==2,(w,'contact links')
        assert pg.get_by_role('link',name='メールでお問い合わせ（メールアプリを開く）').is_visible(),(w,'contact button visibility')
        report.append({'viewport':f'{w}x{h}','horizontal_overflow':False,'filters':'PASS','javascript_errors':0,'store_links':7,'mailto_links':2})
        if w in (375,1280):
            filename=ROOT/f'PREVIEW_{w}.png'
            pg.screenshot(path=str(filename),full_page=True,animations='disabled')
        ctx.close()
    # Offline/JS-disabled mode: all content rendered, category controls hidden to avoid useless buttons.
    ctx=browser.new_context(viewport={'width':375,'height':812},java_script_enabled=False)
    pg=ctx.new_page()
    pg.goto(url,wait_until='load')
    assert pg.locator('article.card').count()==7
    assert not pg.locator('.filter').first.is_visible()
    assert pg.get_by_role('link',name='PetStockをApp Storeで見る（新しいタブ）').is_visible()
    report.append({'mode':'JavaScript disabled','all_7_cards':'PASS','filters_hidden':'PASS'})
    ctx.close()
    ctx=browser.new_context(viewport={'width':390,'height':844})
    pg=ctx.new_page()
    pg.goto(url+'site-policy.html');assert '個人情報の取り扱い' in pg.locator('body').inner_text()
    assert pg.locator('a[href="mailto:support.broaming@gmail.com"]').count()==1
    pg.goto(url+'not-existent');assert pg.locator('body').count()==1 # simple static server responds 404 itself
    pg.goto(url+'404.html');assert 'お探しのページは見つかりませんでした' in pg.locator('body').inner_text()
    ctx.close()
    browser.close()
finally:
 httpd.shutdown()
(ROOT/'QA_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
