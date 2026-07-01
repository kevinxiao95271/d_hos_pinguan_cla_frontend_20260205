"""Verify backend compatibility layer: old /registrations/** paths with draftId"""
import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031/api'

def login(phone, pwd):
    r = requests.post(BASE + '/auth/login-with-password', json={'phone': phone, 'password': pwd}, timeout=30)
    d = r.json()
    if not d.get('success'):
        return None, None
    return d['data']['token'], d['data']

def pp(label, r, max_len=1200):
    try:
        body = r.json()
    except Exception:
        body = r.text[:400]
    print(f'\n--- {label} ---')
    print(f'HTTP {r.status_code}')
    s = json.dumps(body, ensure_ascii=False, indent=2)
    print(s[:max_len] + ('...' if len(s) > max_len else ''))
    return body

token, user = login('13872005640', 'user123')
if not token:
    print('登录失败'); sys.exit(1)
print(f'参赛者登录 OK institutionId={user.get("institutionId")}')
h = {'Authorization': f'Bearer {token}'}

print('\n========== 旧路径全流程（模拟前端） ==========')

# 1. POST create
b = pp('1. POST /registrations', requests.post(BASE + '/registrations', headers=h, json={
    'competitionId': 1, 'projectName': '兼容层探测项目', 'groupType': 'COMPREHENSIVE'
}, timeout=30))
if not b.get('success'):
    sys.exit(1)
rid = b['data']['id']
print(f'>>> 前端存 id={rid}, status={b["data"].get("status")}, draft={b["data"].get("draft")}')

# 2. GET detail
b2 = pp('2. GET /registrations/{id}', requests.get(BASE + f'/registrations/{rid}', headers=h, timeout=30))
draft_flag = (b2.get('data') or {}).get('draft')
status = (b2.get('data') or {}).get('registration', b2.get('data', {}))
if isinstance(status, dict):
    reg = b2.get('data', {}).get('registration') or b2.get('data', {})
else:
    reg = b2.get('data', {})
print(f'>>> detail draft={draft_flag}, keys={list((b2.get("data") or {}).keys())[:8]}')

# 3. PUT basic
b3 = pp('3. PUT /registrations/{id}', requests.put(BASE + f'/registrations/{rid}', headers=h, json={
    'projectName': '兼容层探测项目-已修改', 'groupType': 'COMPREHENSIVE',
    'projectLeaderName': '测试负责人', 'projectLeaderPhone': '13800000001'
}, timeout=30))

# 4. PUT members
b4 = pp('4. PUT /registrations/{id}/members', requests.put(BASE + f'/registrations/{rid}/members', headers=h, json={
    'members': [{'name': '成员甲', 'title': '护师', 'role': 'MEMBER'}]
}, timeout=30))

# 5. check-duplicate with selfId=draftId
b5 = pp('5. GET check-duplicate selfId=draftId', requests.get(BASE + '/registrations/check-duplicate', headers=h, params={
    'competitionId': 1, 'institutionId': user.get('institutionId'), 'projectName': '兼容层探测',
    'selfId': rid
}, timeout=30))

# 6. GET my list - find our item
b6 = pp('6. GET /registrations/my', requests.get(BASE + '/registrations/my', headers=h, timeout=30))
items = b6.get('data') or []
mine = next((x for x in items if x.get('id') == rid), None)
if mine:
    print(f'>>> 列表项 id={mine["id"]} draft={mine.get("draft")} status={mine.get("status")}')

# 7. submit without materials
b7 = pp('7. POST submit (no materials)', requests.post(BASE + f'/registrations/{rid}/submit', headers=h, timeout=30))

# 8. compare new path still works
b8 = pp('8. GET /registration-drafts/{id} (新路径)', requests.get(BASE + f'/registration-drafts/{rid}', headers=h, timeout=30))

# cleanup
requests.delete(BASE + f'/registration-drafts/{rid}', headers=h, timeout=10)
print(f'\n已清理 draft id={rid}')
print('\n=== 兼容层验证完毕 ===')
