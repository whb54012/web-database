# 1. HTTP 基础与 Web 工作原理

## 什么是 HTTP？

HTTP（HyperText Transfer Protocol）是 Web 的基石——浏览器和服务器之间通信的「语言」。

## 🔄 请求-响应模型

```
浏览器（客户端）                    服务器
    │                               │
    │ ──── HTTP Request ──────────> │
    │    GET /index.html HTTP/1.1   │
    │    Host: example.com          │
    │                               │
    │ <──── HTTP Response ───────── │
    │    HTTP/1.1 200 OK            │
    │    <html>...                  │
```

## 📨 HTTP 请求结构

```
POST /login HTTP/1.1              ← 请求行：方法 + 路径 + 协议版本
Host: example.com                 ← 请求头
User-Agent: Mozilla/5.0
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123
                                  ← 空行
username=admin&password=123456    ← 请求体（POST 才有）
```

### 常见请求方法

| 方法 | 含义 | 特点 |
|------|------|------|
| GET | 获取资源 | 参数在 URL 中，可缓存，可收藏 |
| POST | 提交数据 | 参数在请求体中，相对安全 |
| PUT | 更新资源（完整） | 幂等 |
| DELETE | 删除资源 | — |
| PATCH | 更新资源（部分） | — |
| OPTIONS | 查询支持的方法 | CORS 预检 |

## 📬 HTTP 响应结构

```
HTTP/1.1 200 OK                   ← 状态行：协议版本 + 状态码 + 原因短语
Content-Type: text/html           ← 响应头
Set-Cookie: session=xyz
Content-Length: 1234
                                  ← 空行
<!DOCTYPE html>                   ← 响应体
<html>...
```

### 常见状态码

| 状态码 | 含义 |
|--------|------|
| **200** | OK — 成功 |
| **301** | 永久重定向 |
| **302** | 临时重定向 |
| **400** | 请求错误 |
| **401** | 未认证 |
| **403** | 禁止访问 |
| **404** | 未找到 |
| **500** | 服务器内部错误 |
| **502** | 网关错误 |

## 🍪 Cookie 和 Session

### 为什么需要？

HTTP 是**无状态**协议——服务器不记得你刚做过什么。Cookie 和 Session 解决了这个问题。

### Cookie
- 浏览器端存储的小段数据
- 每次请求自动发送给服务器
- 可设置过期时间、HttpOnly、Secure 等属性

### Session
- 服务器端存储的用户数据
- 通过 Session ID（存在 Cookie 中）关联
- Session ID 被窃取 = 账号被盗（会话劫持）

## 🔐 HTTPS

```
HTTP  明文传输 ── 可以被抓包查看
HTTPS TLS 加密 ── 中间人看不到内容
```

HTTPS = HTTP + TLS/SSL

### TLS 握手简述：
1. 客户端发送支持的加密算法列表
2. 服务器选择算法，返回数字证书
3. 客户端验证证书
4. 双方协商出对称密钥
5. 之后的数据用对称密钥加密

## 🌐 URL 结构

```
https://user:pass@example.com:8080/path/page?key=value#anchor
└─┬──┘ └──┘ └─┬┘ └─────────┘ └──┘ └────────┘ └──────────┘ └──┬─┘
协议   用户 密码   主机名      端口   路径     查询参数       锚点
```

## 🧰 浏览器开发者工具（F12）

安全测试最常用的面板：

| 面板 | 用途 |
|------|------|
| **Network** | 抓包，查看所有请求/响应 |
| **Console** | 执行 JS，查看报错 |
| **Storage** | 查看 Cookie、localStorage |
| **Elements** | 查看/修改 DOM 和 CSS |
| **Application** | Cookie、Session 管理 |

## 🎯 安全相关的重要 HTTP 头

| 头部 | 作用 |
|------|------|
| `X-Frame-Options` | 防止点击劫持 |
| `Content-Security-Policy` | 防止 XSS |
| `X-Content-Type-Options` | 防止 MIME 嗅探 |
| `Strict-Transport-Security` | 强制 HTTPS |
| `Set-Cookie: HttpOnly` | 防止 JS 读取 Cookie |
| `Set-Cookie: Secure` | 只在 HTTPS 下发送 |

## 📝 动手实验

1. 打开浏览器 F12 → Network 面板
2. 访问任意网站
3. 点击某个请求，观察：
   - 请求 URL、方法、状态码
   - Request Headers 和 Response Headers
   - Cookie 的 Domain、Path、HttpOnly、Secure 属性

---

**下一步**：[SQL 注入](02-sql-injection.md)
