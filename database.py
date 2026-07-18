import sqlite3

# Connect to database
connection = sqlite3.connect("skillai.db")
cursor = connection.cursor()

# ==========================
# Users Table
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
# Profiles Table
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

# ==========================
# Assessment Results Table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS assessments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    skill TEXT NOT NULL,

    score INTEGER NOT NULL,

    badge TEXT,

    verification_status TEXT,

    completed INTEGER DEFAULT 1,

    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)

)
""")

connection.commit()
connection.close()

print("Database Created Successfully!")