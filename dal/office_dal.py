def create_office(conn, floor, room_number, capacity):
    cur = conn.execute(
        "INSERT INTO offices (floor, room_number, capacity) VALUES (?, ?, ?)",
        (floor, room_number, capacity)
    )
    return cur.lastrowid

def get_office(conn, office_id):
    return conn.execute("SELECT * FROM offices WHERE id = ?", (office_id,)).fetchone()

def get_all_offices(conn):
    return conn.execute("SELECT * FROM offices").fetchall()

def update_office(conn, office_id, floor, room_number, capacity):
    cur = conn.execute(
        "UPDATE offices SET floor = ?, room_number = ?, capacity = ? WHERE id = ?",
        (floor, room_number, capacity, office_id)
    )
    return cur.rowcount

def delete_office(conn, office_id):
    cur = conn.execute("DELETE FROM offices WHERE id = ?", (office_id,))
    return cur.rowcount
