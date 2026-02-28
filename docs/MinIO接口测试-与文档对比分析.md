# MinIO接口测试 - 与文档对比分析

**测试时间：** 2026-02-27  
**测试环境：** `http://localhost:6031/api`  
**测试账号：** 13300005566 (参赛者)

---

## 🚨 核心问题汇总

| 问题 | 严重程度 | 影响 |
|------|---------|------|
| **问题1**: 模版API未加入白名单 | 🔴 高 | 用户无法下载模版，注册流程无法完成 |
| **问题2**: 列表API返回500错误 | 🔴 高 | 管理后台列表页无法使用 |
| **问题3**: 材料下载API不存在 | 🔴 高 | 无法下载材料文件 |

---

## 📊 详细测试结果

### ❌ 问题1：模版API未加入JWT白名单

#### 测试接口1：`GET /api/system-templates/active`

**文档说明：**
- ✅ 公开接口（无需JWT token）
- ✅ 用户注册后下载模版使用
- ✅ URL永久有效

**实际测试：**
```bash
GET http://localhost:6031/api/system-templates/active
```

**实际结果：**
```
HTTP Status: 401 Unauthorized
```

**问题分析：**
- ❌ **后端未将此接口加入JWT白名单**
- ❌ 调用时返回401，要求提供token
- ❌ 与文档描述不符（文档明确说是公开接口）

**影响：**
- 用户注册后无法下载模版
- 前端调用此接口会触发"登录已过期"错误
- 导致注册页面无法正常使用

---

#### 测试接口2：`GET /api/system-templates/{id}/download`

**文档说明：**
- ✅ 公开接口（无需JWT token）
- ✅ URL永久有效
- ✅ 支持最大30MB文件
- ✅ 中文文件名支持

**实际测试：**
```bash
GET http://localhost:6031/api/system-templates/1/download
```

**实际结果：**
```
HTTP Status: 401 Unauthorized
```

**问题分析：**
- ❌ **后端未将此接口加入JWT白名单**
- ❌ 与文档描述不符

---

### ❌ 问题2：列表API返回500错误

#### 测试接口3：`GET /api/admin/registrations/filter`

**文档说明：**
- ✅ 后台报名筛选列表API
- ✅ 响应中应包含 `materials` 字段
- ✅ 每个材料包含：id, type, fileName, downloadUrl

**文档预期响应：**
```json
{
  "success": true,
  "data": [
    {
      "registrationId": 123,
      "projectName": "xxx",
      "materials": [
        {
          "id": 456,
          "type": "registration_form",
          "fileName": "xxx.docx",
          "downloadUrl": "/api/materials/456/download"
        }
      ]
    }
  ]
}
```

**实际测试：**
```bash
GET http://localhost:6031/api/admin/registrations/filter?competitionId=1&status=SUBMITTED
Authorization: Bearer {token}
```

**实际结果：**
```json
{
  "timestamp": "2026-02-27T13:24:55.025+00:00",
  "status": 500,
  "error": "Internal Server Error",
  "path": "/api/admin/registrations/filter"
}
```

**问题分析：**
- ❌ **后端代码抛出500异常**
- ⚠️ 可能原因：
  1. 后端尝试关联查询 `materials` 字段时出错
  2. `MaterialFileRepository.findByRegistrationIdIn` 方法可能不存在或有bug
  3. DTO字段映射错误
  4. 数据库关联查询语法错误

**影响：**
- 管理后台书审/面谈分组列表页无法加载
- 组委会、评委无法查看项目列表
- 核心功能完全瘫痪

---

### ❌ 问题3：材料下载API不存在

#### 测试接口4：`GET /api/materials/{id}/download`

**文档说明：**
- ✅ 下载报名材料文件
- ✅ 需要JWT token
- ✅ 带权限控制（参赛者、评委、组委会、OPS）

**实际测试：**
```bash
GET http://localhost:6031/api/materials/1/download
Authorization: Bearer {token}
```

**实际结果：**
```
HTTP Status: 404 Not Found
```

**问题分析：**
- ❌ **后端未实现此API**
- ⚠️ MaterialController中可能缺少 `download` 方法

**影响：**
- 无法下载材料文件
- 管理后台材料预览功能无法使用
- 详情页下载按钮无效

---

## 🔧 需要后端修复的问题

### 修复1：将模版API加入JWT白名单

**文件：** `JwtAuthorizationFilter.java`

**需要添加（约第54行）：**

```java
// 5. 系统模版下载接口（公开）
if ("GET".equalsIgnoreCase(method) && 
    (path.equals("/api/system-templates/active") || 
     path.matches("^/api/system-templates/\\d+/download$"))) {
    filterChain.doFilter(request, response);
    return;
}
```

**说明：**
- 必须添加这段代码，否则前端无法下载模版
- 这是文档明确说明的"公开接口"要求

---

### 修复2：修复列表API的500错误

**可能的问题位置：**

#### A. MaterialFileRepository缺少方法

**文件：** `MaterialFileRepository.java`

