
import sqlite3

MAX_DURATION = 180
TEMP_LIMIT = 28.0


def validate_booking(duration):
    if duration <= 0 or duration > MAX_DURATION:
        raise ValueError("Invalid booking duration")
    return True


def sensor_alert(value):
    return value > TEMP_LIMIT


def approve_booking(role):
    if role not in ["Administrator", "Department Approver"]:
        raise PermissionError("Approval not allowed")
    return "Approved"


def validate_ticket(title):
    if not title or not title.strip():
        raise ValueError("Ticket title is required")
    return True


def valid_transition(old, new):
    transitions = {
        "New": "Assigned",
        "Assigned": "In Progress",
        "In Progress": "Resolved",
        "Resolved": "Closed"
    }
    return transitions.get(old) == new


def connect(db):
    con = sqlite3.connect(db)

    con.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY,
            room TEXT,
            start INTEGER,
            end INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS sensors(
            event_id TEXT UNIQUE,
            temperature REAL
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS tickets(
            id INTEGER PRIMARY KEY,
            title TEXT,
            status TEXT
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS audit(
            action TEXT
        )
    """)

    return con


def add_booking(con, room, start, end):
    duration = end - start
    validate_booking(duration)

    overlap = con.execute(
        """SELECT id FROM bookings
        WHERE room=? AND start < ? AND end > ?""",
        (room, end, start)
    ).fetchone()

    if overlap:
        raise ValueError("Booking overlap")

    con.execute(
        "INSERT INTO bookings(room,start,end) VALUES(?,?,?)",
        (room, start, end)
    )
    con.commit()


def add_sensor(con, event_id, value):
    con.execute(
        "INSERT OR IGNORE INTO sensors VALUES(?,?)",
        (event_id, value)
    )
    con.commit()


def add_ticket(con, title):
    validate_ticket(title)

    con.execute(
        "INSERT INTO tickets(title,status) VALUES(?,?)",
        (title, "New")
    )
    con.commit()


def change_ticket(con, ticket_id, new_status):
    row = con.execute(
        "SELECT status FROM tickets WHERE id=?",
        (ticket_id,)
    ).fetchone()

    if not row:
        raise ValueError("Ticket not found")

    if not valid_transition(row[0], new_status):
        raise ValueError("Invalid ticket transition")

    con.execute(
        "UPDATE tickets SET status=? WHERE id=?",
        (new_status, ticket_id)
    )

    con.execute(
        "INSERT INTO audit VALUES(?)",
        (new_status,)
    )

    con.commit()
