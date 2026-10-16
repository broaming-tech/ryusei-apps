#!/usr/bin/env python3
"""Add, publish, archive and list app/game/website portfolio entries safely.

New entries default to draft. Publication is an explicit step and a fresh
build automatically enables the website filter if a website is published.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from project_data import CATALOG, ROOT, KINDS, STATUSES, validate


def save(items):
    validate(items)
    tmp = CATALOG.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(CATALOG)


def slugify(name):
    value = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not value or len(value) < 2: raise ValueError('Websites need an ASCII slug: --id your-site')
    return value[:60].rstrip('-')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Maintain the portfolio project catalog')
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('list', help='Show project IDs and publication status')
    add = sub.add_parser('add', help='Add a new DRAFT record; publish separately')
    add.add_argument('--kind', required=True, choices=KINDS)
    add.add_argument('--name', required=True)
    add.add_argument('--url', required=True)
    add.add_argument('--label', required=True)
    add.add_argument('--tagline', required=True)
    add.add_argument('--description', required=True)
    add.add_argument('--color', default='#88A18F')
    add.add_argument('--id', help='Site slug or App Store numeric ID (automatically found in Apple URL when omitted)')
    add.add_argument('--image', help='For websites: local site/assets/projects/XXX.png etc., URL relative to site/')
    for action in ('publish', 'archive', 'draft'):
        c = sub.add_parser(action)
        c.add_argument('id', help='ID from list')
    args = parser.parse_args(argv)
    items = json.loads(CATALOG.read_text('utf-8'))
    if args.action == 'list':
        validate(items)
        for p in sorted(items, key=lambda x:x['sort']):
            print(f"{p['status']:9} {p['category']:7} {p['id']:20} {p['name']}")
        return
    if args.action == 'add':
        if args.kind in ('app', 'game'):
            match = re.search(r'/id(\d{10})(?:$|[/?])', urlsplit(args.url).path)
            id_ = args.id or (match.group(1) if match else None)
            if not id_: parser.error('App Store apps need a numeric ID in the URL or --id')
        else:
            id_ = args.id or slugify(args.name)
        if any(p['id']==id_ for p in items): parser.error('Project ID already exists')
        item = dict(id=id_, name=args.name, category=args.kind,
                    label=args.label, sort=min((p['sort'] for p in items),default=1)-1,
                    tagline=args.tagline, description=args.description,
                    url=args.url, color=args.color, status='draft')
        if args.image: item['image'] = args.image
        items.append(item)
        try: save(items)
        except ValueError as error: parser.error(str(error))
        print(f'Added draft: {id_}. Use: python tools/manage_projects.py publish {id_}')
        return
    matches = [p for p in items if p['id'] == args.id]
    if not matches: parser.error(f'Unknown project id {args.id}')
    entry = matches[0]
    entry['status'] = {'publish':'published', 'archive':'archived', 'draft':'draft'}[args.action]
    try: save(items)
    except ValueError as error: parser.error(str(error))
    print(f"{args.id}: {entry['status']}. Run tools/build_site.py and deploy updated content.")

if __name__ == '__main__': main()
