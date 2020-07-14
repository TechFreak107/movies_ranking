import sqlite3
import os

conn = sqlite3.connect("movies.sqlite")
cur = conn.cursor()

try:
    os.remove("movies.sqlite-journal")
except:
    pass

try:
    os.remove("movies_ranking.sqlite-journal")
except:
    pass

cur.execute('''UPDATE movies SET selection = NUll''')
conn.commit()

conn_1 = sqlite3.connect("movies_ranking.sqlite")
cur_1 = conn_1.cursor()
try:
    cur_1.execute('''DELETE FROM movies_rank''')
    conn_1.commit()
except:
    pass

