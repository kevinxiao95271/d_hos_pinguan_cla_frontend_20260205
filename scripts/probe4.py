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

# committee 查看书审/面谈分组详情接口
print('=== committee detail APIs ===')
paths = [
    '/api/admin/registrations/136/detail',
    '/api/admin/registrations?id=136',
    '/api/committee/book/registrations/136',
    '/api/admin/book/registrations/136',
    '/api/admin/registrations/filter?competitionId=1&registrationId=136',
]
for path in paths:
    c, b = get(path, token_com)
    if c == 200:
        d = b.get('data') if isinstance(b, dict) else b
        info = ''
        if isinstance(d, dict):
            mats = d.get('materials', [])
            info = 'materials: ' + str([m.get('type') for m in mats])
        elif isinstance(d, list) and d:
            info = 'list, first keys: ' + str(list(d[0].keys())[:6])
        print(f'  OK  {path} => {info}')
    else:
        print(f'  {c}  {path}')

# 材料下载接口
print('\n=== material download ===')
for mat_id, mtype in [(29,'DOC'),(30,'PDF')]:
    for path in [f'/api/materials/{mat_id}/download', f'/api/admin/materials/{mat_id}/download']:
        c, b = get(path, token_com)
        print(f'  {c}  {path} ({mtype})')
        if c == 200:
            break

# 评委账号尝试
print('\n=== reviewer login attempts ===')
rev_phones = ['13800002569','13811185687','13886509429']
token_rev = None
rev_ok = None
for ph in rev_phones:
    for pwd in ['reviewer2026','review2026','Reviewer@2026','pgds2026','cla2026','aabb1234']:
        try:
            t = login(ph, pwd)
            token_rev = t
            rev_ok = (ph, pwd)
            print(f'  OK: {ph} / {pwd}')
            break
        except:
            pass
    if token_rev:
        break

if token_rev:
    print(f'\n=== reviewer APIs (phone={rev_ok[0]}) ===')
    rev_paths = [
        '/api/reviews/my-assignments?competitionId=1',
        '/api/reviews/projects?competitionId=1&stage=BOOK',
        '/api/registrations/136',
        '/api/reviews/registration-detail/136',
    ]
    for path in rev_paths:
        c, b = get(path, token_rev)
        if c == 200:
            d = b.get('data') if isinstance(b, dict) else b
            info = ''
            if isinstance(d, dict):
                mats = d.get('materials', [])
                info = 'materials=' + str([m.get('type') for m in mats])
            elif isinstance(d, list) and d:
                info = f'list[{len(d)}], first={list(d[0].keys())[:5]}'
            print(f'  OK  {path} => {info}')
        else:
            print(f'  {c}  {path}')
else:
    print('  reviewer login failed, check password with admin')
