import urllib.request, json, ssl

ctx = ssl._create_unverified_context()

req = urllib.request.Request(
    'http://zkjb.zjmss.org.cn/api/auth/login-with-password',
    data=json.dumps({'phone':'13588758501','password':'858500'}).encode(),
    headers={'Content-Type':'application/json'}
)
with urllib.request.urlopen(req, context=ctx) as r:
    login = json.loads(r.read())

token = login['data']['token']
print('role:', login['data'].get('role'))
print('pendingIntegrityNoticeKeys:', login['data'].get('pendingIntegrityNoticeKeys'))

req2 = urllib.request.Request(
    'http://zkjb.zjmss.org.cn/api/reviews/final/my-tasks',
    headers={'Authorization': 'Bearer ' + token}
)
with urllib.request.urlopen(req2, context=ctx) as r:
    tasks = json.loads(r.read())

data = tasks.get('data') or []
print('final tasks count:', len(data))
for t in data:
    status = t.get('status')
    name = t.get('projectName')
    sf = t.get('scoreForm')
    total = t.get('total')
    print('  [' + str(status) + '] ' + str(name) + ' | scoreForm=' + str(sf) + ' | total=' + str(total))
