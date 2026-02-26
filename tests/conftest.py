import os
import sqlite3
import tempfile

import pytest

import app as m


@pytest.fixture
def client():
    fd, temp_db = tempfile.mkstemp(prefix="meta90_test_", suffix=".db")
    os.close(fd)

    old_db = m.DB_PATH
    m.DB_PATH = temp_db
    m.app.config["TESTING"] = True
    m.crear_base_datos()

    test_client = m.app.test_client()
    try:
        yield test_client, temp_db
    finally:
        m.DB_PATH = old_db
        try:
            os.remove(temp_db)
        except OSError:
            pass


def db_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
