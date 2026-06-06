"""
Web 安全漏洞靶场 —— 仅供学习使用！
包含常见 Web 漏洞的故意脆弱代码，用于理解攻击原理和防御方法。
⚠️ 请勿将此代码部署到公网！
"""
import sqlite3
import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory

app = Flask(__name__)
app.secret_key = 'insecure-secret-key-for-lab'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ──────────────────────────────────────────────
#  数据库初始化（故意用明文密码）
# ──────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'lab.db'))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT   -- ⚠️ 故意明文存储密码（不安全！）
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            content TEXT   -- ⚠️ 故意不转义（XSS 靶场用）
        )
    ''')
    # 插入测试数据
    conn.executescript('''
        INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123');
        INSERT OR IGNORE INTO users VALUES (2, 'test', 'test');
        INSERT OR IGNORE INTO users VALUES (3, 'alice', 'password');
        INSERT OR IGNORE INTO posts VALUES (1, '欢迎来到黑客数据库', '这是第一个帖子，请多多指教！');
        INSERT OR IGNORE INTO posts VALUES (2, '安全公告', '系统维护中，请勿上传敏感文件。');
    ''')
    conn.commit()
    conn.close()
    print('[OK] 数据库初始化完成')

# ──────────────────────────────────────────────
#  首页
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ╔══════════════════════════════════════════════╗
# ║  漏洞1：SQL 注入 (SQL Injection)            ║
# ╚══════════════════════════════════════════════╝

@app.route('/sqli/login', methods=['GET', 'POST'])
def sqli_login():
    """
    练习1：SQL 注入登录绕过
    目标：不用密码，以 admin 身份登录
    提示：admin' OR '1'='1' --
    """
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        # ⚠️ 故意拼接 SQL（不安全！）
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        message = f"[DEBUG] 执行的 SQL: {query}"
        try:
            result = conn.execute(query).fetchone()
            if result:
                message = f"✅ 登录成功！欢迎 {result['username']} —— SQL 注入成功绕过了密码验证"
            else:
                message += "\n❌ 登录失败"
        except Exception as e:
            message += f"\n⚠️ SQL 错误: {e}"
        conn.close()
    return render_template('sqli_login.html', message=message)

@app.route('/sqli/search', methods=['GET', 'POST'])
def sqli_search():
    """
    练习2：SQL 注入联合查询
    目标：通过 UNION 注入获取 users 表数据
    提示：' UNION SELECT 1,username,password FROM users--
    """
    message = ''
    results = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = get_db()
        query = f"SELECT * FROM posts WHERE title LIKE '%{keyword}%' OR content LIKE '%{keyword}%'"
        message = f"[DEBUG] 执行的 SQL: {query}"
        try:
            cursor = conn.execute(query)
            results = cursor.fetchall()
            if not results:
                message += "\n没有找到结果"
        except Exception as e:
            message += f"\n⚠️ SQL 错误: {e}"
        conn.close()
    return render_template('sqli_search.html', message=message, results=results)

# ╔══════════════════════════════════════════════╗
# ║  漏洞2：XSS 跨站脚本攻击                     ║
# ╚══════════════════════════════════════════════╝

@app.route('/xss/reflected')
def xss_reflected():
    """
    练习3：反射型 XSS
    目标：注入 JavaScript 代码弹窗
    提示：?name=<script>alert('XSS')</script>
    """
    name = request.args.get('name', '')
    # ⚠️ 故意不过滤 HTML（不安全！）
    return render_template('xss_reflected.html', name=name)

@app.route('/xss/stored', methods=['GET', 'POST'])
def xss_stored():
    """
    练习4：存储型 XSS
    目标：提交包含 JavaScript 的评论，让其他用户访问时执行
    提示：<script>alert(document.cookie)</script>
    """
    conn = get_db()
    if request.method == 'POST':
        content = request.form['content']
        conn.execute("INSERT INTO comments (post_id, content) VALUES (1, ?)", (content,))
        conn.commit()
    comments = conn.execute("SELECT * FROM comments ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('xss_stored.html', comments=comments)

# ╔══════════════════════════════════════════════╗
# ║  漏洞3：命令注入 (Command Injection)         ║
# ╚══════════════════════════════════════════════╝

@app.route('/cmdi/ping', methods=['GET', 'POST'])
def cmdi_ping():
    """
    练习5：命令注入
    目标：在 Ping 功能中注入额外命令
    提示：127.0.0.1 & whoami
    提示：127.0.0.1 | dir  (Windows)
    提示：127.0.0.1; ls   (Linux)
    """
    result = ''
    if request.method == 'POST':
        ip = request.form['ip']
        # ⚠️ 故意拼接命令（不安全！）
        cmd = f"ping -n 3 {ip}" if os.name == 'nt' else f"ping -c 3 {ip}"
        try:
            result = subprocess.getoutput(cmd)
        except Exception as e:
            result = str(e)
    return render_template('cmdi_ping.html', result=result)

# ╔══════════════════════════════════════════════╗
# ║  漏洞4：文件上传漏洞                          ║
# ╚══════════════════════════════════════════════╝

@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    """
    练习6：任意文件上传
    目标：上传一个 Web Shell（如 PHP、Python 脚本）
    提示：先试试上传 .py 文件，再尝试访问它
    """
    message = ''
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # ⚠️ 故意不检查文件类型和扩展名（不安全！）
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            message = f"✅ 文件已上传到 /uploads/{file.filename}"
    return render_template('upload.html', message=message)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # ⚠️ 故意允许访问任意上传文件（不安全！）
    return send_from_directory(UPLOAD_FOLDER, filename)

# ╔══════════════════════════════════════════════╗
# ║  漏洞5：路径遍历 (Path Traversal)            ║
# ╚══════════════════════════════════════════════╝

@app.route('/file/view')
def file_view():
    """
    练习7：路径遍历
    目标：读取系统敏感文件
    提示：?file=../../../etc/passwd  (Linux)
    提示：?file=../../../windows/win.ini  (Windows)
    """
    filename = request.args.get('file', '')
    content = ''
    error = ''
    if filename:
        # ⚠️ 故意不限制路径（不安全！）
        filepath = os.path.join(BASE_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            error = str(e)
    return render_template('file_view.html', content=content, error=error, filename=filename)

# ╔══════════════════════════════════════════════╗
# ║  漏洞6：IDOR (不安全的直接对象引用)           ║
# ╚══════════════════════════════════════════════╝

@app.route('/idor/profile')
def idor_profile():
    """
    练习8：IDOR 越权访问
    目标：查看其他用户的敏感信息
    提示：试试 ?id=1 改成 ?id=2
    """
    user_id = request.args.get('id', '1')
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if user:
        return f"""
        <h2>用户资料</h2>
        <p>ID: {user['id']}</p>
        <p>用户名: {user['username']}</p>
        <p>密码: {user['password']}</p>
        <p><a href="?id={int(user_id)-1}">← 上一个</a> | <a href="?id={int(user_id)+1}">下一个 →</a></p>
        <a href="/">返回首页</a>
        """
    return "用户不存在 <a href='/'>返回首页</a>"

# ╔══════════════════════════════════════════════╗
# ║  漏洞7：CSRF (跨站请求伪造)                   ║
# ╚══════════════════════════════════════════════╝

@app.route('/csrf/transfer', methods=['GET', 'POST'])
def csrf_transfer():
    """
    练习9：CSRF 攻击
    目标：构造恶意页面，诱导用户点击完成转账
    注意：此页面故意不验证 Referer 和 CSRF Token
    """
    message = ''
    if request.method == 'POST':
        to = request.form.get('to', '')
        amount = request.form.get('amount', '')
        # ⚠️ 故意不做 CSRF 防护（不安全！）
        message = f"✅ 已向 {to} 转账 {amount} 元（模拟）"
    return render_template('csrf_transfer.html', message=message)

# ╔══════════════════════════════════════════════╗
# ║  漏洞8：SSRF (服务端请求伪造)                 ║
# ╚══════════════════════════════════════════════╝

@app.route('/ssrf/fetch', methods=['GET', 'POST'])
def ssrf_fetch():
    """
    练习10：SSRF 攻击
    目标：让服务器请求内网地址
    提示：http://127.0.0.1:5000/admin
    提示：http://169.254.169.254/ (云元数据)
    """
    import urllib.request as urllib_req
    content = ''
    error = ''
    if request.method == 'POST':
        url = request.form['url']
        # ⚠️ 故意不限制 URL 目标（不安全！）
        try:
            resp = urllib_req.urlopen(url, timeout=5)
            content = resp.read().decode('utf-8', errors='ignore')[:2000]
        except Exception as e:
            error = str(e)
    return render_template('ssrf_fetch.html', content=content, error=error)

# ──────────────────────────────────────────────
#  启动
# ──────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("""
============================================================
    Web 安全漏洞靶场 - 仅供学习使用，请勿部署到公网！
    访问 http://127.0.0.1:5000 开始练习
============================================================
    """)
    app.run(debug=True, host='127.0.0.1', port=5000)