**需要添加：**
```java
/**
 * 批量查询多个报名的材料文件
 */
@Query("SELECT m FROM MaterialFile m WHERE m.registration.id IN :registrationIds")
List<MaterialFile> findByRegistrationIdIn(@Param("registrationIds") List<Long> registrationIds);
```

#### B. RegistrationService关联查询错误

**文件：** `RegistrationService.java`

**检查 `filterRegistrations` 方法：**
- 是否正确调用了 `materialFileRepository.findByRegistrationIdIn(registrationIds)`
- 是否正确设置了 `item.setMaterials()`
- 是否有空指针异常

#### C. RegistrationFilterItem缺少materials字段

**文件：** `RegistrationFilterItem.java`

**需要添加：**
```java
private List<MaterialFileSimple> materials;

@Data
@AllArgsConstructor
@NoArgsConstructor
public static class MaterialFileSimple {
    private Long id;
    private String type;
    private String fileName;
    private String downloadUrl;
}
```

**检查建议：**
1. 查看后端日志，找到具体的500错误堆栈信息
2. 检查是否所有相关代码都已实现
3. 检查数据库表和关联关系是否正确

---

### 修复3：实现材料下载API

**文件：** `MaterialController.java`

**需要添加方法：**

```java
@GetMapping("/{id}/download")
@Operation(summary = "下载材料文件")
public ResponseEntity<InputStreamResource> download(@PathVariable Long id) {
    MaterialFile material = materialService.getById(id);
    
    // 从 MinIO 获取文件流
    String bucketName = minioProperties.getBucket().getRegistrationFiles();
    InputStream inputStream = fileStorageService.getInputStream(
        material.getFileUrl(), bucketName
    );
    
    // URL 编码文件名（支持中文）
    String encodedFilename;
    try {
        encodedFilename = URLEncoder.encode(material.getFileName(), "UTF-8")
            .replace("+", "%20");
    } catch (UnsupportedEncodingException e) {
        throw new IllegalStateException("UTF-8 encoding not supported", e);
    }
    
    return ResponseEntity.ok()
        .contentType(MediaType.APPLICATION_OCTET_STREAM)
        .header(HttpHeaders.CONTENT_DISPOSITION, 
                "attachment; filename*=UTF-8''" + encodedFilename)
        .body(new InputStreamResource(inputStream));
}
```

**同时需要在 MaterialService 添加：**

```java
public MaterialFile getById(Long materialId) {
    return materialFileRepository.findById(materialId)
            .orElseThrow(() -> new IllegalArgumentException("材料文件不存在"));
}
```

---

## 📋 文档与实际不符汇总

### 1. 响应格式差异

**文档描述：**
```json
{
  "code": 200,
  "message": "success",
  "data": [...]
}
```

**实际可能是：**
```json
{
  "success": true,
  "data": [...],
  "message": null
}
```

**差异说明：**
- 文档使用 `code` 字段，实际可能使用 `success` 字段
- 前端已适配 `success` 格式（无需调整）

---

### 2. 公开接口未实现

**文档明确说明：**
- `/api/system-templates/active` - 公开接口
- `/api/system-templates/{id}/download` - 公开接口

**实际情况：**
- 返回401，需要token
- **后端未按文档实现白名单**

---

### 3. 材料字段未实现

**文档说明：**
- `GET /api/admin/registrations/filter` 应返回 `materials` 字段

**实际情况：**
- 返回500错误
- **后端可能未完成此功能开发**

---

## ✅ 后端需要完成的工作清单

### 🔴 P0 - 紧急（必须修复才能使用）

1. **修复列表API的500错误**
   - 检查后端日志，定位错误原因
   - 确保 `MaterialFileRepository.findByRegistrationIdIn` 方法存在
   - 确保 `RegistrationFilterItem` 有 `materials` 字段和setter
   - 确保 `RegistrationService.filterRegistrations` 正确关联查询材料

2. **将模版API加入JWT白名单**
   - 在 `JwtAuthorizationFilter.java` 添加白名单规则
   - 允许 `/api/system-templates/active` 和 `/api/system-templates/{id}/download` 无token访问

3. **实现材料下载API**
   - 在 `MaterialController.java` 添加 `download` 方法
   - 实现权限控制（参赛者只能下载自己的）

### 🟡 P1 - 重要（影响功能完整性）

4. **创建系统模版数据**
   - 运行 `init_system_templates_minio.py` 脚本
   - 上传两个模版文件到MinIO
   - 在数据库中创建记录

---

## 🧪 验证步骤（修复后）

### 1. 验证模版API

```bash
# 无需token，应该返回200
curl -X GET http://localhost:6031/api/system-templates/active

# 无需token，应该下载文件
curl -X GET http://localhost:6031/api/system-templates/1/download -o test.docx
```

### 2. 验证列表API

```bash
# 带token，应该返回200，且每项包含materials字段
curl -X GET "http://localhost:6031/api/admin/registrations/filter?competitionId=1" \
  -H "Authorization: Bearer {TOKEN}" | jq '.data[0].materials'
```

### 3. 验证材料下载API

```bash
# 带token，应该下载文件
curl -X GET http://localhost:6031/api/materials/1/download \
  -H "Authorization: Bearer {TOKEN}" -o material.docx
```

