"""Published project catalog and strict validation for a static public website."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

KINDS = {'app': 'アプリ', 'game': 'ゲーム', 'website': 'Webサイト'}
STATUSES = {'draft', 'published', 'archived'}
ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'data' / 'projects.json'

class CatalogError(ValueError):
    pass


def validate(items, root=ROOT):
    if not isinstance(items, list):
        raise CatalogError('Catalog must be a JSON array')
    seen = set()
    for pos, project in enumerate(items):
        def fail(message):
            raise CatalogError(f'projects[{pos}]: {message}')
        if not isinstance(project, dict): fail('record must be an object')
        key = project.get('id')
        if not isinstance(key, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,60}', key):
            fail('id must be a lowercase slug or App Store numeric ID')
        if key in seen: fail('duplicate id')
        seen.add(key)
        kind = project.get('category')
        if kind not in KINDS: fail('unsupported category')
        if project.get('status') not in STATUSES: fail('invalid status')
        if not isinstance(project.get('sort'), int) or isinstance(project.get('sort'), bool): fail('sort must be an integer')
        for field in ('name', 'label', 'tagline', 'description', 'url'):
            val = project.get(field)
            if not isinstance(val, str) or not val.strip() or len(val) > 500:
                fail(f'{field} required (1..500 characters)')
        color = project.get('color')
        if not isinstance(color, str) or not re.fullmatch(r'#[0-9A-Fa-f]{6}', color): fail('color must be #RRGGBB')
        parts = urlsplit(project['url'])
        if parts.scheme != 'https' or not parts.netloc or parts.username or parts.password or parts.port not in (None,443):
            fail('public target URL must use HTTPS and contain no credentials or unusual port')
        hostname = (parts.hostname or '').lower()
        if hostname in ('localhost', '127.0.0.1', 'example.com', 'example.org', 'example.net') or '.' not in hostname:
            fail('URL must be a public real destination')
        if kind in ('app', 'game'):
            if not re.fullmatch(r'\d{10}', key): fail('App Store items need a 10-digit app ID')
            if hostname != 'apps.apple.com' or not re.search(r'/id'+re.escape(key)+r'(?:$|[/?])', parts.path):
                fail('App Store URL and numeric id do not match')
            if project.get('image'): fail('App Store icons must come from official Apple artwork, not a custom image')
        else:
            img = project.get('image')
            if img:
                if not isinstance(img, str) or not re.fullmatch(r'assets/projects/[A-Za-z0-9_.-]+\.(?:png|webp|jpg|jpeg)', img):
                    fail('website image must be a local asset in assets/projects')
                if project['status'] == 'published' and not (root/'site'/img).is_file():
                    fail(f'published website image does not exist: {img}')
    return True


def load(path=CATALOG, root=ROOT):
    items = json.loads(Path(path).read_text(encoding='utf-8'))
    validate(items, root=root)
    # Never expose draft or archived projects in HTML, metadata or icon retrieval.
    return sorted((item for item in items if item['status']=='published'),
                  key=lambda item: (item['sort'], item['name'].casefold()))
