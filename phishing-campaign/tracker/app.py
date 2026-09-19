import os
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DB_PATH = os.environ.get("DB_PATH", "/data/phishing.db")

PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Учебная фишинговая рассылка</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#f3f4f6;
color:#1f2937;display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0}
.card{max-width:560px;margin:24px;padding:32px 36px;background:#fff;border-radius:14px;
box-shadow:0 10px 30px rgba(0,0,0,.08);border-top:6px solid #dc2626}
h1{color:#dc2626;font-size:22px;margin:0 0 12px}p{line-height:1.6;font-size:16px}
</style></head>
<body><div class="card">
<h1>Вы перешли по учебной фишинговой ссылке.</h1>
<p>Если данное письмо вызвало подозрение — сообщите об этом
в отдел информационной безопасности.</p>
</div></body></html>"""


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS clicks("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "email TEXT, token TEXT, ip TEXT, created_at TEXT NOT NULL)"
        )


def record_click(email, token, ip):
    if not (email or token):
        return False
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "INSERT INTO clicks(email, token, ip, created_at) VALUES(?,?,?,?)",
            (email, token, ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
    return True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        email = q.get("email", [""])[0]
        token = q.get("token", [""])[0]
        ip = self.headers.get("X-Real-IP", self.client_address[0])
        record_click(email, token, ip)

        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    init_db()
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
