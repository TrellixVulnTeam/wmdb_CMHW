from db_connection import db_connection

curs = db_connection.cursor()
movie_rows = curs.execute('SELECT MID, director_UID FROM MOVIE ORDER BY MID DESC').fetchall()

for row in movie_rows:
    if row[1] is not None:
        curs.execute('UPDATE DIRECTOR SET famous_for_MID = ? WHERE UID = ?', (row[0], row[1]))
        db_connection.commit()
