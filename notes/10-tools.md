# 10. 信息收集与工具使用

> 渗透测试中，信息收集的质量决定了攻击面的大小。

## 🔍 信息收集层次

```
第一层：被动收集（不接触目标）
  └─ Google Hacking、Shodan、Whois、DNS 查询、SSL 证书、GitHub 泄露、Web Archive

第二层：主动收集（直接扫描目标）
  └─ 端口扫描、目录爆破、指纹识别、爬虫

第三层：漏洞扫描
  └─ 自动化扫描器、手动测试
```

## 🛠️ 核心工具

### 1. Burp Suite（Web 渗透核心）

```
┌─────────────────────────────────┐
│  Proxy        │ 抓包、修改请求    │  ← 用得最多
│  Repeater     │ 重复发送、调参    │  ← 手动测试
│  Intruder     │ 自动化爆破        │  ← 枚举/跑字典
│  Scanner      │ 自动漏洞扫描      │  ← 专业版才有
│  Decoder      │ 编解码            │
│  Comparer     │ 对比请求/响应     │
└─────────────────────────────────┘
```

**必学**：设置代理 → 抓包 → 修改 → Repeater 重放

### 2. Nmap（端口扫描）

```bash
nmap -sV 192.168.1.1         # 服务版本检测
nmap -sC 192.168.1.1         # 默认脚本扫描
nmap -p- 192.168.1.1         # 扫全部端口(1-65535)
nmap -O 192.168.1.1          # 操作系统检测
nmap -A 192.168.1.1          # 综合扫描（激进）
```

### 3. SQLMap（SQL 注入自动化）

```bash
sqlmap -u "http://target.com/page?id=1"          # 基础扫描
sqlmap -u "http://target.com/page?id=1" --dbs     # 列出数据库
sqlmap -u "http://target.com/page?id=1" -D db --tables  # 列库中的表
sqlmap -u "http://target.com/page?id=1" -D db -T users --dump  # 导出数据
sqlmap -r request.txt           # 从 Burp 抓的请求文件注入
sqlmap -u "..." --os-shell      # 尝试获取系统 Shell（有风险）
```

### 4. Dirb / Gobuster / Dirsearch（目录爆破）

```bash
dirb http://target.com /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://target.com -w wordlist.txt
dirsearch -u http://target.com -e php,asp,js,html
```

常见发现：
```
/admin
/backup
/phpmyadmin
/.git/
/.env
/robots.txt
/server-status
```

### 5. Wireshark（网络协议分析）

用于分析网络流量、抓包、排查问题。

### 6. Nikto（Web 服务器扫描）

```bash
nikto -h http://target.com
```

检查：过时的服务器软件、危险文件、配置问题。

## 🔎 Google Hacking（被动收集）

```
site:target.com                  # 限定站点
site:target.com filetype:pdf     # 搜索 PDF（可能有敏感信息）
site:target.com inurl:admin      # 管理后台
site:target.com intitle:"index of"  # 目录浏览
site:target.com "password"       # 可能包含密码的页面
site:github.com target.com       # GitHub 上可能泄露的代码
site:pastebin.com target.com     # Pastebin 泄露
```

## 🐳 Docker 环境（推荐）

你不用装一堆工具，用 Docker 一键搭建渗透环境：

```
docker pull kalilinux/kali-rolling
docker run -it kalilinux/kali-rolling /bin/bash
```

或者直接用 Kali Linux 虚拟机。

## 📚 在线资源

| 资源 | 链接 |
|------|------|
| PortSwigger Academy | https://portswigger.net/web-security |
| HackTheBox | https://www.hackthebox.com |
| TryHackMe | https://tryhackme.com |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ |
| HackerOne Hacktivity | https://hackerone.com/hacktivity |

---

## 📝 总结

恭喜你完成了 10 个 Web 安全基础知识的学习！

接下来建议：
1. 把靶场每个漏洞都亲手练习一遍
2. 去 PortSwigger Academy 刷免费实验
3. 试着修改靶场代码 → 看看防御措施怎么加
4. 关注 HackerOne 上的公开漏洞报告

> 🎯 安全是不断学习的过程，保持好奇心和动手精神！
