import ssl
import urllib.request, urllib.parse, urllib.error
import json
import sqlite3
import secrets

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect("movies.sqlite")
cur = conn.cursor()

conn_1 = sqlite3.connect("movies_ranking.sqlite")
cur_1 = conn_1.cursor()

cur_1.execute('''CREATE TABLE IF NOT EXISTS movies_rank (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
title TEXT UNIQUE,
genre TEXT,
rating REAL
)''')



def api_call(movie_name):
    endpoint = "http://www.omdbapi.com/?"
    params = urllib.parse.urlencode({ "t" : movie_name, "apikey" : secrets.api_key_2 })
    url = endpoint + params
    try:
        with urllib.request.urlopen(url, context=ctx) as url_obj:
            content = url_obj.read().decode()
            json_py_obj = json.loads(content)

            ratings = json_py_obj["Ratings"]
            for i in range(len(ratings)):
                if i == 0:
                    imdb = ratings[0]["Value"]
                if i == 1:
                    rotten_tomatoes = ratings[1]["Value"]
                if i == 2:
                    metacritic = ratings[2]["Value"]
            try:
                i_rating = float(imdb[ : 3])
            except:
                i_rating = None
            try:
                r_rating = float(rotten_tomatoes[ : 2])/10
            except:
                r_rating = None
            try:
                m_rating = eval(metacritic) * 10
            except:
                m_rating = None

            rating_list = [i_rating, r_rating, m_rating]
            final = list()
            for rating in rating_list:
                if rating is None:
                    continue
                final.append(rating)

            movie_rating = sum(final)/len(final)

            yield movie_rating

            movie_title = json_py_obj["Title"]
            yield  movie_title

            movie_genre = json_py_obj["Genre"]
            yield movie_genre
    except:
        return None


cur.execute('''SELECT movie_id, title FROM movies WHERE selection is NULL ORDER BY RANDOM()''')
rows = cur.fetchall()

total_items_done = 0
count = 0
while True:
    num = input("Enter the no. of movies(greater than 10): ")
    if len(num) == 0:
        break
    num_items = int(num)
    total_items_done += num_items
    if count == 0:
        start_pos = 0
    else:
        start_pos = end_pos
    end_pos = total_items_done
    for item in rows[ start_pos : end_pos]:
        try:
            movie_title = item[1]
            movie_id = item[0]

            gen_obj = api_call(movie_title)
            if gen_obj is None:
                continue
            try:
                rating = next(gen_obj)
            except:
                continue
            title = next(gen_obj)
            genre = next(gen_obj)

            print("Title: ", title)
            print("Genre: ", genre)
            print("Rating: ", rating)


            cur_1.execute('''INSERT OR IGNORE INTO movies_rank (title, genre, rating) VALUES(?, ?, ?)''',(title, genre, rating))
            cur.execute('''UPDATE movies SET selection = ? WHERE movie_id = ?''',(1, movie_id))
            count += 1
            if count % 10 == 0:
                conn_1.commit()
                conn.commit()
            print(count)
            print("===========================================================")
        except KeyboardInterrupt:
            break

conn.commit()
conn_1.commit()