"""
Database Configuration dan Connection Management
"""

from contextlib import contextmanager
from typing import Generator, Tuple, Any

import psycopg2
from psycopg2.extras import DictCursor

from app.core.config import settings
from app.utils.logger import log


@contextmanager
def get_db_connection():
    """
    Mendapatkan koneksi database dengan context manager.
    
    Yields:
        psycopg2.connection: Koneksi database
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.PGHOST,
            port=settings.PGPORT,
            dbname=settings.PGDATABASE,
            user=settings.PGUSER,
            password=settings.PGPASSWORD,
            connect_timeout=10,
        )
        log.debug("✅ Koneksi database berhasil")
        yield conn
    except psycopg2.Error as e:
        log.error(f"❌ Gagal koneksi ke database: {e}")
        raise
    finally:
        if conn:
            conn.close()
            log.debug("🔌 Koneksi database ditutup.")


@contextmanager
def get_db_cursor(commit: bool = False):
    """
    Mendapatkan cursor standar dengan opsi commit otomatis.
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        
    Yields:
        Tuple[cursor, connection]: Cursor dan koneksi database
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor, conn
                if commit:
                    conn.commit()
                    log.debug("✅ Commit berhasil")
            except Exception as e:
                conn.rollback()
                log.error(f"❌ Rollback terjadi: {e}")
                raise


@contextmanager
def get_dict_cursor(commit: bool = False):
    """
    Mendapatkan cursor dengan hasil Dict (key nama kolom).
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                yield cursor, conn
                if commit:
                    conn.commit()
                    log.debug("✅ Commit berhasil")
            except Exception as e:
                conn.rollback()
                log.error(f"❌ Rollback terjadi: {e}")
                raise


@contextmanager
def get_dict_cursor_dep(commit: bool = False):
    """
    [DEPRECATED] Mendapatkan DictCursor - legacy function.
    Gunakan get_dict_cursor() sebagai gantinya.
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
    """
    # Redirect ke get_dict_cursor untuk kompatibilitas
    with get_dict_cursor(commit) as (cursor, conn):
        yield cursor, conn


@contextmanager
def get_autocommit_cursor():
    """
    Cursor untuk operasi cepat (insert/update/delete) tanpa commit manual.
    
    Yields:
        cursor: Cursor dengan autocommit=True
    """
    with get_db_connection() as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            try:
                yield cursor
            except Exception as e:
                log.error(f"❌ Error pada autocommit cursor: {e}")
                raise


@contextmanager
def get_clean_dict_cursor(commit: bool = False):
    """
    Mendapatkan DictCursor dengan rollback otomatis jika error.
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        
    Yields:
        DictCursor: DictCursor untuk operasi database
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                yield cursor
                if commit:
                    conn.commit()
                    log.debug("✅ Commit berhasil")
            except Exception as e:
                conn.rollback()
                log.error(f"❌ Rollback terjadi: {e}")
                raise


# ================================
# FUNGSI BANTUAN
# ================================
def execute_query(query: str, params: tuple = None, fetch_one: bool = False) -> Any:
    """
    Eksekusi query dan return hasil.
    
    Args:
        query: SQL query
        params: Parameter query
        fetch_one: Jika True return satu baris, else return semua
        
    Returns:
        List atau Dict hasil query
    """
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(query, params)
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()


def execute_transaction(queries: list) -> bool:
    """
    Eksekusi multiple queries dalam satu transaksi.
    
    Args:
        queries: List of (query, params) tuples
        
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cursor:
                for query, params in queries:
                    cursor.execute(query, params)
                conn.commit()
                log.debug("✅ Transaksi berhasil")
                return True
        except Exception as e:
            conn.rollback()
            log.error(f"❌ Transaksi gagal: {e}")
            return False


# ================================
# TEST CONNECTION
# ================================
def test_connection() -> bool:
    """
    Test koneksi database.
    
    Returns:
        bool: True jika koneksi berhasil
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                log.info("✅ Database connection test successful")
                return True
    except Exception as e:
        log.error(f"❌ Database connection test failed: {e}")
        return False