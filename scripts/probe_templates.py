import urllib.request
import urllib.parse
import json
import io

base = 'http://81.71.44.180:6031'

# Login
data = json.dumps({'phone': '13800000005', 'password': 'ops2026'}).encode()
req = urllib.request.Request(base + '/api/auth/login-with-password', data=data,
                              headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=10)
body = json.loads(resp.read())
token = body['data']['token']
print('login ok, token prefix:', token[:20])

def get(path):
    try:
        req = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + token})
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# 探测可能的 endpoints
paths = [
    '/api/system-templates',
    '/api/system-templates/active',
    '/api/admin/system-templates',
    '/api/admin/system-templates/active',
]

for p in paths:
    code, body = get(p)
    print(f'{code}  {p}  =>  {str(body)[:120]}')

# 尝试用最小 multipart 上传（只带 file 字段）
print('\n--- 尝试 POST /api/system-templates/upload (只带file) ---')
boundary = '----FormBoundary7MA4YWxkTrZu0gW'
content = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="test.docx"\r\n'
    f'Content-Type: application/octet-stream\r\n\r\n'
    f'FAKECONTENT\r\n'
    f'--{boundary}--\r\n'
).encode()

try:
    req = urllib.request.Request(
        base + '/api/system-templates/upload',
        data=content,
        headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        },
        method='POST'
    )
    resp = urllib.request.urlopen(req, timeout=10)
    print(resp.status, json.loads(resp.read()))
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode()[:300])

# 尝试带 templateType 字段
print('\n--- 尝试 POST /api/system-templates/upload (带templateType) ---')
content2 = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="test.docx"\r\n'
    f'Content-Type: application/octet-stream\r\n\r\n'
    f'FAKECONTENT\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="templateType"\r\n\r\n'
    f'registration_form\r\n'
    f'--{boundary}--\r\n'
).encode()

try:
    req2 = urllib.request.Request(
        base + '/api/system-templates/upload',
        data=content2,
        headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        },
        method='POST'
    )
    resp2 = urllib.request.urlopen(req2, timeout=10)
    print(resp2.status, json.loads(resp2.read()))
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode()[:300])
