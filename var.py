import sqlite3


con = sqlite3.connect('db/oge.db')
cur = con.cursor()
result = cur.execute("""SELECT task, answer FROM hist
            WHERE id IN (SELECT id FROM hist ORDER BY RANDOM() LIMIT 5)""").fetchall()
for elem in result:
    print(elem[1])
    print(elem[2])
    print(elem[5])
    print(elem[7])
    print(elem[9])