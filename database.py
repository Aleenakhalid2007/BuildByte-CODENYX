import sqlite3

# Connect to database (creates it if it doesn't exist)
connection = sqlite3.connect("skillai.db")

cursor = connection.cursor()

# ==========================
# Create Users Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL,

    role TEXT NOT NULL

)
""")

# ==========================
# Create Profiles Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER UNIQUE NOT NULL,

    bio TEXT,

    skills TEXT,

    github TEXT,

    linkedin TEXT,

    project_name TEXT,

    project_description TEXT,

    FOREIGN KEY(user_id) REFERENCES users(id)

)
""")

# Save changes
connection.commit()

# Close connection
connection.close()

print("Database Created Successfully!")