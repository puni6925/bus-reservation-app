import sqlite3

# Create and connect to bus.db
conn = sqlite3.connect('bus.db')
cursor = conn.cursor()

# Create buses table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS buses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bus_name TEXT,
        source TEXT,
        destination TEXT,
        seats INTEGER
    )
''')

# Create bookings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        bus_id INTEGER,
        FOREIGN KEY (bus_id) REFERENCES buses(id)
    )
''')

# Insert sample data into buses table
cursor.executemany('''
    INSERT INTO buses (bus_name, source, destination, seats) VALUES (?, ?, ?, ?)
''',  [
    ('Shatabdi Express', 'Mumbai', 'Pune', '09:00 AM'),
    ('Rajdhani Travels', 'Delhi', 'Jaipur', '02:00 PM'),
    ('Southern Line', 'Chennai', 'Bangalore', '06:00 PM'),
    ('Goa Deluxe', 'Hyderabad', 'Goa', '08:30 AM'),
    ('Eastbound Express', 'Kolkata', 'Patna', '05:15 PM')
]
)

conn.commit()
conn.close()

print("Database created and sample data inserted.")
