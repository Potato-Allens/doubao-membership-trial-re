#!/usr/bin/env python3
"""R469: structured diff of two trade/init responses (eligible vs normal).

Usage:
    python tools/_r469_diff.py --hit-json A.json A.json --normal B.json
    python tools/_r469_diff.py --fetch --hit-cookie-file hit.ck --normal-cookie-file normal.ck

The point of this script is negative evidence: after diffing every field of a
real `trade/init` response between an eligible account and a non-eligible one,
the only differences live inside `sku_list[i].purchase_card_list[0]` (the
discounted card) plus `service_current_time`. `data.activities` is identical,
so there is no hidden client-side cohort marker to spoof.
"""
import argparse, json

SCOPE = {"version_code":"20800","language":"zh","device_platform":"web",
         "doubao_device_platform":"web","aid":"497858","real_aid":"497858",
         "pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0",
         "region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop",
         "use-olympus-account":"1"}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
H = {"content-type":"application/json","agw-js-conv":"str",
     "referer":"https://www.doubao.com/member/subscription",
     "origin":"https://www.doubao.com","user-agent":UA,
     "accept":"application/json, text/plain, */*"}


def parse_cookie(s):
    d = {}
    for p in s.split(';'):
        if '=' in p:
            k, v = p.split('=', 1)
            d[k.strip()] = v.strip()
    return d


def fetch(cookie):
    import requests
    s = requests.Session()
    s.cookies.update(parse_cookie(cookie))
    s.headers.update(H)
    r = s.post('https://www.doubao.com/alice/commerce/sale/trade/init/',
               params=SCOPE, json={'scene_key':'default_member_link','purchase_channel':2},
               timeout=25)
    return r.json()


def diff(a, b, path=''):
    out = []
    if type(a) != type(b):
        return [(path, type(a).__name__, type(b).__name__)]
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((path + '/' + k, '<missing>', str(b[k])[:60]))
            elif k not in b:
                out.append((path + '/' + k, str(a[k])[:60], '<missing>'))
            else:
                out += diff(a[k], b[k], path + '/' + k)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path + '/len', len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, path + '[%d]' % i)
    else:
        if a != b:
            out.append((path, str(a)[:80], str(b)[:80]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hit-json')
    ap.add_argument('--normal-json')
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--hit-cookie-file')
    ap.add_argument('--normal-cookie-file')
    ap.add_argument('--out-dir')
    a = ap.parse_args()
    if a.fetch:
        hit = fetch(open(a.hit_cookie_file, encoding='utf-8').read().strip())
        nrm = fetch(open(a.normal_cookie_file, encoding='utf-8').read().strip())
        if a.out_dir:
            os.makedirs(a.out_dir, exist_ok=True)
            json.dump(hit, open(os.path.join(a.out_dir, 'hit_init.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            json.dump(nrm, open(os.path.join(a.out_dir, 'normal_init.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
    else:
        hit = json.load(open(a.hit_json, encoding='utf-8'))
        nrm = json.load(open(a.normal_json, encoding='utf-8'))
    print('hit  code=%r activities=%r' % (hit.get('code'), (hit.get('data') or {}).get('activities')))
    print('norm code=%r activities=%r' % (nrm.get('code'), (nrm.get('data') or {}).get('activities')))
    d = diff(hit, nrm)
    print('diff_count=%d' % len(d))
    for p, x, y in d:
        print('  %-70s %-28s -> %s' % (p, x, y))


if __name__ == '__main__':
    main()
