import urllib.request
import json

base = 'http://localhost:6031'

def login(phone, password):
    data = json.dumps({'phone': phone, 'password': password}).encode()
    req = urllib.request.Request(base + '/api/auth/login-with-password', data=data,
                                  headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=10)
    body = json.loads(resp.read())
    return body['data']['token']

def get(path, token):
    try:
        req = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + token})
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]

def show_materials(mats):
    if not mats:
        print('    (无)')
        return
    for m in mats:
        print(f'    id={m.get("id")} type={m.get("type")} fileName={m.get("fileName")} uploadedAt={m.get("uploadedAt","")[:16]}')

# ========== 用 committee 账号 ==========
print('=== 用 committee 账号探测 ===')
token_com = login('13800000127', 'committee2026')

# 1. 书审分组 - 项目列表
print('\n[1] 书审分组 项目列表')
code, body = get('/api/admin/registrations/filter?competitionId=1&page=1&size=5', token_com)
print(f'  GET /admin/registrations/filter => {code}')
if isinstance(body, dict) and body.get('data'):
    items = body['data'].get('content', [])
    print(f'  共 {body["data"].get("totalElements", "?")} 条，取前{len(items)}条')
    if items:
        reg = items[0]
        reg_id = reg['id']
        print(f'  第一条 id={reg_id}, projectName={reg.get("projectName")}')
        mats = reg.get('materials', [])
        print(f'  materials({len(mats)}):')
        show_materials(mats)
        pproofs = reg.get('paymentProofs', [])
        print(f'  paymentProofs({len(pproofs)}):')
        show_materials(pproofs)

# 2. 书审分组详情 - 获取单个报名详情
print('\n[2] 书审/面谈 - 获取报名详情 (registrationId=136)')
code2, detail = get('/api/admin/registrations/136', token_com)
print(f'  GET /admin/registrations/136 => {code2}')
if isinstance(detail, dict) and detail.get('data'):
    d = detail['data']
    mats = d.get('materials', [])
    print(f'  materials({len(mats)}):')
    show_materials(mats)
    pproofs = d.get('paymentProofs', [])
    print(f'  paymentProofs({len(pproofs)}):')
    show_materials(pproofs)

# 3. 书审分组列表
print('\n[3] 书审分组列表 (book stage groups)')
code3, body3 = get('/api/admin/registrations/filter?competitionId=1&stage=BOOK&page=1&size=5', token_com)
print(f'  GET (with stage=BOOK) => {code3}')

# 4. 尝试面谈分组 API
print('\n[4] 面谈分组列表')
code4, body4 = get('/api/admin/registrations/filter?competitionId=1&groupType=ADVANCED&page=1&size=5', token_com)
print(f'  GET (ADVANCED group) => {code4}')
if isinstance(body4, dict) and body4.get('data'):
    items4 = body4['data'].get('content', [])
    print(f'  共 {body4["data"].get("totalElements")} 条')

# ========== 用评委账号 ==========
print('\n=== 用评委账号探测 ===')
# Try to find a reviewer account
token_rev = None
for phone, pwd in [('13800000200', 'reviewer2026'), ('13800000201', 'reviewer2026'),
                   ('13800000100', 'reviewer2026'), ('13900000001', 'reviewer2026')]:
    try:
        token_rev = login(phone, pwd)
        print(f'  评委登录成功: {phone}')
        break
    except:
        pass

if token_rev:
    # 获取分配给我的项目列表
    print('\n[5] 评委 - 我的项目列表')
    code5, body5 = get('/api/reviews/my-assignments?competitionId=1', token_rev)
    print(f'  GET /reviews/my-assignments => {code5}')
    if isinstance(body5, dict):
        items5 = body5.get('data', [])
        if items5:
            print(f'  共{len(items5)}条')
            reg5 = items5[0]
            reg_id5 = reg5.get('registrationId') or reg5.get('id')
            print(f'  第一条 registrationId={reg_id5}')

    # 尝试获取项目详情
    print('\n[6] 评委 - 项目详情 (registrationId=136)')
    code6, detail6 = get('/api/reviews/registration/136', token_rev)
    print(f'  GET /reviews/registration/136 => {code6}')
    if isinstance(detail6, dict) and detail6.get('data'):
        d6 = detail6['data']
        mats6 = d6.get('materials', [])
        print(f'  materials({len(mats6)}):')
        show_materials(mats6)

    # 尝试其他可能的路径
    for path in ['/api/registrations/136', '/api/admin/registrations/136']:
        code7, body7 = get(path, token_rev)
        print(f'\n[7] 评委访问 {path} => {code7}')
        if isinstance(body7, dict) and body7.get('data'):
            d7 = body7['data']
            mats7 = d7.get('materials', [])
            print(f'  materials({len(mats7)}):')
            show_materials(mats7)
else:
    print('  未能找到评委账号，跳过评委测试')

# ========== 材料下载 ==========
print('\n=== 测试材料下载 ===')
# 先用 committee 账号获取一个 REGISTRATION_FORM_DOC 材料的 id
code8, body8 = get('/api/admin/registrations/filter?competitionId=1&page=1&size=20', token_com)
if isinstance(body8, dict) and body8.get('data'):
    for reg in body8['data'].get('content', []):
        for m in reg.get('materials', []):
            if m.get('type') in ('REGISTRATION_FORM_DOC', 'REGISTRATION_FORM_PDF'):
                mat_id = m['id']
                code9, body9 = get(f'/api/materials/{mat_id}/download', token_com)
                print(f'  GET /materials/{mat_id}/download (type={m["type"]}) => {code9}')
                break
        else:
            continue
        break
