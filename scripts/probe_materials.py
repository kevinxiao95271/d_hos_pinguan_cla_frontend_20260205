import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:6031/api'

r = requests.post(BASE + '/auth/login-with-password', json={'phone':'13309090909','password':'test0909'}, timeout=15)
token = r.json()['data']['token']
headers = {'Authorization': 'Bearer ' + token}

r2 = requests.get(BASE + '/registrations/my', headers=headers, timeout=15)
regs = r2.json().get('data', [])
for reg in regs:
    reg_id = reg.get('id')
    status = reg.get('status')
    print(f'regId={reg_id} status={status}')

    r3 = requests.get(BASE + '/registrations/' + str(reg_id) + '/materials', headers=headers, timeout=15)
    print('  GET /registrations/{}/materials: {}'.format(reg_id, r3.status_code))
    if r3.status_code == 200:
        d = r3.json().get('data', r3.json())
        if isinstance(d, list):
            print('  count={}'.format(len(d)))
            if d:
                print('  Keys:', list(d[0].keys()))
                print('  Sample:', json.dumps(d[0], ensure_ascii=False)[:400])
                mat_id = d[0].get('id') or d[0].get('materialId')
                r4 = requests.get(BASE + '/materials/' + str(mat_id) + '/download', headers=headers, timeout=15, stream=True)
                ct = r4.headers.get('Content-Type', '')
                print('  GET /materials/{}/download: {} {}'.format(mat_id, r4.status_code, ct))
                if r4.status_code != 200:
                    print('  error:', r4.text[:200])
        else:
            print('  data:', str(d)[:200])
    else:
        print('  error:', r3.text[:200])
