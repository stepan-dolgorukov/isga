import csv
import os
import secrets
import smtplib
import sys
from email.message import EmailMessage
from urllib.parse import urlencode

SMTP_HOST = os.environ.get("SMTP_HOST", "mailpit")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "security-team@company.local")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8084").rstrip("/")
CSV_PATH = os.environ.get("CSV_PATH", "users.csv")


def read_users(path: str):
    users = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            value = row[0].strip()
            if not value or value.lower() == "email":
                continue
            users.append(value)
    return users


def build_link(email: str, token: str) -> str:
    query = urlencode({"email": email, "token": token})
    return f"{BASE_URL}/?{query}"


def build_message(email: str, link: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "Требуется подтверждение учётной записи"
    msg["From"] = MAIL_FROM
    msg["To"] = email

    msg.set_content(
        "Здравствуйте!\n\n"
        "Мы зафиксировали необычную активность в вашей учётной записи.\n"
        "Пожалуйста, подтвердите вход по ссылке:\n\n"
        f"{link}\n\n"
        "С уважением,\nСлужба поддержки"
    )
    return msg


def main() -> int:
    try:
        users = read_users(CSV_PATH)
    except FileNotFoundError:
        print(f"[!] CSV-файл не найден: {CSV_PATH}", file=sys.stderr)
        return 1

    if not users:
        print("[!] В CSV нет ни одного пользователя.", file=sys.stderr)
        return 1

    print(f"[*] Отправка писем: {len(users)} получател(ь/я/ей)")
    print(f"[*] SMTP: {SMTP_HOST}:{SMTP_PORT}")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        if SMTP_USER:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)

        for email in users:
            token = secrets.token_hex(8)
            link = build_link(email, token)
            msg = build_message(email, link)
            server.send_message(msg)
            print(f"    -> {email:<25} token={token}")
            print(f"       {link}")

    print("[+] Готово.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
