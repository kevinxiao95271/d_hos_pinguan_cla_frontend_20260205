"""Probe registration-drafts full flow with verified test accounts"""
import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031/api'

def login(phone, pwd):
    r = requests.post(BASE + '/auth/login-with-password', json={'phone': phone, 'password': pwd}, timeout=30)
    d = r.json()
    if not d.get('success'):
        return None, None, d
    u = d['data']
    return u['token'], u, d

def pp(label, r):
    try:
        body = r.json()
    except Exception:
        body = r.text[:500]
    print(f'\n--- {label} ---')
    print(f'HTTP {r.status_code}')
    s = json.dumps(body, ensure_ascii=False, indent=2)
    print(s[:1800] + ('...' if len(s) > 1800 else ''))
    return body

# ========== 登录 ==========
print('========== 登录验证 ==========')
ops_token, ops_user, _ = login('13800000005', 'ops2026')
if not ops_token:
    print('OPS 登录失败'); sys.exit(1)
print(f'OPS 登录 OK: {ops_user.get("name")} role={ops_user.get("role")}')

c_token, c_user, _ = login('13872005640', 'user123')
if not c_token:
    print('参赛者登录失败'); sys.exit(1)
print(f'参赛者登录 OK: {c_user.get("name")} role={c_user.get("role")} institutionId={c_user.get("institutionId")}')

h_c = {'Authorization': f'Bearer {c_token}'}

# ========== 参赛者：创建草稿 ==========
print('\n========== 参赛者：草稿流程 ==========')
r = requests.post(BASE + '/registration-drafts', headers=h_c, json={
    'competitionId': 1,
    'projectName': '前端探测草稿项目',
    'groupType': 'COMPREHENSIVE'
}, timeout=30)
b = pp('POST /registration-drafts (create)', r)
draft_id = (b.get('data') or {}).get('id') if b.get('success') else None
if not draft_id:
    print('创建草稿失败，退出'); sys.exit(1)
print(f'draftId = {draft_id}')

# GET detail
pp(f'GET /registration-drafts/{draft_id}', requests.get(BASE + f'/registration-drafts/{draft_id}', headers=h_c, timeout=30))

# check-duplicate
pp('GET check-duplicate (selfDraftId)', requests.get(BASE + '/registration-drafts/check-duplicate', headers=h_c, params={
    'competitionId': 1, 'institutionId': c_user.get('institutionId') or 4553,
    'projectName': '前端探测草稿项目', 'selfDraftId': draft_id
}, timeout=30))

# materials list (empty)
pp(f'GET materials', requests.get(BASE + f'/registration-drafts/{draft_id}/materials', headers=h_c, timeout=30))

# submit without materials (expect fail)
pp('POST submit (no materials, expect fail)', requests.post(BASE + f'/registration-drafts/{draft_id}/submit', headers=h_c, timeout=30))

# ========== 我的报名列表 ==========
print('\n========== GET /registrations/my ==========')
r = requests.get(BASE + '/registrations/my', headers=h_c, timeout=30)
b = pp('GET /registrations/my', r)
items = b.get('data') or []
if items:
    print(f'共 {len(items)} 条, 字段: {list(items[0].keys())}')
    drafts = [x for x in items if x.get('draft')]
    formal = [x for x in items if not x.get('draft')]
    print(f'草稿 draft=true: {len(drafts)} 条, 正式: {len(formal)} 条')
    for x in items[:5]:
        print(f'  id={x.get("id")} draft={x.get("draft")} status={x.get("status")} name={x.get("projectName","")[:30]}')

# ========== 旧接口对比 ==========
print('\n========== 旧接口 POST /registrations ==========')
r = requests.post(BASE + '/registrations', headers=h_c, json={
    'competitionId': 1, 'projectName': '旧接口对比探测', 'groupType': 'BASIC'
}, timeout=30)
b = pp('POST /registrations', r)
legacy_id = (b.get('data') or {}).get('id') if b.get('success') else None
if legacy_id:
    d = b['data']
    print(f'  id={legacy_id}, status={d.get("status")}, draft={d.get("draft")}, keys={list(d.keys())}')
    r_reg = requests.get(BASE + f'/registrations/{legacy_id}', headers=h_c, timeout=30)
    r_draft = requests.get(BASE + f'/registration-drafts/{legacy_id}', headers=h_c, timeout=30)
    print(f'  GET /registrations/{legacy_id} -> HTTP {r_reg.status_code}')
    print(f'  GET /registration-drafts/{legacy_id} -> HTTP {r_draft.status_code}')
    if r_reg.status_code == 200:
        print('  → 旧创建仍走 registrations 表')
    elif r_draft.status_code == 200:
        print('  → 旧创建实际返回 draftId')

# cleanup
for did in filter(None, [draft_id, legacy_id]):
    requests.delete(BASE + f'/registration-drafts/{did}', headers=h_c, timeout=10)
    if legacy_id and legacy_id != draft_id:
        requests.delete(BASE + f'/registrations/{legacy_id}', headers=h_c, timeout=10)
print(f'\n已清理测试数据 draft={draft_id} legacy={legacy_id}')
print('\n=== 探测完毕 ===')
