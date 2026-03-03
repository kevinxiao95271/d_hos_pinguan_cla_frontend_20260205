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

# 获取评委列表
print('=== 评委账号 ===')
code, body = get('/api/admin/reviewers?competitionId=1', token_com)
print(f'GET /admin/reviewers => {code}')
reviewers = body.get('data', []) if isinstance(body, dict) else []
if isinstance(reviewers, list):
    for r in reviewers[:5]:
        print(f'  phone={r.get("phone")} name={r.get("name")} id={r.get("id")}')
    rev_phone = reviewers[0].get('phone') if reviewers else None
else:
    rev_phone = None

# 评委登录
token_rev = None
if rev_phone:
    for pwd in ['reviewer2026', 'Reviewer2026', '123456', rev_phone[-6:]]:
        try:
            token_rev = login(rev_phone, pwd)
            print(f'  评委登录成功: {rev_phone} / {pwd}')
            break
        except Exception as e:
            print(f'  {rev_phone}/{pwd} 失败')

# 评委可访问的项目详情接口探测
if token_rev:
    print('\n=== 评委项目详情接口 ===')
    for path in [
        '/api/reviews/my-assignments?competitionId=1',
        '/api/reviews/projects?competitionId=1',
        '/api/registrations/136',
        '/api/reviews/registration-detail/136',
        '/api/reviews/project/136',
    ]:
        c, b = get(path, token_rev)
        if c == 200:
            d = b.get('data') if isinstance(b, dict) else b
            print(f'  ✅ {path} => 200')
            if isinstance(d, dict):
                mats = d.get('materials', [])
                if mats:
                    print(f'    materials: {[m.get("type") for m in mats]}')
            elif isinstance(d, list) and d:
                first = d[0]
                print(f'    first item keys: {list(first.keys())[:8]}')
        else:
            print(f'  ❌ {path} => {c}')

# committee 查看书审分组的项目详情（单个项目）
print('\n=== committee 项目详情接口 ===')
for path in [
    '/api/admin/registrations/136/detail',
    '/api/admin/registrations?id=136',
    '/api/committee/book/registrations/136',
    '/api/admin/book/registrations/136',
    '/api/admin/registrations/filter?competitionId=1&registrationId=136',
]:
    c, b = get(path, token_com)
    if c == 200:
        d = b.get('data') if isinstance(b, dict) else b
        print(f'  ✅ {path} => 200')
        if isinstance(d, dict):
            mats = d.get('materials', [])
            print(f'    materials: {[m.get("type") for m in mats]}')
        elif isinstance(d, list) and d:
            first = d[0] if d else {}
            print(f'    first keys: {list(first.keys())[:8]}')
    else:
        print(f'  ❌ {path} => {c}')

# 材料下载测试
print('\n=== 材料下载接口 ===')
for mat_id, mat_type in [(29, 'REGISTRATION_FORM_DOC'), (30, 'REGISTRATION_FORM_PDF')]:
    for path in [f'/api/materials/{mat_id}/download', f'/api/admin/materials/{mat_id}/download']:
        c, b = get(path, token_com)
        print(f'  {path} ({mat_type}) => {c}')
        if c == 200:
            break
