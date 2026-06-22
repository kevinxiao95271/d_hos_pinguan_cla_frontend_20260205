import urllib.request, json, ssl

ctx = ssl._create_unverified_context()

def req(url, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers, method=method)
    with urllib.request.urlopen(r, context=ctx) as resp:
        return json.loads(resp.read())

BASE = 'http://zkjb.zjmss.org.cn/api'

# 1. 登录
login = req(f'{BASE}/auth/login-with-password', 'POST', {'phone': '13754322649', 'password': '589856'})
token = login['data']['token']
print('登录成功, role:', login['data'].get('role'))

# 2. 获取决赛任务
tasks_res = req(f'{BASE}/reviews/final/my-tasks', token=token)
tasks = tasks_res.get('data') or []
print('决赛任务数:', len(tasks))

# 取第一个 PENDING 任务
task = next((t for t in tasks if t.get('status') == 'PENDING'), None)
if not task:
    print('没有 PENDING 任务')
    exit()

task_id = task.get('taskId')
score_form = task.get('scoreForm')
project = task.get('projectName')
print(f'选取任务: [{task_id}] {project} | scoreForm={score_form}')

# 3. 保存草稿 86 分
payload = {'scoreForm': score_form, 'total': 86}
draft_res = req(f'{BASE}/reviews/final/scores/{task_id}/draft', 'PUT', payload, token=token)
print('保存草稿结果:', draft_res.get('success'), draft_res.get('message'))

# 4. 重新拉任务列表，确认草稿分
tasks_res2 = req(f'{BASE}/reviews/final/my-tasks', token=token)
tasks2 = tasks_res2.get('data') or []
t2 = next((t for t in tasks2 if t.get('taskId') == task_id), None)
if t2:
    print('草稿分 draftScore.total:', t2.get('draftScore', {}).get('total') if t2.get('draftScore') else '无草稿')
    print('任务状态:', t2.get('status'))
else:
    print('未找到任务')
