import sqlite3

conn = sqlite3.connect('bus.db')
cursor = conn.cursor()

# Add profile_pic column if it doesn't exist
cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
conn.commit()
conn.close()

print("✅ users table updated with profile_pic column.")
