#!/usr/bin/env python3
"""Download the true App Store icons at *build time*, never fabricate app artwork.
Run from an internet-connected environment. GitHub Actions performs this at deploy.
"""
from pathlib import Path
from project_data import load
from urllib.request import Request, urlopen
import argparse, json, io, sys, time

ROOT = Path(__file__).resolve().parent.parent

def retrieve(url, timeout=25):
    req=Request(url,headers={'User-Agent':'ryusei-apps-deploy/1.0 (App Store metadata sync)'})
    with urlopen(req,timeout=timeout) as response:
        return response.read()

def run(strict=True, retrieval=retrieve):
    apps=[project for project in load() if project['category'] in ('app','game')]
    dst=ROOT/'site/assets/icons';dst.mkdir(parents=True,exist_ok=True)
    errors=[]
    from PIL import Image
    for app in apps:
        id_=app['id']
        try:
            # Apple Lookup API returns official artwork URL, identity checked by trackId and artist.
            api=f'https://itunes.apple.com/lookup?id={id_}&country=jp&entity=software'
            payload=json.loads(retrieval(api))
            matches=[item for item in payload.get('results',[]) if str(item.get('trackId'))==id_]
            if len(matches)!=1: raise ValueError('Apple lookup returned no unique application record')
            info=matches[0]
            artist=str(info.get('artistName','')).casefold().replace(' ','')
            if 'ryuseikawanami' not in artist: raise ValueError(f'Developer differs: {info.get("artistName")}')
            art=info.get('artworkUrl512') or info.get('artworkUrl100')
            if not art or not art.startswith('https://'): raise ValueError('No official HTTPS artwork URL')
            binary=retrieval(art)
            src=Image.open(io.BytesIO(binary));src.load()
            if src.width<100 or src.height<100: raise ValueError('Artwork unexpectedly small')
            src.convert('RGBA').save(dst/f'{id_}.png',optimize=True)
            print('OK',id_,src.size)
        except Exception as exc:
            errors.append(f'{id_} ({app["name"]}): {exc}')
            print('ERROR',errors[-1],file=sys.stderr)
        time.sleep(.05)
    if errors and strict: raise RuntimeError(f'Icons missing: {len(errors)}/{len(apps)}. Not deploying in strict mode.')
    return errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--allow-missing',action='store_true');opts=p.parse_args()
    run(strict=not opts.allow_missing)
