#!/usr/bin/env python3
"""Push the VitePress site to GitHub via the Git Data API.

Uses the vault-stored PAT through the credential surrogate mechanism:
the surrogate goes in the Authorization header and the egress proxy
swaps it for the real token. Binary-safe (blobs are base64).
"""
import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, '/opt/muse/skills/custom-connector-setup/bin')
from dynamic_credentials import dynamic_credential_entry

OWNER = 'pkm365'
REPO = 'witcher3-guide'
BRANCH = 'main'
ROOT = os.environ.get('W3_SITE_DIR', os.path.expanduser('~/workspace/witcher3-guide/site'))

SKIP_DIRS = {'node_modules', '.git', 'dist', 'cache', '_sections', '__pycache__'}
SKIP_FILES = {'.DS_Store', 'convert.py'}


def get_token():
    entry = dynamic_credential_entry('custom.github-push', 'access_token')
    surr = entry['surrogate']
    if not surr:
        sys.exit('ERROR: no credential surrogate available')
    return surr


def api(method, path, data=None, retries=5):
    import time
    import http.client
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                'https://api.github.com' + path,
                data=json.dumps(data).encode() if data is not None else None,
                method=method,
                headers={
                    'Authorization': f'Bearer {TOKEN}',
                    'Accept': 'application/vnd.github+json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'dq-cloud-push',
                },
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.request.HTTPError as e:
            last = e
            if e.code in (500, 502, 503) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (http.client.RemoteDisconnected, http.client.IncompleteRead,
                ConnectionError, TimeoutError) as e:
            last = e
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise
    raise last


def collect_files():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn in SKIP_FILES:
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, ROOT)
            out.append((rel, full))
    return sorted(out)


def main():
    global TOKEN
    TOKEN = get_token()
    message = sys.argv[1] if len(sys.argv) > 1 else '更新攻略站'

    files = collect_files()
    print(f'{len(files)} files to push')

    # 1. current ref（空仓库无 ref 时走首提交路径）
    try:
        ref = api('GET', f'/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}')
        base_sha = ref['object']['sha']
        base_commit = api('GET', f'/repos/{OWNER}/{REPO}/git/commits/{base_sha}')
        base_tree = base_commit['tree']['sha']
    except Exception:
        base_sha, base_tree = None, None
        print('empty repo: initial commit mode')

    # 2. create blobs
    tree_items = []
    for i, (rel, full) in enumerate(files):
        with open(full, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        blob = api('POST', f'/repos/{OWNER}/{REPO}/git/blobs',
                   {'content': content, 'encoding': 'base64'})
        tree_items.append({'path': rel, 'mode': '100644',
                           'type': 'blob', 'sha': blob['sha']})
        if (i + 1) % 10 == 0:
            print(f'  blobs: {i + 1}/{len(files)}')

    # 3. create tree, commit, update ref
    tree_payload = {'tree': tree_items}
    if base_tree:
        tree_payload['base_tree'] = base_tree
    tree = api('POST', f'/repos/{OWNER}/{REPO}/git/trees', tree_payload)
    commit_payload = {'message': message, 'tree': tree['sha']}
    if base_sha:
        commit_payload['parents'] = [base_sha]
    commit = api('POST', f'/repos/{OWNER}/{REPO}/git/commits', commit_payload)
    if base_sha:
        api('PATCH', f'/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}',
            {'sha': commit['sha']})
    else:
        api('POST', f'/repos/{OWNER}/{REPO}/git/refs',
            {'ref': f'refs/heads/{BRANCH}', 'sha': commit['sha']})
    print('pushed commit', commit['sha'])
    print(f'https://github.com/{OWNER}/{REPO}/commit/{commit["sha"]}')


if __name__ == '__main__':
    main()
