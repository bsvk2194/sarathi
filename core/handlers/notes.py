import sqlite3

from flask import jsonify

from core.config import DATABASE
from core.backup import create_backup

# search notes handler
def handle_search_notes(keyword):

    keyword = keyword.strip()

    if keyword == "":

        return jsonify({
            "reply":
            "Please tell me what to search for."
        })

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT content
        FROM notes
        WHERE LOWER(content) LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{keyword.lower()}%",)
    )

    notes = cursor.fetchall()

    conn.close()

    if not notes:

        return jsonify({
            "reply":
            f"No notes found containing '{keyword}'."
        })

    notes_list = ""

    for i, note in enumerate(notes, start=1):

        notes_list += (
            f"{i}. {note[0]}\n\n"
        )

    return jsonify({
        "reply":
        f"""Found {len(notes)} matching note(s).
        {notes_list}
        """
    })

# add note handler
def handle_add_note(note_text):

    note_text = note_text.strip()

    if note_text == "":

        return jsonify({
            "reply": "Please provide a note."
        })

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notes (content)
        VALUES (?)
        """,
        (note_text,)
    )

    conn.commit()

    create_backup()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM notes
        """
    )

    total_notes = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "reply":
        f"""Note saved successfully.

Note:
{note_text}

Total notes: {total_notes}
"""
    })