import os
import sqlite3

import app

TMP = "/tmp/_tracker_test.db"


def test_record_click():
    app.DB_PATH = TMP
    if os.path.exists(TMP):
        os.remove(TMP)
    app.init_db()

    assert app.record_click("a@test.ru", "tok", "1.2.3.4") is True
    assert app.record_click("", "", "1.2.3.4") is False

    rows = list(sqlite3.connect(TMP).execute("SELECT email, token, ip FROM clicks"))
    assert rows == [("a@test.ru", "tok", "1.2.3.4")], rows
    print("ok")


if __name__ == "__main__":
    test_record_click()
