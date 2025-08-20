#!/usr/bin/env python3
import sys
import sqlite3
import os

DB_FILE = "tags.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, path TEXT UNIQUE)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS file_tags (file_id INTEGER, tag_id INTEGER, PRIMARY KEY(file_id, tag_id))")
    conn.commit()
    return conn


def add(file_path, tags):
    conn = init_db()
    cur = conn.cursor()
    # Insert file
    cur.execute("INSERT OR IGNORE INTO files(path) VALUES(?)", (file_path,))
    conn.commit()
    cur.execute("SELECT id FROM files WHERE path=?", (file_path,))
    file_id = cur.fetchone()[0]
    # Insert tags
    for tag in tags:
        cur.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
        conn.commit()
        cur.execute("SELECT id FROM tags WHERE name=?", (tag,))
        tag_id = cur.fetchone()[0]
        cur.execute(
            "INSERT OR IGNORE INTO file_tags(file_id, tag_id) VALUES(?, ?)", (file_id, tag_id))
    conn.commit()
    print(f"Added tags {tags} to {file_path}")
    conn.close()


def remove(file_path, tags):
    conn = init_db()
    cur = conn.cursor()
    # TODO: modify to REMOVE tag from file_path
    # Insert file
    cur.execute("INSERT OR IGNORE INTO files(path) VALUES(?)", (file_path,))
    conn.commit()
    cur.execute("SELECT id FROM files WHERE path=?", (file_path,))
    file_id = cur.fetchone()[0]
    # Insert tags
    for tag in tags:
        cur.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
        conn.commit()
        cur.execute("SELECT id FROM tags WHERE name=?", (tag,))
        tag_id = cur.fetchone()[0]
        cur.execute(
            "INSERT OR IGNORE INTO file_tags(file_id, tag_id) VALUES(?, ?)", (file_id, tag_id))
    conn.commit()
    print(f"Added tags {tags} to {file_path}")
    conn.close()


def list_tags(file_path):
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM files WHERE path=?", (file_path,))
    row = cur.fetchone()
    if not row:
        print("No tags for file.")
        return
    file_id = row[0]
    cur.execute(
        "SELECT name FROM tags JOIN file_tags ON tags.id=file_tags.tag_id WHERE file_id=?", (file_id,))
    tags = [t[0] for t in cur.fetchall()]
    print(f"{file_path}: {', '.join(tags) if tags else 'No tags'}")
    conn.close()


def search(tag):
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM tags WHERE name=?", (tag,))
    row = cur.fetchone()
    if not row:
        print("No files with this tag.")
        return
    tag_id = row[0]
    cur.execute(
        "SELECT path FROM files JOIN file_tags ON files.id=file_tags.file_id WHERE tag_id=?", (tag_id,))
    files = [f[0] for f in cur.fetchall()]
    print(f"Files tagged '{tag}':")
    for f in files:
        print(" -", f)
    conn.close()


def all_tags():
    conn = init_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT name, COUNT(file_tags.file_id) FROM tags LEFT JOIN file_tags ON tags.id=file_tags.tag_id GROUP BY tags.id")
    rows = cur.fetchall()
    print("=== Tags ===")
    for name, count in rows:
        print(f"{name} ({count} files)")
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./tagger.py [add|list|search|tags] ...")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "add":
        if len(sys.argv) < 4:
            print("Usage: ./tagger.py add <file_path> <tag1> [tag2...]")
        else:
            add(sys.argv[2], sys.argv[3:])
    if cmd == "rm":
        if len(sys.argv) < 4:
            print("Usage: ./tagger.py rm <file_path> <tag1> [tag2...]")
        else:
            remove(sys.argv[2], sys.argv[3:])
    if cmd == "rename":
        if len(sys.argv) < 4:
            print("Usage: ./tagger.py rename <tag_old_name> <tag_new_name>")
        else:
            # remove(sys.argv[2], sys.argv[3:])
            # TODO: to be implemented
            print("To be implemented!")
    elif cmd == "list":
        if len(sys.argv) < 3:
            print("Usage: ./tagger.py list <file_path>")
        else:
            list_tags(sys.argv[2])
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: ./tagger.py search <tag>")
        else:
            search(sys.argv[2])
    elif cmd == "tags":
        all_tags()
    else:
        print("Unknown command:", cmd)
