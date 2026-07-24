"""
Database Configuration dan Connection Management - Complete Implementation

Menyediakan:
- Connection pooling dengan psycopg2
- Context managers untuk cursor dan koneksi
- FastAPI dependencies
- Health check
- Query execution helpers
- Transaction management
- Connection retry logic
"""

from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
import time
import logging

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import DictCursor, RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)


# =====================================================
# CONNECTION POOL
# =====================================================

class DatabasePool:
    """
    Database connection pool manager.
    """
    
    _pool: Optional[SimpleConnectionPool] = None
    _initialized: bool = False
    
    @classmethod
    def initialize(cls, min_conn: int = 2, max_conn: int = 10) -> None:
        """
        Initialize connection pool.
        
        Args:
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        if cls._initialized:
            return
        
        try:
            cls._pool = SimpleConnectionPool(
                min_conn,
                max_conn,
                host=settings.PGHOST,
                port=settings.PGPORT,
                dbname=settings.PGDATABASE,
                user=settings.PGUSER,
                password=settings.PGPASSWORD,
                connect_timeout=10,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
            )
            cls._initialized = True
            logger.info(f"✅ Database connection pool initialized: min={min_conn}, max={max_conn}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """
        Get a connection from the pool.
        
        Returns:
            Database connection
        """
        if not cls._initialized:
            cls.initialize()
        
        try:
            return cls._pool.getconn()
        except Exception as e:
            logger.error(f"❌ Failed to get connection from pool: {e}")
            raise
    
    @classmethod
    def return_connection(cls, conn) -> None:
        """
        Return connection to the pool.
        
        Args:
            conn: Database connection
        """
        if cls._pool and cls._initialized:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_all(cls) -> None:
        """
        Close all connections in the pool.
        """
        if cls._pool and cls._initialized:
            cls._pool.closeall()
            cls._initialized = False
            logger.info("🔌 All database connections closed")


# =====================================================
# CONTEXT MANAGERS
# =====================================================

@contextmanager
def get_db_connection(use_pool: bool = True):
    """
    Mendapatkan koneksi database dengan context manager.
    
    Args:
        use_pool: Use connection pool if True
        
    Yields:
        psycopg2.connection: Koneksi database
    """
    conn = None
    try:
        if use_pool:
            conn = DatabasePool.get_connection()
        else:
            conn = psycopg2.connect(
                host=settings.PGHOST,
                port=settings.PGPORT,
                dbname=settings.PGDATABASE,
                user=settings.PGUSER,
                password=settings.PGPASSWORD,
                connect_timeout=10,
            )
        
        logger.debug("✅ Database connection acquired")
        yield conn
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Database connection error: {e}")
        raise
    except psycopg2.Error as e:
        logger.error(f"❌ Database error: {e}")
        raise
    finally:
        if conn:
            if use_pool and DatabasePool._initialized:
                DatabasePool.return_connection(conn)
                logger.debug("🔌 Connection returned to pool")
            else:
                conn.close()
                logger.debug("🔌 Connection closed")


@contextmanager
def get_db_cursor(commit: bool = False, use_pool: bool = True):
    """
    Mendapatkan cursor standar dengan opsi commit otomatis.
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        use_pool: Use connection pool if True
        
    Yields:
        Tuple[cursor, connection]: Cursor dan koneksi database
    """
    with get_db_connection(use_pool=use_pool) as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor, conn
                if commit:
                    conn.commit()
                    logger.debug("✅ Transaction committed")
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Transaction rolled back: {e}")
                raise


@contextmanager
def get_dict_cursor(commit: bool = False, use_pool: bool = True):
    """
    Mendapatkan cursor dengan hasil Dict (key nama kolom).
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        use_pool: Use connection pool if True
        
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
    """
    with get_db_connection(use_pool=use_pool) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                yield cursor, conn
                if commit:
                    conn.commit()
                    logger.debug("✅ Transaction committed")
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Transaction rolled back: {e}")
                raise


@contextmanager
def get_real_dict_cursor(commit: bool = False, use_pool: bool = True):
    """
    Mendapatkan cursor dengan RealDictCursor (results as dict).
    
    Args:
        commit: Jika True, auto-commit setelah selesai
        use_pool: Use connection pool if True
        
    Yields:
        Tuple[RealDictCursor, connection]: RealDictCursor dan koneksi
    """
    with get_db_connection(use_pool=use_pool) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                yield cursor, conn
                if commit:
                    conn.commit()
                    logger.debug("✅ Transaction committed")
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Transaction rolled back: {e}")
                raise


# =====================================================
# FASTAPI DEPENDENCIES (LENGKAP)
# =====================================================

def get_dict_cursor_dep():
    """
    FASTAPI DEPENDENCY - Untuk operasi READ (tanpa commit otomatis)
    Digunakan di endpoint GET / search / list / detail
    
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
    """
    with get_dict_cursor(commit=False) as (cursor, conn):
        yield cursor, conn


def get_dict_cursor_dep_commit():
    """
    FASTAPI DEPENDENCY - Untuk operasi WRITE (dengan commit otomatis)
    Digunakan di endpoint POST / PUT / DELETE
    
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
    """
    with get_dict_cursor(commit=True) as (cursor, conn):
        yield cursor, conn


# =====================================================
# ALIAS / SHORTCUT FUNCTIONS
# =====================================================

@contextmanager
def get_dict_cursor_with_commit():
    """
    Alias untuk get_dict_cursor dengan commit=True.
    Digunakan untuk operasi WRITE dengan commit otomatis.
    
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
        
    Example:
        with get_dict_cursor_with_commit() as (cursor, conn):
            cursor.execute("INSERT INTO ...")
            # Auto-commit setelah keluar context
    """
    with get_dict_cursor(commit=True) as (cursor, conn):
        yield cursor, conn


@contextmanager
def get_dict_cursor_no_commit():
    """
    Alias untuk get_dict_cursor dengan commit=False.
    Digunakan untuk operasi READ tanpa commit.
    
    Yields:
        Tuple[DictCursor, connection]: DictCursor dan koneksi database
        
    Example:
        with get_dict_cursor_no_commit() as (cursor, conn):
            cursor.execute("SELECT ...")
            # Tidak ada auto-commit
    """
    with get_dict_cursor(commit=False) as (cursor, conn):
        yield cursor, conn


@contextmanager
def get_cursor_with_commit():
    """
    Alias untuk get_db_cursor dengan commit=True.
    
    Yields:
        Tuple[cursor, connection]: Cursor dan koneksi database
    """
    with get_db_cursor(commit=True) as (cursor, conn):
        yield cursor, conn


@contextmanager
def get_cursor_no_commit():
    """
    Alias untuk get_db_cursor dengan commit=False.
    
    Yields:
        Tuple[cursor, connection]: Cursor dan koneksi database
    """
    with get_db_cursor(commit=False) as (cursor, conn):
        yield cursor, conn


# =====================================================
# DEPRECATED FUNCTIONS (untuk backward compatibility)
# =====================================================

@contextmanager
def get_autocommit_cursor():
    """
    [DEPRECATED] Cursor untuk operasi cepat tanpa commit manual.
    Gunakan get_dict_cursor_dep_commit() untuk FastAPI.
    """
    import warnings
    warnings.warn(
        "get_autocommit_cursor is deprecated. Use get_dict_cursor_dep_commit()",
        DeprecationWarning,
        stacklevel=2
    )
    with get_db_connection() as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                yield cursor
            except Exception as e:
                logger.error(f"❌ Error pada autocommit cursor: {e}")
                raise


@contextmanager
def get_clean_dict_cursor(commit: bool = False):
    """
    [DEPRECATED] Mendapatkan DictCursor dengan rollback otomatis.
    Gunakan get_dict_cursor_dep() atau get_dict_cursor_dep_commit().
    """
    import warnings
    warnings.warn(
        "get_clean_dict_cursor is deprecated. Use get_dict_cursor_dep() or get_dict_cursor_dep_commit()",
        DeprecationWarning,
        stacklevel=2
    )
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                yield cursor
                if commit:
                    conn.commit()
                    logger.debug("✅ Commit berhasil")
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Rollback terjadi: {e}")
                raise

# =====================================================
# QUERY EXECUTION HELPERS
# =====================================================

def execute_query(
    query: str,
    params: Optional[Union[tuple, dict]] = None,
    fetch_one: bool = False,
    fetch_all: bool = False,
) -> Any:
    """
    Eksekusi query dan return hasil.
    
    Args:
        query: SQL query
        params: Parameter query
        fetch_one: Jika True return satu baris
        fetch_all: Jika True return semua baris
        
    Returns:
        List atau Dict hasil query
    """
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        
        # Return affected rows count for INSERT/UPDATE/DELETE
        return cursor.rowcount


def execute_query_dict(
    query: str,
    params: Optional[dict] = None,
) -> List[Dict[str, Any]]:
    """
    Eksekusi query dan return hasil sebagai list of dicts.
    
    Args:
        query: SQL query
        params: Parameter query sebagai dict
        
    Returns:
        List of dicts
    """
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def execute_query_one(
    query: str,
    params: Optional[Union[tuple, dict]] = None,
    default: Any = None,
) -> Optional[Dict[str, Any]]:
    """
    Eksekusi query dan return satu baris.
    
    Args:
        query: SQL query
        params: Parameter query
        default: Default value if no rows
        
    Returns:
        Dict atau default
    """
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else default


def execute_transaction(queries: List[Tuple[str, Union[tuple, dict]]]) -> bool:
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
                logger.debug("✅ Transaction committed successfully")
                return True
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Transaction failed: {e}")
            return False


def execute_transaction_with_result(
    queries: List[Tuple[str, Union[tuple, dict]]],
    return_query: Optional[str] = None,
    return_params: Optional[Union[tuple, dict]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Eksekusi transaksi dan return hasil dari query terakhir.
    
    Args:
        queries: List of (query, params) tuples
        return_query: Query untuk return hasil
        return_params: Parameters untuk return_query
        
    Returns:
        Dict hasil query atau None
    """
    with get_db_connection() as conn:
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                for query, params in queries:
                    cursor.execute(query, params)
                
                if return_query:
                    cursor.execute(return_query, return_params)
                    row = cursor.fetchone()
                    result = dict(row) if row else None
                else:
                    result = {'rowcount': cursor.rowcount}
                
                conn.commit()
                logger.debug("✅ Transaction committed successfully")
                return result
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Transaction failed: {e}")
            raise


