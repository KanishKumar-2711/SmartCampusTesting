
import pytest

from campus import (
    validate_booking,
    sensor_alert,
    approve_booking,
    validate_ticket,
    valid_transition,
    connect,
    add_booking,
    add_sensor,
    add_ticket,
    change_ticket
)


# UNIT TESTING (6 TESTS)

def test_valid_duration():
    assert validate_booking(120) == True


def test_invalid_duration():
    with pytest.raises(ValueError):
        validate_booking(181)


def test_sensor_boundary():
    assert sensor_alert(28.00) == False


def test_sensor_alert():
    assert sensor_alert(28.01) == True


def test_student_approval():
    with pytest.raises(PermissionError):
        approve_booking("Student")


def test_missing_ticket():
    with pytest.raises(ValueError):
        validate_ticket("")


# INTEGRATION TESTING (4 TESTS)

def test_booking_database():
    con = connect(":memory:")
    add_booking(con, "Lab1", 10, 12)

    result = con.execute(
        "SELECT * FROM bookings"
    ).fetchall()

    assert len(result) == 1
    con.close()


def test_duplicate_sensor():
    con = connect(":memory:")

    add_sensor(con, "E101", 29.0)
    add_sensor(con, "E101", 29.0)

    result = con.execute(
        "SELECT * FROM sensors"
    ).fetchall()

    assert len(result) == 1
    con.close()


def test_unauthorized_approval():
    con = connect(":memory:")
    add_booking(con, "Lab1", 10, 12)

    with pytest.raises(PermissionError):
        approve_booking("Student")

    result = con.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    assert result == 1
    con.close()


def test_ticket_database():
    con = connect(":memory:")
    add_ticket(con, "Water leakage")

    change_ticket(con, 1, "Assigned")

    result = con.execute(
        "SELECT status FROM tickets WHERE id=1"
    ).fetchone()

    assert result[0] == "Assigned"
    con.close()


# REGRESSION TESTING (4 TESTS)

def test_back_to_back_booking():
    con = connect(":memory:")

    add_booking(con, "Lab1", 10, 12)
    add_booking(con, "Lab1", 12, 14)

    count = con.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    assert count == 2
    con.close()


def test_invalid_ticket_transition():
    con = connect(":memory:")
    add_ticket(con, "Electrical issue")

    with pytest.raises(ValueError):
        change_ticket(con, 1, "Closed")

    con.close()


def test_repeated_sensor_event():
    con = connect(":memory:")

    for i in range(5):
        add_sensor(con, "E102", 30.0)

    count = con.execute(
        "SELECT COUNT(*) FROM sensors"
    ).fetchone()[0]

    assert count == 1
    con.close()


def test_database_persistence(tmp_path):
    db = str(tmp_path / "test_campus.db")

    con = connect(db)
    add_booking(con, "Lab2", 20, 22)
    con.close()

    con = connect(db)

    count = con.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    assert count == 1
    con.close()
