# 4. CSRF 跨站请求伪造

## 是什么？

CSRF（Cross-Site Request Forgery）利用用户已登录的身份，在用户不知情的情况下，以用户的名义发起恶意请求。

## 🧠 原理

```
1. 用户登录了银行网站 bank.com（Cookie 有效）
2. 用户又打开了恶意网站 evil.com
3. evil.com 的页面自动向 bank.com/transfer 发起请求
4. 浏览器自动带上 bank.com 的 Cookie
5. 银行以为是用户本人操作 → 转账成功！
```

**关键**：浏览器会自动带上目标网站的 Cookie，不管请求是从哪个页面发起的。

## 💀 真实案例

1. **Gmail CSRF (2007)** — 攻击者可创建邮件过滤器，把用户邮件转发到自己邮箱
2. **Netflix CSRF (2006)** — 修改用户邮寄地址、添加 DVD 到队列
3. **ING Direct** — 创建额外账户

## 🛡️ 防御方法

### ✅ 1. CSRF Token（最有效）

```html
<form method="POST" action="/transfer">
  <input type="hidden" name="csrf_token" value="随机生成的token">
  ...
</form>
```

服务器验证 token 是否匹配。攻击者无法猜到这个 token。

```python
# Flask 示例
# 生成 token
session['csrf_token'] = os.urandom(32).hex()

# 验证 token
if request.form['csrf_token'] != session['csrf_token']:
    abort(403)
```

### ✅ 2. SameSite Cookie

```http
Set-Cookie: session=abc; SameSite=Strict
Set-Cookie: session=abc; SameSite=Lax
```

| 值 | 效果 |
|----|------|
| Strict | 跨站一概不带 Cookie（最严） |
| Lax | 跨站导航（GET 链接）会带，POST/ajax 不带 |
| None | 跨站也能带（不设防） |

### ✅ 3. 验证 Referer/Origin 头

```python
referer = request.headers.get('Referer', '')
if not referer.startswith('https://my-site.com'):
    abort(403)
```

> ⚠️ Referer 可能被隐藏或伪造，作为辅助手段。

### ✅ 4. 关键操作二次验证

- 转账前输入密码/验证码
- 修改密码前要求输入旧密码

## 📊 CSRF vs XSS

| | CSRF | XSS |
|------|------|-----|
| 攻击目标 | 利用已登录状态，发起请求 | 在用户浏览器执行脚本 |
| 是否读响应 | 不能读（同源策略） | 可以 |
| 受害者 | 已登录的用户 | 访问页面的任何人 |
| 防御 | CSRF Token、SameSite | 输出编码、CSP |

---

## 📝 练习

1. 访问 `http://127.0.0.1:5000/csrf/transfer`，先正常用一次
2. 创建 `csrf_attack.html`，用浏览器打开，观察是否自动转账成功
3. 思考：加上 CSRF Token 后，攻击为什么就不行了？

---

**下一步**：[命令注入](05-command-injection.md)
