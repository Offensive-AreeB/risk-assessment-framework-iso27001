import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'grc_app.db')

def get_db_connection():
    """Establish and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db_session():
    """Context manager for database sessions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize the database using the schema.sql file."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        
    with db_session() as conn:
        conn.executescript(schema_sql)

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Execute a parameterized query and optionally return results."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        
        return cursor.lastrowid
