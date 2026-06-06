# 8. IDOR 不安全的直接对象引用

## 是什么？

Insecure Direct Object References — 当应用通过用户可控的 ID 来引用对象（如用户资料、订单），但没有验证该用户是否有权限访问时，攻击者只需改 ID 就能看到别人的数据。

## 🧠 原理

```
URL: /profile?id=1   → 看到用户 1 的信息
改成: /profile?id=2   → 看到用户 2 的信息！
改成: /profile?id=3   → 看到用户 3 的信息！
```

```python
# 不安全的代码
@app.route('/profile')
def profile():
    user_id = request.args['id']
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    return render_template('profile.html', user=user)
    # ⚠️ 没有检查当前登录用户是否有权看这个 ID！
```

## 🎯 靶场练习 8：IDOR

打开 `http://127.0.0.1:5000/idor/profile`

### 练习

```
1. 访问 /idor/profile?id=1       → 看到 admin 用户和密码
2. 改成 /idor/profile?id=2       → 看到 test 用户和密码
3. 改成 /idor/profile?id=3       → 看到 alice 用户和密码
```

—— 不需要登录就能看到所有用户的信息！

## 💀 真实案例

### 案例 1：Facebook IDOR（2013）
修改 `?user_id=` 参数可查看任何用户的私信、支付信息。

### 案例 2：AT&T iPad 泄露（2010）
通过修改 URL 中的 ICC-ID 参数，获取了 11.4 万 iPad 用户的邮箱地址。

### 案例 3：外卖平台
修改订单号查看其他用户的订单（地址、电话、点了什么）。

## 🎯 IDOR 常出现的地方

```
/profile?id=123           → 用户资料
/invoice?file=INV-001     → 发票文件
/api/orders/12345         → RESTful API
/download?file=report.pdf → 文件下载
/reset-password?uid=123   → 密码重置
/admin?user_id=456        → 管理员功能
```

## 🧪 如何发现 IDOR

### 方法 1：枚举 ID

```
遍历：id=1, 2, 3, 4...
使用 Burp Suite Intruder 自动遍历
```

### 方法 2：创建两个账号对比

```
账号 A：查看自己的资料 → 抓包
账号 B：把 A 的 ID 换成 B 的 → 看能不能看
```

### 方法 3：注意 UUID

```
如果 ID 不是自增数字而是 UUID（如 a1b2c3d4...），相对更安全
但仍然要验证权限——UUID 只是猜不到，不代表不该验证
```

## 🛡️ 防御方法

### ✅ 1. 使用当前用户上下文（最重要）

```python
# ✅ 安全的代码
@app.route('/profile')
@login_required
def profile():
    user = db.query("SELECT * FROM users WHERE id=?", (current_user.id,))
    return render_template('profile.html', user=user)
    # 直接取当前登录用户的 ID，不接收参数
```

### ✅ 2. 验证权限

```python
@app.route('/order/<order_id>')
@login_required
def view_order(order_id):
    order = Order.get(order_id)
    if order.user_id != current_user.id:
        abort(403)  # 不是你的订单
    return render_template('order.html', order=order)
```

### ✅ 3. 使用间接引用

```python
# 不用真实 ID，用随机的引用标识
# URL: /order/a3f2b1c  (不是 /order/123)

mapping = {'a3f2b1c': 123, 'd4e5f6g': 456}
```

---

## 📝 练习

1. 在靶场尝试不同 ID，观察返回结果
2. 思考：遇到 UUID 作为 ID 就安全了吗？

---

**下一步**：[SSRF 服务器请求伪造](09-ssrf.md)
