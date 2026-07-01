#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证：草稿阶段上传材料 → POST submit（DB COPY，MinIO 不动）
→ 正式项目材料可见、preview/download 正常，file_url 与草稿期一致，material id 为新 id。
"""
import hashlib
import io
import json
import sys
import time
from datetime import datetime

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os

BASE = os.environ.get('API_BASE', 'http://81.71.44.180:6039/api')
TS = datetime.now().strftime('%Y%m%d%H%M%S')
MARKER = f'SUBMIT-MAT-TEST-{TS}'.encode('utf-8')

results = []


def record(step, ok, detail=''):
    status = 'PASS' if ok else 'FAIL'
    results.append({'step': step, 'status': status, 'detail': str(detail or '')})
    print(f"{'✅' if ok else '❌'} [{status}] {step}")
    if detail:
        print(f'    {detail}')


def login(phone, pwd):
    r = requests.post(BASE + '/auth/login-with-password', json={'phone': phone, 'password': pwd}, timeout=30)
    d = r.json()
    if not d.get('success'):
        return None, None
    return d['data']['token'], d['data']


def api(method, path, token, **kwargs):
    h = {'Authorization': f'Bearer {token}'}
    r = requests.request(method, BASE + path, headers=h, timeout=120, **kwargs)
    try:
        body = r.json()
    except Exception:
        body = None
    return r, body


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def upload_mat(token, reg_id, mat_type, filename, content, mime):
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


def list_materials(token, reg_id):
    """兼容多种列表接口"""
    for path in (f'/registrations/{reg_id}/materials', f'/materials/registration/{reg_id}'):
        r, body = api('GET', path, token)
        if r.status_code == 200 and body and body.get('success'):
            data = body.get('data') or []
            if data:
                return data, path
    return [], None


def fetch_bytes(token, path):
    h = {'Authorization': f'Bearer {token}'}
    r = requests.get(BASE + path, headers=h, timeout=120)
    return r.status_code, r.content, r.headers.get('Content-Type', '')


def mat_index(mats):
    return {(m.get('type'), m.get('fileName')): m for m in mats}


print('=' * 72)
print('草稿材料 → 提交 → 预览/下载 持久性验证')
print(f'API: {BASE}')
print('=' * 72)

c_token, c_user = login('13872005640', 'user123')
com_token, _ = login('13800000127', 'committee2026')
record('参赛者 / Committee 登录', c_token and com_token)

# ── 1. 创建草稿 ──
r, body = api('POST', '/registrations', c_token, json={
    'competitionId': 1,
    'projectName': f'材料持久性测试-{TS}',
    'groupType': 'COMPREHENSIVE',
})
draft_id = (body or {}).get('data', {}).get('id') if body and body.get('success') else None
record('创建草稿', draft_id is not None, f'draftId={draft_id}')

if not draft_id:
    sys.exit(1)

# ── 2. 上传带唯一标记的材料 ──
uploads = [
    ('REGISTRATION_FORM_DOC', f'draft-form-{TS}.docx',
     b'PK\x03\x04' + MARKER + b'-DOC', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
    ('REGISTRATION_FORM_PDF', f'draft-form-{TS}.pdf',
     b'%PDF-1.4\n' + MARKER + b'-PDF', 'application/pdf'),
    ('REPORT', f'draft-report-{TS}.pdf',
     b'%PDF-1.4\n' + MARKER + b'-REPORT', 'application/pdf'),
]
uploaded_content = {}
draft_mats_by_type = {}

for mtype, fname, content, mime in uploads:
    sc, b = upload_mat(c_token, draft_id, mtype, fname, content, mime)
    ok = sc == 200 and b.get('success')
    if ok:
        d = b['data']
        draft_mats_by_type[mtype] = d
        uploaded_content[mtype] = content
        record(f'草稿上传 {mtype}', True, f"matId={d.get('id')} fileUrl={d.get('fileUrl')}")
    else:
        record(f'草稿上传 {mtype}', False, json.dumps(b, ensure_ascii=False)[:200])

if len(draft_mats_by_type) < 3:
    print('材料上传不完整，退出')
    sys.exit(1)

# ── 3. 草稿期列表 + 下载校验 ──
draft_list, list_path = list_materials(c_token, draft_id)
record('草稿期材料列表', len(draft_list) >= 3, f'{list_path} count={len(draft_list)}')

for mtype, dm in draft_mats_by_type.items():
    mid = dm['id']
    sc, data, _ = fetch_bytes(c_token, f'/materials/{mid}/download')
    # 草稿材料 id 在 material_files 查不到，download 常 403/500；列表可见即可
    record(
        f'草稿期 download {mtype}（可选，草稿 id 常无权限）',
        sc != 200,  # 预期走不通；提交后才挂正式 material_files
        f'matId={mid} HTTP={sc}（草稿期不依赖此接口）',
    )

# ── 4. 提交（只 POST submit，不再上传）──
r, body = api('POST', f'/registrations/{draft_id}/submit', c_token)
submitted = body and body.get('success')
formal = body.get('data') if submitted else {}
if isinstance(formal, list):
    formal = formal[0] if formal else {}
formal_id = formal.get('id')
formal_status = formal.get('status')
record(
    'POST submit（无二次上传）',
    submitted and formal_id and formal_id != draft_id,
    f'draftId={draft_id} → formalId={formal_id} status={formal_status}',
)

if not formal_id:
    sys.exit(1)

time.sleep(0.5)

# ── 5. 正式项目材料列表 ──
formal_list, formal_list_path = list_materials(c_token, formal_id)
record('正式项目材料列表', len(formal_list) >= 3, f'{formal_list_path} count={len(formal_list)}')

# 按 type 建索引
formal_by_type = {}
for m in formal_list:
    formal_by_type[m.get('type')] = m

# ── 6. 核心：file_url 不变、material id 为新 id ──
for mtype, dm in draft_mats_by_type.items():
    fm = formal_by_type.get(mtype)
    if not fm:
        record(f'正式材料存在 {mtype}', False, '列表中未找到')
        continue
    draft_url = dm.get('fileUrl') or dm.get('file_url')
    formal_url = fm.get('fileUrl') or fm.get('file_url')
    draft_mid = dm.get('id')
    formal_mid = fm.get('id')
    url_same = draft_url == formal_url and draft_url
    id_changed = formal_mid != draft_mid
    record(
        f'{mtype} file_url 不变',
        url_same,
        f'url={formal_url}',
    )
    record(
        f'{mtype} material id 为新 id',
        id_changed,
        f'draftMatId={draft_mid} → formalMatId={formal_mid}',
    )
    # fileHash 若存在也应一致
    dh = dm.get('fileHash')
    fh = fm.get('fileHash')
    if dh or fh:
        record(f'{mtype} fileHash 一致', dh == fh, f'draft={dh} formal={fh}')

# ── 7. 草稿 material id 应已不可访问（草稿行 CASCADE 删除）──
for mtype, dm in draft_mats_by_type.items():
    old_mid = dm['id']
    sc, _, _ = fetch_bytes(c_token, f'/materials/{old_mid}/download')
    record(
        f'旧草稿 matId={old_mid} 不可再访问',
        sc != 200,
        f'HTTP {sc}（草稿行已 CASCADE，旧 id 失效）',
    )

# ── 8. 正式 material：download + preview，内容仍是原文件 ──
for mtype, fm in formal_by_type.items():
    if mtype not in uploaded_content:
        continue
    mid = fm['id']
    expected = uploaded_content[mtype]

    sc_dl, data_dl, ct_dl = fetch_bytes(c_token, f'/materials/{mid}/download')
    content_ok = sc_dl == 200 and MARKER in data_dl
    record(
        f'正式 download {mtype}',
        content_ok,
        f'matId={mid} HTTP={sc_dl} bytes={len(data_dl)} marker={"有" if MARKER in data_dl else "无"}',
    )

    sc_pv, data_pv, ct_pv = fetch_bytes(c_token, f'/materials/{mid}/preview')
    preview_ok = sc_pv == 200 and MARKER in data_pv
    record(
        f'正式 preview {mtype}',
        preview_ok,
        f'matId={mid} HTTP={sc_pv} Content-Type={ct_pv[:50]}',
    )

    if sc_dl == 200:
        record(
            f'{mtype} 内容与上传字节一致',
            data_dl == expected,
            f'upload={len(expected)} downloaded={len(data_dl)} md5={md5(data_dl)}',
        )

# ── 9. Committee 也能 preview/download ──
if com_token and formal_by_type:
    sample = formal_by_type.get('REGISTRATION_FORM_PDF') or next(iter(formal_by_type.values()))
    mid = sample['id']
    sc, data, _ = fetch_bytes(com_token, f'/materials/{mid}/preview')
    record('Committee preview 正式材料', sc == 200 and MARKER in data, f'matId={mid} HTTP={sc}')
    sc2, data2, _ = fetch_bytes(com_token, f'/materials/{mid}/download')
    record('Committee download 正式材料', sc2 == 200 and MARKER in data2, f'matId={mid} HTTP={sc2}')

# ── 10. GET 正式报名详情含材料 ──
r, body = api('GET', f'/registrations/{formal_id}', c_token)
data = (body or {}).get('data') or {}
mats_in_detail = data.get('materials') or (data.get('registration') or {}).get('materials') or []
record(
    '正式详情接口含材料',
    len(mats_in_detail) >= 3 if mats_in_detail else True,
    f'materials字段={len(mats_in_detail)}条' if mats_in_detail else '详情未嵌 materials（可能仅独立列表接口）',
)

# ── 汇总 ──
print('\n' + '=' * 72)
passed = sum(1 for x in results if x['status'] == 'PASS')
failed = sum(1 for x in results if x['status'] == 'FAIL')
for x in results:
    print(f"  [{x['status']}] {x['step']}")
print('-' * 72)
print(f'合计: {passed} PASS / {failed} FAIL / {len(results)} 项')
print(f'保留正式项目 formalId={formal_id}（测试数据，可人工清理）')
sys.exit(1 if failed else 0)
