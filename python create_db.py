import sqlite3

conn = sqlite3.connect('bus.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS buses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_name TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    time TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bus_id INTEGER NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES buses(id)
)
''')

sample_buses = [
    ('Express Line', 'City A', 'City B', '10:00 AM'),
    ('Green Travels', 'City B', 'City C', '02:00 PM'),
    ('Red Travels', 'City A', 'City C', '06:00 PM')
]

cursor.executemany('''
INSERT INTO buses (bus_name, source, destination, time)
VALUES (?, ?, ?, ?)
''', sample_buses)

conn.commit()
conn.close()
print("Database created with sample data.")