# =====================================================
# BULK OPERATIONS HELPERS
# =====================================================

def execute_bulk_insert(
    table: str,
    columns: List[str],
    values: List[tuple],
    page_size: int = 1000,
) -> int:
    """
    Execute bulk insert with pagination.
    
    Args:
        table: Table name
        columns: List of column names
        values: List of value tuples
        page_size: Number of rows per insert
        
    Returns:
        Total rows inserted
    """
    if not values:
        return 0
    
    total_inserted = 0
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cursor:
                for i in range(0, len(values), page_size):
                    page = values[i:i + page_size]
                    query = f"""
                        INSERT INTO {table} ({columns_str})
                        VALUES ({placeholders})
                    """
                    cursor.executemany(query, page)
                    total_inserted += len(page)
                
                conn.commit()
                logger.info(f"✅ Bulk insert complete: {total_inserted} rows")
                return total_inserted
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Bulk insert failed: {e}")
            raise


def execute_bulk_update(
    table: str,
    set_column: str,
    where_column: str,
    updates: Dict[Any, Any],
    page_size: int = 1000,
) -> int:
    """
    Execute bulk update with pagination.
    
    Args:
        table: Table name
        set_column: Column to update
        where_column: Column for WHERE clause
        updates: Dict mapping where_value -> set_value
        page_size: Number of rows per update
        
    Returns:
        Total rows updated
    """
    if not updates:
        return 0
    
    total_updated = 0
    items = list(updates.items())
    
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cursor:
                for i in range(0, len(items), page_size):
                    page = items[i:i + page_size]
                    for where_value, set_value in page:
                        query = f"""
                            UPDATE {table}
                            SET {set_column} = %s
                            WHERE {where_column} = %s
                        """
                        cursor.execute(query, (set_value, where_value))
                        total_updated += cursor.rowcount
                
                conn.commit()
                logger.info(f"✅ Bulk update complete: {total_updated} rows")
                return total_updated
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Bulk update failed: {e}")
            raise


