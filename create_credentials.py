import sqlite3
import hashlib

# Database file
DB_FILE = "users.db"

# Connect to the database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (cl
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Predefined credentials
users = [
    ("customer1", "customer_pass", "customer"),
    ("supplier1", "supplier_pass", "supplier"),
]

# Insert users
for username, password, role in users:
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, hashed_password, role))
        print(f"User {username} added successfully!")
    except sqlite3.IntegrityError:
        print(f"User {username} already exists.")

# Commit changes and close connection
conn.commit()
conn.close()
