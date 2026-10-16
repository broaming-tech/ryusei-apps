import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_site import page, CONTACT_EMAIL
from project_data import validate, load, CatalogError


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_projects = json.loads((ROOT/'data/projects.json').read_text('utf-8'))
        cls.projects = load()
        cls.html = (ROOT/'site/index.html').read_text('utf-8')
        cls.dom = Collector()
        cls.dom.feed(cls.html)

    def test_seven_published_projects_currently(self):
        validate(self.all_projects)
        self.assertEqual(len(self.projects), 7)
        self.assertEqual(sum(p['category']=='app' for p in self.projects), 4)
        self.assertEqual(sum(p['category']=='game' for p in self.projects), 3)
        self.assertEqual(sum(p['category']=='website' for p in self.projects), 0)

    def test_exactly_seven_official_links(self):
        links=[a for tag,a in self.dom.tags if tag=='a' and 'apps.apple.com' in a.get('href','')]
        self.assertEqual(len(links),7)
        self.assertEqual({a['href'] for a in links},{x['url'] for x in self.projects})
        self.assertTrue(all(a.get('target')=='_blank' and a.get('rel')=='noopener noreferrer' for a in links))

    def test_cards_and_icon_paths(self):
        cards = [a for tag,a in self.dom.tags if tag=='article' and a.get('data-kind')]
        self.assertEqual([a['data-kind'] for a in cards].count('app'), 4)
        self.assertEqual([a['data-kind'] for a in cards].count('game'), 3)
        for project in self.projects:
            self.assertIn(f'assets/icons/{project["id"]}.png', self.html)
            self.assertIn(project['name'],self.html)

    def test_head_metadata(self):
        self.assertIn('lang="ja"',self.html)
        metas=[a for tag,a in self.dom.tags if tag=='meta']
        for key, value in [('property','og:image'),('name','description'),('name','twitter:card')]:
            self.assertTrue(any(x.get(key)==value for x in metas),value)
        self.assertTrue(any(tag=='link' and a.get('rel')=='canonical' for tag,a in self.dom.tags))
        self.assertIn('7作品',self.html)

    def test_resources_exist(self):
        for rel in ['assets/images/banner.webp','assets/images/avatar.webp','assets/images/og.jpg','assets/images/favicon.png','styles.css','scripts.js','404.html','site-policy.html','robots.txt','sitemap.xml']:
            self.assertTrue((ROOT/'site'/rel).is_file(),rel)

    def test_no_trackers_or_placeholders(self):
        lower=self.html.lower()
        for word in ['googletagmanager','google-analytics','facebook.com/tr','TODO'.lower(),'準備中']:
            self.assertNotIn(word,lower)

    def test_filters_auto_build(self):
        buttons=[a for tag,a in self.dom.tags if tag=='button' and a.get('data-filter')]
        self.assertEqual([a['data-filter'] for a in buttons],['all','app','game'])
        self.assertEqual([a['aria-pressed'] for a in buttons],['true','false','false'])
        self.assertNotIn('data-filter="website"',self.html)
        self.assertIn('つくったもの',self.html)

    def test_xml_sitemap(self):
        tree=ET.parse(ROOT/'site/sitemap.xml')
        urls=[e.text for e in tree.getroot().iter() if e.tag.endswith('loc')]
        self.assertEqual(len(urls),1)
        self.assertEqual(urlparse(urls[0]).scheme,'https')

    def test_images_integrity(self):
        from PIL import Image
        for name in ['avatar.webp','banner.webp','og.jpg','favicon.png']:
            with Image.open(ROOT/'site/assets/images'/name) as im:im.verify()

    def test_icon_identity_guard_website_exclusion(self):
        source=(ROOT/'tools/fetch_icons.py').read_text('utf-8')
        for value in ['artistName','trackId','raise RuntimeError',"('app','game')",'load()']:
            self.assertIn(value,source)

    def test_external_links_safe(self):
        external=[a for tag,a in self.dom.tags if tag=='a' and a.get('href','').startswith('https://')]
        self.assertTrue(all(a.get('target')=='_blank' and a.get('rel')=='noopener noreferrer' for a in external))
        scripts=[a.get('src') for tag,a in self.dom.tags if tag=='script']
        self.assertEqual(scripts,['scripts.js'])

    def test_new_published_website_automatically_appears(self):
        future = dict(id='my-new-site',name='私のサイト',category='website',status='published',label='ツール',
                      tagline='便利なサイト',description='新しいWebサイトの作品です。',url='https://some-website.dev/',
                      color='#dce8dc',sort=-1)
        validate(self.all_projects+[future])
        html=page([future]+self.projects,'https://my-user.github.io/works/')
        self.assertIn('data-filter="website"',html)
        self.assertIn('Webサイト (1)',html)
        self.assertIn('data-kind="website"',html)
        self.assertIn('Webサイトを見る',html)
        self.assertIn('8作品',html)
        self.assertIn('iOSアプリやゲーム、Webサイト',html)
        self.assertEqual(html.count('class="card"'),8)

    def test_draft_and_archived_never_published(self):
        draft=dict(id='future-site',name='Future website',category='website',status='draft',label='ツール',
                   tagline='Soon',description='Unpublished',url='https://my-web.dev/',color='#889988',sort=-9)
        archived={**draft,'id':'old-site','status':'archived'}
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'projects.json'
            file.write_text(json.dumps(self.all_projects+[draft,archived]),encoding='utf-8')
            published=load(file,root=ROOT)
            self.assertEqual(len(published),7)
            html=page(published,'https://my-user.github.io/works/')
            self.assertNotIn('Future website',html)
            self.assertNotIn('my-web.dev',html)

    def test_reject_malicious_entries(self):
        base = deepcopy(self.all_projects[0])
        for patch in ({'url':'javascript:alert(1)'}, {'color':'red; background:url(x)'},
                      {'status':'open'}, {'category':'unknown'}, {'id':self.all_projects[1]['id']}):
            with self.subTest(patch=patch):
                bad={**base,**patch}
                with self.assertRaises(CatalogError): validate(self.all_projects+[bad])

    def test_website_image_must_be_local_and_present_when_published(self):
        example=dict(id='portfolio-website',name='サイト',category='website',status='published',label='作品',
                     tagline='作品です',description='公開中のWebサイト',url='https://my-portfolio.dev/',
                     color='#ddccbb',sort=1, image='assets/projects/missing.png')
        with self.assertRaises(CatalogError):validate(self.all_projects+[example])
        example['status']='draft'
        validate(self.all_projects+[example])
        example['image']='https://evil.example/pic.png'
        with self.assertRaises(CatalogError):validate(self.all_projects+[example])

    def test_html_escapes_text(self):
        safe={**self.all_projects[0], 'name':'<script>alert(1)</script>'}
        html=page([safe],'https://github.io.example/some/')
        self.assertNotIn('<script>alert(1)</script>',html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;',html)

    def test_official_support_email_in_contact_locations(self):
        self.assertEqual(CONTACT_EMAIL, 'support.broaming@gmail.com')
        mailto = 'mailto:' + CONTACT_EMAIL
        links = [attrs for tag, attrs in self.dom.tags if tag == 'a' and attrs.get('href') == mailto]
        self.assertEqual(len(links), 2, 'Contact action and footer link')
        self.assertTrue(all('お問い合わせ' in a.get('aria-label', '') for a in links))
        self.assertIn('お問い合わせ', self.html)
        self.assertNotIn('support@example.com', self.html)

    def test_policy_contact_and_mail_client_link(self):
        content = (ROOT / 'site/site-policy.html').read_text('utf-8')
        self.assertIn(f'href="mailto:{CONTACT_EMAIL}"', content)
        self.assertIn('>support.broaming@gmail.com</a>', content)
        self.assertIn('メールアプリが開きます', content)
        self.assertNotIn('support@example.com', content)

    def test_contact_does_not_reduce_existing_content(self):
        self.assertEqual(self.html.count('class="card"'), 7)
        self.assertIn('data-filter="app"', self.html)
        self.assertIn('data-filter="game"', self.html)
        self.assertIn('https://x.com/broaming_app', self.html)
        for p in self.projects:
            self.assertIn(p['url'], self.html)

    def test_single_source_and_auto_deployment(self):
        workflow=(ROOT/'.github/workflows/pages.yml').read_text('utf-8')
        self.assertIn('tools/build_site.py',workflow)
        self.assertIn('tools/fetch_icons.py',workflow)
        self.assertIn('python -m unittest',workflow)
        self.assertFalse((ROOT/'data/apps.json').exists())

if __name__=='__main__':unittest.main()
