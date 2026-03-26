CREATE TABLE offices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor INTEGER NOT NULL,
    room_number INTEGER NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    UNIQUE(floor, room_number)
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    salary REAL NOT NULL CHECK (salary > 0),
    office_id INTEGER NULL,
    FOREIGN KEY (office_id) REFERENCES offices(id) ON DELETE SET NULL
);
