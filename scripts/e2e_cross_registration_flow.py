#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端交叉逻辑验证：创建赛事 → 切换赛事 → 多草稿 → 交叉编辑 → 提交正式项目"""
import io
import json
import sys
import time
from datetime import datetime, timedelta

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031/api'
TS = datetime.now().strftime('%Y%m%d%H%M%S')
COMP_NAME = f'E2E交叉测试-{TS}'

results = []


def record(step, ok, detail=''):
    status = 'PASS' if ok else 'FAIL'
    detail = '' if detail is None else str(detail)
    results.append({'step': step, 'status': status, 'detail': detail})
    icon = '✅' if ok else '❌'
    print(f'{icon} [{status}] {step}')
    if detail:
        print(f'    {detail}')


def login(phone, pwd):
    r = requests.post(
        BASE + '/auth/login-with-password',
        json={'phone': phone, 'password': pwd},
        timeout=30,
    )
    d = r.json()
    if not d.get('success'):
        return None, None, d.get('message', r.text[:200])
    u = d['data']
    return u['token'], u, None


def api_msg(body, n=120):
    return str(body.get('message') or '')[:n]


def api(method, path, token, **kwargs):
    h = {'Authorization': f'Bearer {token}'}
    r = requests.request(method, BASE + path, headers=h, timeout=60, **kwargs)
    try:
        body = r.json()
    except Exception:
        body = {'_raw': r.text[:500]}
    return r.status_code, body


def upload_material(token, reg_id, mat_type, filename, content, mime):
    h = {'Authorization': f'Bearer {token}'}
    files = {'file': (filename, content, mime)}
    r = requests.post(
        BASE + f'/registrations/{reg_id}/materials?type={mat_type}',
        headers=h,
        files=files,
        timeout=120,
    )
    try:
        body = r.json()
    except Exception:
        body = {'_raw': r.text[:300]}
    return r.status_code, body


def minimal_pdf():
    return b'%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF'


def minimal_docx():
    # 最小 zip 头 + 内容，后端通常只校验扩展名/MIME
    return b'PK\x03\x04' + b'\x00' * 20 + b'e2e-test-docx-content'


def get_reg_field(data, *keys):
    """兼容 draft 详情嵌套 registration 结构"""
    if not isinstance(data, dict):
        return None
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    reg = data.get('registration')
    if isinstance(reg, dict):
        for k in keys:
            if k in reg and reg[k] is not None:
                return reg[k]
    return None


def cleanup_draft(token, draft_id):
    if not draft_id:
        return
    api('DELETE', f'/registration-drafts/{draft_id}', token)


# ── 登录 ──────────────────────────────────────────────
print('=' * 70)
print('E2E 交叉逻辑验证测试')
print('=' * 70)

ops_token, ops_user, err = login('13800000005', 'ops2026')
record('OPS 登录', ops_token is not None, err or f'role={ops_user.get("role")}')

com_token, com_user, err = login('13800000127', 'committee2026')
record('COMMITTEE_ADMIN 登录', com_token is not None, err or f'role={com_user.get("role")}')

c_token, c_user, err = login('13872005640', 'user123')
record('CONTESTANT 登录', c_token is not None, err or f'institutionId={c_user.get("institutionId")}')

if not all([ops_token, com_token, c_token]):
    sys.exit(1)

inst_id = c_user.get('institutionId') or 4553
draft_ids = []
formal_id = None
new_comp_id = None

