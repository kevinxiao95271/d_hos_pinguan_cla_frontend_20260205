import urllib.request
import json
import io

base = 'http://localhost:6031'

# Login
data = json.dumps({'phone': '13937205966', 'password': '155067'}).encode()
req = urllib.request.Request(base + '/api/auth/login-with-password', data=data,
                              headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=10)
body = json.loads(resp.read())
token = body['data']['token']
print('login ok')

def get(path):
    try:
        req = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + token})
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

# 获取报名列表
code, body = get('/api/registrations/my')
print(f'\nGET /registrations/my => {code}')
regs = body.get('data', []) if isinstance(body, dict) else []
if regs:
    reg = regs[0]
    reg_id = reg['id']
    print(f'  第一条报名 id={reg_id}, status={reg.get("status")}')

    # 获取报名详情
    code2, detail = get(f'/api/registrations/{reg_id}')
    print(f'\nGET /registrations/{reg_id} => {code2}')
    if isinstance(detail, dict) and detail.get('data'):
        mats = detail['data'].get('materials', [])
        print(f'  materials({len(mats)}):')
        for m in mats:
            print(f'    id={m.get("id")} type={m.get("type")} fileName={m.get("fileName")}')

    # 测试上传 DOC
    boundary = '----Boundary7MA4'
    content = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="test.docx"\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'
        f'FAKE\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="type"\r\n\r\n'
        f'REGISTRATION_FORM_DOC\r\n'
        f'--{boundary}--\r\n'
    ).encode()
    try:
        req3 = urllib.request.Request(
            base + f'/api/registrations/{reg_id}/materials',
            data=content,
            headers={
                'Authorization': 'Bearer ' + token,
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            },
            method='POST'
        )
        resp3 = urllib.request.urlopen(req3, timeout=10)
        print(f'\nPOST /registrations/{reg_id}/materials (DOC) => {resp3.status}')
        print(json.loads(resp3.read()))
    except urllib.error.HTTPError as e:
        print(f'\nPOST /registrations/{reg_id}/materials (DOC) => {e.code}')
        print(e.read().decode()[:300])

    # 测试上传 PDF
    content2 = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'
        f'FAKE\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="type"\r\n\r\n'
        f'REGISTRATION_FORM_PDF\r\n'
        f'--{boundary}--\r\n'
    ).encode()
    try:
        req4 = urllib.request.Request(
            base + f'/api/registrations/{reg_id}/materials',
            data=content2,
            headers={
                'Authorization': 'Bearer ' + token,
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            },
            method='POST'
        )
        resp4 = urllib.request.urlopen(req4, timeout=10)
        print(f'\nPOST /registrations/{reg_id}/materials (PDF) => {resp4.status}')
        print(json.loads(resp4.read()))
    except urllib.error.HTTPError as e:
        print(f'\nPOST /registrations/{reg_id}/materials (PDF) => {e.code}')
        print(e.read().decode()[:300])

    # 测试错误格式（DOC 传 pdf 文件名）
    content3 = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="wrong.pdf"\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'
        f'FAKE\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="type"\r\n\r\n'
        f'REGISTRATION_FORM_DOC\r\n'
        f'--{boundary}--\r\n'
    ).encode()
    try:
        req5 = urllib.request.Request(
            base + f'/api/registrations/{reg_id}/materials',
            data=content3,
            headers={
                'Authorization': 'Bearer ' + token,
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            },
            method='POST'
        )
        resp5 = urllib.request.urlopen(req5, timeout=10)
        print(f'\nPOST (DOC wrong ext) => {resp5.status}')
    except urllib.error.HTTPError as e:
        print(f'\nPOST (DOC wrong ext) => {e.code}: {e.read().decode()[:200]}')

    # 测试提交（应缺 PDF 报错）
    try:
        req6 = urllib.request.Request(
            base + f'/api/registrations/{reg_id}/submit',
            data=b'{}',
            headers={
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        resp6 = urllib.request.urlopen(req6, timeout=10)
        print(f'\nPOST /submit => {resp6.status}: {resp6.read().decode()[:200]}')
    except urllib.error.HTTPError as e:
        print(f'\nPOST /submit => {e.code}: {e.read().decode()[:300]}')
else:
    print('  无报名数据，用 DRAFT 用户测试')