# =====================================================
# HEALTH CHECK
# =====================================================

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
                logger.info("✅ Database connection test successful")
                return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


def get_db_status() -> Dict[str, Any]:
    """
    Get database status information.
    
    Returns:
        Dict with database status
    """
    try:
        with get_dict_cursor() as (cursor, conn):
            # Get PostgreSQL version
            cursor.execute("SELECT version()")
            version = cursor.fetchone()['version']
            
            # Get database size
            cursor.execute("""
                SELECT pg_database_size(%s) as size
            """, (settings.PGDATABASE,))
            size = cursor.fetchone()['size']
            
            # Get active connections
            cursor.execute("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity
                WHERE datname = %s AND state = 'active'
            """, (settings.PGDATABASE,))
            active_connections = cursor.fetchone()['active_connections']
            
            # Get total connections
            cursor.execute("""
                SELECT count(*) as total_connections
                FROM pg_stat_activity
                WHERE datname = %s
            """, (settings.PGDATABASE,))
            total_connections = cursor.fetchone()['total_connections']
            
            # Get pool status
            pool_status = {
                'initialized': DatabasePool._initialized,
                'min_conn': 2 if DatabasePool._initialized else 0,
                'max_conn': 10 if DatabasePool._initialized else 0,
            }
            
            return {
                'status': 'healthy',
                'version': version,
                'database': settings.PGDATABASE,
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'active_connections': active_connections,
                'total_connections': total_connections,
                'pool': pool_status,
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to get database status: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
        }


# =====================================================
# MIGRATION HELPERS
# =====================================================

def table_exists(table_name: str) -> bool:
    """
    Check if a table exists.
    
    Args:
        table_name: Table name
        
    Returns:
        bool: True if table exists
    """
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = %s
        )
    """
    return execute_query(query, (table_name,), fetch_one=True)[0]


def column_exists(table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in a table.
    
    Args:
        table_name: Table name
        column_name: Column name
        
    Returns:
        bool: True if column exists
    """
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        )
    """
    return execute_query(query, (table_name, column_name), fetch_one=True)[0]


def get_table_columns(table_name: str) -> List[str]:
    """
    Get all column names for a table.
    
    Args:
        table_name: Table name
        
    Returns:
        List of column names
    """
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """
    result = execute_query(query, (table_name,), fetch_all=True)
    return [row['column_name'] for row in result] if result else []


# =====================================================
# CLEANUP
# =====================================================

def close_all_connections() -> None:
    """
    Close all database connections.
    """
    DatabasePool.close_all()
    logger.info("🔌 All database connections closed")


# =====================================================
# INITIALIZATION
# =====================================================

def init_database() -> None:
    """
    Initialize database connection pool.
    Called on application startup.
    """
    try:
        DatabasePool.initialize()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    # Connection pool
    'DatabasePool',
    'init_database',
    'close_all_connections',
    
    # Context managers
    'get_db_connection',
    'get_db_cursor',
    'get_dict_cursor',
    'get_real_dict_cursor',
    
    # FastAPI dependencies
    'get_dict_cursor_with_commit',    # <-- TAMBAHAN BARU
    'get_dict_cursor_no_commit',      # <-- TAMBAHAN BARU
    'get_cursor_with_commit',         # <-- TAMBAHAN BARU
    'get_cursor_no_commit',           # <-- TAMBAHAN BARU
    
    # Query execution
    'execute_query',
    'execute_query_dict',
    'execute_query_one',
    'execute_transaction',
    'execute_transaction_with_result',
    
    # Bulk operations
    'execute_bulk_insert',
    'execute_bulk_update',
    
    # Health check
    'test_connection',
    'get_db_status',
    
    # Migration helpers
    'table_exists',
    'column_exists',
    'get_table_columns',
]