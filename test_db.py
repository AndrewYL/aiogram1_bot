import sqlite3

cur = sqlite3.connect('db/user_db.db')

con = cur.cursor()
result = con.execute("""SELECT * FROM users
            WHERE user_id = 1""").fetchall()
for elem in result:
    print(elem)

con.close()