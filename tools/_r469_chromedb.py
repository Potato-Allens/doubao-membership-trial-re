#!/usr/bin/env python3
r"""R469: recover doubao cookies from local Chrome profiles (Windows, DPAPI + AES-GCM).

Usage:
    python tools/_r469_chromedb.py --base "C:\path\to\chrome_profiles" --out new_pool.json [--known a.json b.json]

Layout expected: <base>/acc_*/{Local State, Default/Network/Cookies} (Chromium 80+).

Crypto notes that cost time to figure out:
  * os_crypt.encrypted_key is base64 and starts with the ASCII tag b"DPAPI" -> strip 5 bytes.
  * v10 blob: nonce = blob[3:15], ciphertext = blob[15:], AESGCM(key).decrypt -> plaintext.
  * The plaintext begins with a 32-byte prefix (Chromium's app-bound header) -> use [32:].
  * v20 (App-Bound Encryption) is not supported here; profiles using it return ''.
"""
import argparse, base64, glob, json, os, re, shutil, sqlite3, tempfile


def key_of(profile_dir):
    import win32crypt
    j = json.load(open(os.path.join(profile_dir, 'Local State'), encoding='utf-8'))
    enc = base64.b64decode(j['os_crypt']['encrypted_key'])
    return win32crypt.CryptUnprotectData(enc[5:], None, None, None, 0)[1]


def dec(key, v):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if not v:
        return ''
    if v[:3] == b'v10':
        try:
            return AESGCM(key).decrypt(v[3:15], v[15:], None)[32:].decode('utf-8', 'replace')
        except Exception:
            return ''
    if v[:3] == b'v20':
        return ''
    try:
        return v.decode('utf-8', 'replace')
    except Exception:
        return ''


NEED = ['sessionid','sessionid_ss','sid_tt','sid_guard','uid_tt','uid_tt_ss','s_v_web_id',
        'device_id','iid','install_id','ttwid','passport_csrf_token','odin_tt','webid','_tea_web_id']


def sid_of(cookie):
    m = re.search(r'sessionid=([0-9a-fA-F]{16,})', cookie or '')
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--known', nargs='*', default=[])
    a = ap.parse_args()

    out, profs = [], 0
    for p in sorted(glob.glob(os.path.join(a.base, 'acc_*'))):
        if not os.path.isdir(p):
            continue
        db = os.path.join(p, 'Default', 'Network', 'Cookies')
        if not os.path.exists(db) or not os.path.exists(os.path.join(p, 'Local State')):
            continue
        try:
            k = key_of(p)
        except Exception:
            continue
        tmp = tempfile.mktemp(suffix='.db')
        try:
            shutil.copy2(db, tmp)
            con = sqlite3.connect(tmp)
            con.row_factory = sqlite3.Row
            rows = [dict(r) for r in con.execute(
                "select host_key,name,value,encrypted_value from cookies where host_key like '%doubao%'")]
            con.close()
        except Exception:
            if os.path.exists(tmp):
                os.remove(tmp)
            continue
        vals = {}
        for r in rows:
            v = r['value'] or dec(k, r['encrypted_value'])
            if r['name'] in NEED and v and r['name'] not in vals:
                vals[r['name']] = v
        os.remove(tmp)
        if not vals.get('sessionid'):
            continue
        profs += 1
        cookie = '; '.join('%s=%s' % (n, vals[n]) for n in NEED if n in vals)
        out.append({'name': os.path.basename(p), 'cookie_string': cookie,
                    'uid_tt': vals.get('uid_tt', '')})
    print('profiles_with_session=%d entries=%d' % (profs, len(out)))

    known = set()
    for f in a.known:
        for acc in json.load(open(f, encoding='utf-8'))['accounts']:
            s = sid_of(acc.get('cookie_string'))
            if s:
                known.add(s)
    new = [x for x in out if sid_of(x['cookie_string']) not in known]
    print('known=%d new=%d' % (len(known), len(new)))
    json.dump({'accounts': new}, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('saved ->', a.out)


if __name__ == '__main__':
    main()
