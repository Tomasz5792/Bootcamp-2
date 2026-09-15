import sqlite3

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE users (name TEXT, age INTEGER)')
cursor.execute("INSERT INTO users VALUES ('Tobias', 28)")
conn.commit()

cursor.execute('SELECT * FROM users')
result = cursor.fetchone()
print(f'User: {result[0]}, Age: {result[1]}')