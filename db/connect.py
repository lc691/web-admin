from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor

from config import PGDATABASE, PGHOST, PGPASSWORD, PGPORT, PGUSER
from configs.logging_setup import log


@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=PGHOST,
            port=PGPORT,
            dbname=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD,
        )
        yield conn
    except psycopg2.Error as e:
        log.error("❌ Gagal koneksi ke database:", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()
            log.debug("🔌 Koneksi database ditutup.")


@contextmanager
def get_db_cursor(commit=False):
    """
    Mendapatkan cursor standar, dengan opsi commit otomatis jika diperlukan.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor, conn
            finally:
                if commit:
                    conn.commit()


@contextmanager
def get_dict_cursor():
    """
    Mendapatkan cursor dengan hasil Dict (key nama kolom).
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            yield cursor, conn


@contextmanager
def get_autocommit_cursor():
    """
    Cursor untuk operasi cepat (insert/update/delete) tanpa perlu panggil conn.commit().
    """
    with get_db_connection() as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            yield cursor


def get_dict_cursor_dep():
    conn = psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        dbname=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
    )
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        yield cursor, conn
    finally:
        cursor.close()
        conn.close()
