/* What is the average rating of all movies? */
SELECT AVG(rating)
FROM REVIEW;

/* What are the names of all directors over 50 years old? */
SELECT given_name
FROM DIRECTOR
WHERE (strftime('%s', 'now') - DoB) / 31540000 > 50;

/* What are the emails of all directors? */
SELECT U.email
FROM USER U, DIRECTOR D
WHERE U.UID = D.UID;

/* What are the names of all movies that made a director famous? */
SELECT MOVIE.title
FROM MOVIE, DIRECTOR
WHERE MID = famous_for_MID;

/* What are the names of all actors who share a birthdate with another actor? */
SELECT A.given_name
FROM ACTOR A, ACTOR B
WHERE A.DoB = B.DoB
      AND NOT A.UID = B.UID;

/* What are the names of all movies with at least one rating above 2 except those created after 1990? */
SELECT DISTINCT M.title
FROM MOVIE M, REVIEW R
WHERE M.MID = R.MID
      AND R.rating > 2
EXCEPT
SELECT M.title
FROM MOVIE M
WHERE M.release_date > strftime('%s', '1990-01-01');

/* What are the names of all actors and directors older than 50? */
SELECT given_name
FROM DIRECTOR
WHERE (strftime('%s', 'now') - DoB) / 31540000 > 50
UNION
SELECT given_name
FROM ACTOR
WHERE (strftime('%s', 'now') - DoB) / 31540000 > 50;

/* How many movies did each director direct? */
SELECT
  DIRECTOR.given_name,
  COUNT(DIRECTOR.given_name)
FROM DIRECTOR, MOVIE
WHERE MOVIE.director_UID = DIRECTOR.UID
GROUP BY DIRECTOR.given_name;

/* What is the average age of all directors? */
SELECT AVG((strftime('%s', 'now') - DoB) / 31540000)
FROM DIRECTOR;

/* What is the highest rating any movie has received? */
SELECT MAX(rating) AS max_rating
FROM review;
