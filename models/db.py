import sqlite3
import os
from flask import g, current_app


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE_PATH'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        schema_path = os.path.join(os.path.dirname(db_path), 'schema.sql')
        seed_path = os.path.join(os.path.dirname(db_path), 'seed.sql')
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        if os.path.exists(seed_path):
            with open(seed_path, 'r') as f:
                conn.executescript(f.read())
        conn.close()


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


def update_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.rowcount