---

## 🎯 前端应对措施（临时）

在后端修复完成前，前端已做以下调整：

### 1. 禁用模版加载（已完成）

```javascript
// RegisterForm.vue - 约540行
// 临时注释掉模版加载，避免401导致登录过期
// loadTemplates().catch(err => {
//   console.warn('模版加载失败（不影响其他功能）:', err)
// })
```

**效果：** 用户可以正常编辑草稿，不会被401踢出登录

### 2. 材料列显示降级（已完成）

```vue
<!-- 材料列会显示"无材料"或"未上传"，不会报错 -->
<el-tag v-else type="info" size="small">无材料</el-tag>
```

**效果：** 列表页可以正常显示，只是暂时看不到材料信息

---

## 📝 给后端的修复指引

### 修复优先级顺序

#### 第1步：修复列表API 500错误（最紧急）

**原因：** 影响管理后台核心功能

**检查项：**
1. 查看后端日志，找到500错误的堆栈信息
2. 检查 `RegistrationService.filterRegistrations` 方法实现
3. 检查 `MaterialFileRepository` 是否有 `findByRegistrationIdIn` 方法
4. 检查 `RegistrationFilterItem` 是否有 `materials` 字段

**临时解决方案（如果来不及加materials字段）：**
- 先恢复原有的列表API，不返回materials字段
- 前端可以正常显示列表（只是看不到材料信息）
- 等materials功能完成后再逐步添加

---

#### 第2步：将模版API加入白名单（高优先级）

**文件：** `JwtAuthorizationFilter.java`

**添加位置：** `doFilterInternal` 方法中，约第54行

**代码：**
```java
// 5. 系统模版下载接口（公开）
if ("GET".equalsIgnoreCase(method)) {
    if (path.equals("/api/system-templates/active") || 
        path.matches("^/api/system-templates/\\d+/download$")) {
        filterChain.doFilter(request, response);
        return;
    }
}
```

**验证：**
```bash
# 不带token，应该返回200
curl -X GET http://localhost:6031/api/system-templates/active
```

---

#### 第3步：实现材料下载API（高优先级）

**文件：** `MaterialController.java`

**完整代码参考：** 见文档 `管理后台文件预览功能实施总结.md` 第123-148行

**核心要点：**
- 使用 `fileStorageService.getInputStream()` 从MinIO获取文件流
- 设置正确的Content-Type和Content-Disposition
- 支持中文文件名（URLEncoder）
- 返回 `InputStreamResource`

**验证：**
```bash
# 带token，应该下载文件
curl -X GET http://localhost:6031/api/materials/1/download \
  -H "Authorization: Bearer {TOKEN}" -o test.docx
```

---

#### 第4步：初始化模版数据（中优先级）

**运行脚本：**
```bash
cd /path/to/backend
python scripts/init_system_templates_minio.py
```

**验证：**
- MinIO控制台看到 `system-templates` bucket
- 数据库 `system_template_files` 表有2条记录
- API返回模版列表

---

## 🔍 后端调试建议

### 查看后端日志

**定位500错误：**
```bash
# 查看Spring Boot日志
tail -f /path/to/logs/application.log

# 或查看控制台输出
# 找到类似以下的堆栈信息：
# java.lang.NullPointerException: ...
# at com.trae.pinguan.service.RegistrationService.filterRegistrations(...)
```

### 使用Swagger测试

1. 访问：`http://localhost:6031/swagger-ui/index.html`
2. 找到 `/api/admin/registrations/filter` 接口
3. 点击 "Try it out" 测试
4. 查看详细的错误响应

### 数据库检查

```sql
-- 检查 material_files 表结构
DESC material_files;

-- 检查是否有测试数据
SELECT id, registration_id, file_name, type 
FROM material_files 
LIMIT 5;

-- 检查关联查询是否正常
SELECT 
    r.id AS registration_id,
    r.project_name,
    m.id AS material_id,
    m.file_name
FROM registrations r
LEFT JOIN material_files m ON m.registration_id = r.id
WHERE r.competition_id = 1
LIMIT 5;
```

---

## 📞 联系与协作

### 前端状态

- ✅ 前端代码已完成
- ⚠️ 临时禁用模版加载（避免401错误）
- ⚠️ 等待后端修复后启用

### 后端状态

- ❌ 模版API未加白名单
- ❌ 列表API返回500
- ❌ 材料下载API未实现
- ⚠️ 需要紧急修复

### 下一步

1. **后端优先修复列表API的500错误**（最紧急，影响现有功能）
2. **后端添加JWT白名单**（阻塞模版下载功能）
3. **后端实现材料下载API**（阻塞材料下载功能）
4. **后端修复完成后，前端取消模版加载的注释**

---

## ✅ 测试脚本

**位置：** `scripts/test_minio_apis.py`

**用途：** 快速测试所有MinIO相关API

**运行：**
```bash
python scripts/test_minio_apis.py
```

---

**测试完成时间：** 2026-02-27 21:24  
**测试人员：** AI Assistant  
**状态：** ❌ 发现3个高优先级问题需要后端修复