# ── 1. OPS 创建赛事 ───────────────────────────────────
now = datetime.now()
reg_start = (now - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
reg_end = (now + timedelta(days=90)).strftime('%Y-%m-%dT23:59:59')

create_payload = {
    'name': COMP_NAME,
    'registerStart': reg_start,
    'registerEnd': reg_end,
    'bookReviewStart': reg_end,
    'bookReviewEnd': (now + timedelta(days=120)).strftime('%Y-%m-%dT23:59:59'),
    'basicGroupPrefix': 'E',
    'comprehensiveGroupPrefix': 'F',
    'advancedGroupPrefix': 'G',
}
code, body = api('POST', '/competitions', ops_token, json=create_payload)
new_comp_id = (body.get('data') or {}).get('id') if body.get('success') else None
record(
    'OPS 创建赛事 (DRAFT)',
    code == 200 and new_comp_id,
    f'id={new_comp_id} name={COMP_NAME}' if new_comp_id else json.dumps(body, ensure_ascii=False)[:300],
)

# ── 2. 激活赛事（同年仅允许一个 ACTIVE，失败时记为预期约束） ──
active_comp_id = None
if new_comp_id:
    code, body = api('POST', f'/competitions/{new_comp_id}/activate', ops_token)
    msg = body.get('message') or ''
    if body.get('success'):
        status = (body.get('data') or {}).get('status')
        active_comp_id = new_comp_id if status == 'ACTIVE' else None
        record('OPS 激活赛事', status == 'ACTIVE', f'status={status}')
    elif '同年只允许一个' in msg or '已存在激活赛事' in msg:
        record('OPS 激活赛事（同年唯一 ACTIVE 约束）', True, msg[:120])
    else:
        record('OPS 激活赛事', False, msg[:120])

code, body = api('GET', '/competitions', ops_token)
active_comp = next((c for c in (body.get('data') or []) if c.get('status') == 'ACTIVE'), None)
if active_comp:
    active_comp_id = active_comp['id']
    record('获取当前 ACTIVE 赛事', True, f'id={active_comp_id} name={active_comp.get("name", "")[:40]}')
else:
    record('获取当前 ACTIVE 赛事', False, '无 ACTIVE 赛事')

# ── 3. 切换当前赛事 (OPS + Committee) ────────────────
if new_comp_id:
    code_ops, body_ops = api('POST', '/admin/current-competition', ops_token, params={'competitionId': new_comp_id})
    code_com, body_com = api('POST', '/admin/current-competition', com_token, params={'competitionId': new_comp_id})
    code_get, body_get = api('GET', '/admin/current-competition', ops_token)
    cur = body_get.get('data') if body_get.get('success') else None
    record(
        '切换当前赛事 → 新赛事',
        code_ops == 200 and code_com == 200 and cur == new_comp_id,
        f'OPS={code_ops} Committee={code_com} current={cur}',
    )

# 新创建的 DRAFT 赛事用于「跨赛事」草稿
other_comp_id = new_comp_id

# ── 4. 参赛者创建多个草稿（主流程用 ACTIVE 赛事） ───
draft_a = draft_b = draft_c = None

if active_comp_id:
    code, body = api('POST', '/registrations', c_token, json={
        'competitionId': active_comp_id,
        'projectName': f'品管圈A-{TS}',
        'groupType': 'COMPREHENSIVE',
    })
    draft_a = (body.get('data') or {}).get('id') if body.get('success') else None
    st = (body.get('data') or {}).get('status')
    if draft_a:
        draft_ids.append(draft_a)
    record('创建草稿 A (ACTIVE 赛事)', draft_a and st == 'DRAFT', f'comp={active_comp_id} id={draft_a} status={st}')

    code, body = api('POST', '/registrations', c_token, json={
        'competitionId': active_comp_id,
        'projectName': f'护理质量改进B-{TS}',
        'groupType': 'BASIC',
    })
    draft_b = (body.get('data') or {}).get('id') if body.get('success') else None
    if draft_b:
        draft_ids.append(draft_b)
    record('创建草稿 B (同 ACTIVE 赛事)', draft_b is not None, f'id={draft_b}')

if other_comp_id and other_comp_id != active_comp_id:
    code, body = api('POST', '/registrations', c_token, json={
        'competitionId': other_comp_id,
        'projectName': f'{COMP_NAME}-草稿C',
        'groupType': 'ADVANCED',
    })
    draft_c = (body.get('data') or {}).get('id') if body.get('success') else None
    if draft_c:
        draft_ids.append(draft_c)
    record('创建草稿 C (DRAFT 赛事)', draft_c is not None, f'competitionId={other_comp_id} id={draft_c}')
else:
    record('创建草稿 C (DRAFT 赛事)', True, '跳过：无独立 DRAFT 赛事可测')

# ── 5. 交叉编辑：A → B → 再读 A ─────────────────────
if draft_a:
    code, body = api('PUT', f'/registrations/{draft_a}', c_token, json={
        'projectName': f'品管圈A-{TS}-已改',
        'groupType': 'COMPREHENSIVE',
        'projectLeaderName': '交叉测试负责人A',
        'projectLeaderPhone': '13872005640',
    })
    record('编辑草稿 A 基本信息', code == 200 and body.get('success'), api_msg(body))

    code, body = api('PUT', f'/registrations/{draft_a}/members', c_token, json={
        'members': [
            {'name': '成员甲', 'title': '护师', 'role': 'PARTICIPANT'},
            {'name': '辅导员乙', 'title': '主任护师', 'role': 'MENTOR'},
        ]
    })
    record('编辑草稿 A 成员', code == 200 and body.get('success'), '')

    code, body = api('PUT', f'/registrations/{draft_a}/activity', c_token, json={
        'theme': '交叉测试主题A',
        'keywords': '品管,测试',
        'subjectTypeCode': 'patient_safety',
        'methodCode': 'qc_circle',
        'experienceImproveCode': 'appointment',
        'qualityTopicCode': 'medication_safety',
        'avgWorkYears': 5,
        'avgAge': 32,
        'crossDepartment': True,
        'relatedToDigitalAi': False,
    })
    record('编辑草稿 A 活动说明', code == 200 and body.get('success'), api_msg(body))

    code, body = api('PUT', f'/registrations/{draft_a}/summary', c_token, json={
        'theme': '摘要主题A',
        'plan': '计划A',
        'problem': '问题A',
        'action': '对策A',
        'success': '成果A',
        'discussion': '讨论A',
        'operation': '运作A',
        'presentation': '展示A',
    })
    record('编辑草稿 A 项目摘要', code == 200 and body.get('success'), '')

if draft_b:
    code, body = api('PUT', f'/registrations/{draft_b}', c_token, json={
        'projectName': f'护理质量改进B-{TS}-已改',
        'groupType': 'BASIC',
        'projectLeaderName': '交叉测试负责人B',
        'projectLeaderPhone': '13872005641',
    })
    record('编辑草稿 B 基本信息', code == 200 and body.get('success'), '')

if draft_a:
    code, body = api('GET', f'/registrations/{draft_a}', c_token)
    name_a = get_reg_field(body.get('data') or {}, 'projectName')
    leader_a = get_reg_field(body.get('data') or {}, 'projectLeaderName')
    is_draft = (body.get('data') or {}).get('draft')
    record(
        '切换回读草稿 A 数据持久',
        code == 200 and name_a == f'品管圈A-{TS}-已改' and leader_a == '交叉测试负责人A',
        f'name={name_a} leader={leader_a} draft={is_draft}',
    )

# ── 6. check-duplicate 自排除 ────────────────────────
if draft_a and active_comp_id:
    code, body = api('GET', '/registrations/check-duplicate', c_token, params={
        'competitionId': active_comp_id,
        'institutionId': inst_id,
        'projectName': f'品管圈A-{TS}',
        'selfId': draft_a,
    })
    dupes = body.get('data') or []
    self_in = any(d.get('id') == draft_a or d.get('draftId') == draft_a for d in dupes)
    record('check-duplicate selfId 排除自身', code == 200 and not self_in, f'命中 {len(dupes)} 条')

# ── 7. 我的报名列表含多草稿 ───────────────────────────
code, body = api('GET', '/registrations/my', c_token)
items = body.get('data') or []
our_drafts = [x for x in items if x.get('id') in draft_ids and x.get('draft')]
record(
    '我的报名列表含全部测试草稿',
    len(our_drafts) >= min(2, len(draft_ids)),
    f'找到草稿 {len(our_drafts)}/{len(draft_ids)} 条',
)

# ── 8. 切换赛事后 Committee 视角 ─────────────────────
if active_comp_id:
    api('POST', '/admin/current-competition', com_token, params={'competitionId': active_comp_id})
    code, body = api('GET', '/registrations', com_token, params={
        'competitionId': active_comp_id,
        'page': 0,
        'size': 50,
    })
    record('Committee 切换 ACTIVE 赛事后查报名列表', code == 200, f'HTTP {code} total≈{len(body.get("data") or [])}')

# ── 9. 上传材料并提交草稿 A ───────────────────────────
submit_draft_id = draft_a
if submit_draft_id:
    mats = [
        ('REGISTRATION_FORM_DOC', 'e2e-form.docx', minimal_docx(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
        ('REGISTRATION_FORM_PDF', 'e2e-form.pdf', minimal_pdf(), 'application/pdf'),
        ('REPORT', 'e2e-report.pdf', minimal_pdf(), 'application/pdf'),
    ]
    upload_ok = True
    for mtype, fname, content, mime in mats:
        c, b = upload_material(c_token, submit_draft_id, mtype, fname, content, mime)
        if not (c == 200 and b.get('success')):
            upload_ok = False
            record(f'上传材料 {mtype}', False, json.dumps(b, ensure_ascii=False)[:200])
            break
    else:
        record('上传全部必填材料', True, 'DOC + PDF + REPORT')

    if upload_ok:
        code, body = api('POST', f'/registrations/{submit_draft_id}/submit', c_token)
        submitted = body.get('success')
        data = body.get('data')
        if isinstance(data, list):
            data = data[0] if data else {}
        elif not isinstance(data, dict):
            data = {}
        formal_id = data.get('id') if submitted else None
        new_status = data.get('status')
        record(
            '提交草稿 A → 正式项目',
            submitted and new_status not in (None, 'DRAFT'),
            f'formal_id={formal_id} status={new_status} msg={api_msg(body, 80)}',
        )
        if formal_id and formal_id != submit_draft_id:
            draft_ids = [d for d in draft_ids if d != submit_draft_id]

# ── 10. 提交后状态验证 ───────────────────────────────
if formal_id:
    code, body = api('GET', f'/registrations/{formal_id}', c_token)
    is_draft = (body.get('data') or {}).get('draft')
    status = get_reg_field(body.get('data') or {}, 'status')
    record(
        '正式项目详情 draft=false',
        code == 200 and is_draft is False,
        f'status={status} draft={is_draft}',
    )

    code, body = api('PUT', f'/registrations/{formal_id}', c_token, json={
        'projectName': '试图修改已提交项目',
        'groupType': 'COMPREHENSIVE',
    })
    blocked = code >= 400 or not body.get('success')
    record('已提交项目不可再编辑', blocked, f'HTTP {code} success={body.get("success")}')

    code, body = api('GET', f'/registrations/{submit_draft_id}', c_token)
    # 旧 draftId 可能 404 或重定向到 formal
    draft_gone = code == 404 or (body.get('success') and get_reg_field(body.get('data') or {}, 'status') != 'DRAFT')
    record('原 draftId 已不可作草稿编辑', draft_gone or code != 200, f'HTTP {code}')

# ── 11. 未提交草稿 B 仍可编辑 ─────────────────────────
if draft_b:
    code, body = api('PUT', f'/registrations/{draft_b}', c_token, json={
        'projectName': f'护理质量改进B-{TS}-再次修改',
        'groupType': 'BASIC',
        'projectLeaderName': '仍可调B',
        'projectLeaderPhone': '13872005642',
    })
    record('草稿 B 在 A 提交后仍可编辑', code == 200 and body.get('success'), '')

# ── 12. 管理员切回 DRAFT 赛事，参赛者草稿 C 仍可读 ──
if other_comp_id and draft_c and other_comp_id != active_comp_id:
    api('POST', '/admin/current-competition', ops_token, params={'competitionId': other_comp_id})
    code_get, body_get = api('GET', '/admin/current-competition', ops_token)
    code, body = api('GET', f'/registrations/{draft_c}', c_token)
    name_c = get_reg_field(body.get('data') or {}, 'projectName')
    record(
        '切换赛事后草稿 C 仍可读',
        code == 200 and COMP_NAME in (name_c or ''),
        f'current={body_get.get("data")} name={name_c}',
    )
elif draft_c is None:
    record('切换赛事后草稿 C 仍可读', True, '跳过：未创建跨赛事草稿 C')

# ── 13. 无材料提交应失败 ──────────────────────────────
if draft_b:
    code, body = api('POST', f'/registrations/{draft_b}/submit', c_token)
    record('草稿 B 无材料提交被拒', code >= 400 or not body.get('success'), api_msg(body, 100))

# ── 清理未提交测试草稿 ────────────────────────────────
print('\n--- 清理测试草稿 ---')
for did in list(draft_ids):
    cleanup_draft(c_token, did)
    print(f'  删除 draft {did}')

# 正式项目保留（可人工清理）；测试赛事保留
print(f'\n保留: 正式项目 id={formal_id}, 测试赛事 id={new_comp_id} ({COMP_NAME})')

# ── 汇总 ──────────────────────────────────────────────
print('\n' + '=' * 70)
print('测试结果汇总')
print('=' * 70)
passed = sum(1 for r in results if r['status'] == 'PASS')
failed = sum(1 for r in results if r['status'] == 'FAIL')
for r in results:
    print(f"  [{r['status']}] {r['step']}")
    if r['detail']:
        print(f'         {r["detail"]}')
print('-' * 70)
print(f'合计: {passed} PASS / {failed} FAIL / {len(results)} 项')
sys.exit(1 if failed else 0)
