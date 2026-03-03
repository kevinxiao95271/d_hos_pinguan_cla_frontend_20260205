import urllib.request, json

base = 'http://localhost:6031'

def login(phone, pwd):
    data = json.dumps({'phone': phone, 'password': pwd}).encode()
    req = urllib.request.Request(base+'/api/auth/login-with-password', data=data,
                                  headers={'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())['data']['token']

def get(path, token):
    try:
        req = urllib.request.Request(base+path, headers={'Authorization':'Bearer '+token})
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

token_com = login('13800000127','committee2026')

# 1. 筛选 id=136 的报名详情（从filter接口）
print('=== [1] 查 id=136 的材料（filter接口） ===')
code, body = get('/api/admin/registrations/filter?competitionId=1&page=1&size=100', token_com)
if isinstance(body, dict) and body.get('data'):
    for reg in body['data'].get('content', []):
        if reg['id'] == 136:
            print(f'  id=136 status={reg.get("status")}')
            mats = reg.get('materials', [])
            print(f'  materials({len(mats)}):')
            for m in mats:
                print(f'    id={m.get("id")} type={m.get("type")} fileName={m.get("fileName")}')
            pp = reg.get('paymentProofs', [])
            print(f'  paymentProofs({len(pp)}):')
            for p in pp:
                print(f'    id={p.get("id")} type={p.get("type")} fileName={p.get("fileName")}')
            break
    else:
        print('  id=136 not in this page')

# 2. 找评委账号（从 admin reviewers 列表）
print('\n=== [2] 获取评委列表 ===')
code2, body2 = get('/api/admin/reviewers?competitionId=1&page=1&size=10', token_com)
print(f'  GET /admin/reviewers => {code2}')
if isinstance(body2, dict) and body2.get('data'):
    reviewers = body2['data'].get('content') or body2['data']
    if isinstance(reviewers, list):
        for r in reviewers[:5]:
            print(f'  phone={r.get("phone")} name={r.get("name")} id={r.get("id")}')

# 3. 尝试评委详情接口 - 找书审分组详情
print('\n=== [3] 书审分组 - 单个项目详情接口 ===')
for path in ['/api/admin/book-groups/1', '/api/admin/registrations/group/136',
             '/api/committee/registrations/136', '/api/registrations/136/detail']:
    code3, b3 = get(path, token_com)
    if code3 == 200:
        print(f'  ✅ {path} => 200: {str(b3)[:150]}')
    else:
        print(f'  ❌ {path} => {code3}')

# 4. 评委查看项目详情 - 常见路径
print('\n=== [4] 可能的评委项目详情接口 ===')
# 先用 contestant 账号登录看 registration 详情
token_user = login('13937205966','155067')
for path in ['/api/registrations/136', '/api/registrations/my']:
    code4, b4 = get(path, token_user)
    print(f'  {path} => {code4}')
    if isinstance(b4, dict) and b4.get('data'):
        d = b4['data'] if isinstance(b4['data'], dict) else {}
        mats = d.get('materials', [])
        print(f'    materials({len(mats)}):')
        for m in mats:
            print(f'      id={m.get("id")} type={m.get("type")} fileName={m.get("fileName")}')
        pp = d.get('paymentProofs', [])
        if pp:
            print(f'    paymentProofs({len(pp)}):')
            for p in pp:
                print(f'      id={p.get("id")} type={p.get("type")} fileName={p.get("fileName")}')
