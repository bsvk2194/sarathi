import sqlite3
import dateparser

from flask import jsonify

from core.config import DATABASE
from core.backup import create_backup

# upcoming events handler
def handle_upcoming_events():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, event_date
        FROM events
        ORDER BY event_date ASC
        LIMIT 5
        """
    )

    events = cursor.fetchall()

    conn.close()

    if not events:

        return jsonify({
            "reply": "No upcoming events found."
        })

    event_list = ""

    for i, event in enumerate(events, start=1):

        event_list += (
            f"{i}. {event[0]} ({event[1]})\n"
        )

    return jsonify({
        "reply":
        f"Upcoming Events:\n\n{event_list}"
    })

# add event handler
def handle_add_event(title, event_date):

    title = title.strip()
    event_date = event_date.strip()

    #print("Title:", title)
    #print("Date:", event_date)

    if event_date.lower().startswith("next "):
        event_date = event_date[5:]

    parsed_date = dateparser.parse(
        event_date,
        settings={
            "PREFER_DATES_FROM": "future"
        }
    )

    #print("Parsed:", parsed_date)

    if not parsed_date:

        return jsonify({
            "reply":
            "I couldn't understand the date."
        })

    event_date = parsed_date.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO events
        (title, event_date)
        VALUES (?, ?)
        """,
        (
            title,
            event_date
        )
    )

    conn.commit()

    create_backup()

    conn.close()

    return jsonify({
        "reply":
        f"""Event added successfully.

Title:
{title}

Date:
{event_date}
"""
    })