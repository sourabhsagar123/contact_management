"""
Database Module for Contact Management System
============================================
Uses SQLite (standard Python library, zero-configuration, lightweight).
Provides persistent storage so that in-memory ADSA data structures can be loaded on boot
and mutations (Insert, Update, Delete) are saved permanently.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection with Row factory for dict-like access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Contacts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        email TEXT,
        category TEXT DEFAULT 'General',
        company TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        is_favorite INTEGER DEFAULT 0,
        call_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Contact relationships table for Graph ADSA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id INTEGER NOT NULL,
        to_id INTEGER NOT NULL,
        relationship TEXT NOT NULL,
        FOREIGN KEY (from_id) REFERENCES contacts(id) ON DELETE CASCADE,
        FOREIGN KEY (to_id) REFERENCES contacts(id) ON DELETE CASCADE,
        UNIQUE(from_id, to_id)
    );
    """)

    conn.commit()
    conn.close()


def fetch_all_contacts() -> List[Dict[str, Any]]:
    """Fetches all contacts as list of dictionaries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts ORDER BY id ASC")
    rows = cursor.fetchall()
    contacts = [dict(row) for row in rows]
    conn.close()
    return contacts


def fetch_contact_by_id(contact_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single contact by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def insert_contact_db(contact_data: Dict[str, Any]) -> int:
    """Inserts a contact and returns generated id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO contacts (name, phone, email, category, company, notes, is_favorite, call_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        contact_data.get("name", "").strip(),
        contact_data.get("phone", "").strip(),
        contact_data.get("email", "").strip(),
        contact_data.get("category", "General"),
        contact_data.get("company", ""),
        contact_data.get("notes", ""),
        1 if contact_data.get("is_favorite") else 0,
        contact_data.get("call_count", 0)
    ))
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return contact_id


def update_contact_db(contact_id: int, contact_data: Dict[str, Any]) -> bool:
    """Updates an existing contact."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE contacts
    SET name = ?, phone = ?, email = ?, category = ?, company = ?, notes = ?, is_favorite = ?, call_count = ?
    WHERE id = ?
    """, (
        contact_data.get("name", "").strip(),
        contact_data.get("phone", "").strip(),
        contact_data.get("email", "").strip(),
        contact_data.get("category", "General"),
        contact_data.get("company", ""),
        contact_data.get("notes", ""),
        1 if contact_data.get("is_favorite") else 0,
        contact_data.get("call_count", 0),
        contact_id
    ))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_contact_db(contact_id: int) -> bool:
    """Deletes a contact and connected relationships."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contact_relationships WHERE from_id = ? OR to_id = ?", (contact_id, contact_id))
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def fetch_all_relationships() -> List[Dict[str, Any]]:
    """Fetches all stored relationship edges for Graph."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT from_id, to_id, relationship FROM contact_relationships")
    rows = cursor.fetchall()
    rels = [dict(row) for row in rows]
    conn.close()
    return rels


def insert_relationship_db(from_id: int, to_id: int, relationship: str) -> None:
    """Stores an edge in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO contact_relationships (from_id, to_id, relationship)
    VALUES (?, ?, ?)
    """, (from_id, to_id, relationship))
    conn.commit()
    conn.close()
