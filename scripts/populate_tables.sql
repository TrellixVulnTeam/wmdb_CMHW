/* Create admins (i.e., us) */
INSERT INTO USER VALUES (0, 'eichenhofer', 'eichenhofer@wisc.edu', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (0, 'creator');
INSERT INTO USER VALUES (1, 'yhuang276', 'yhuang276@wisc.edu', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (1, 'creator');
INSERT INTO USER VALUES (2, 'kazaniwskyj', 'kazaniwskyj@wisc.edu', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (2, 'creator');

/* add first movie (shawshank redemption) */
/* director first: */
INSERT INTO USER VALUES (3, 'darabont', 'darabont@darabont.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (3, NULL, 'Frank Darabont', strftime('%s', '1959-01-28'));
/* then movie */
INSERT INTO MOVIE VALUES (0, 3, 'The Shawshank Redemption', strftime('%s', '1994-10-14'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (4, 'robbins', 'robins_t@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (4, 'Tim Robbins', 'Timothy Francis Robbins', strftime('%s', '1958-10-16'));
INSERT INTO ACTED_IN VALUES (0, 4, 'Andy Dufresne');
/* now actor 2 */
INSERT INTO USER VALUES (5, 'mfreeman', 'mfreeman@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (5, 'Morgan Freeman', 'Morgan Freeman Jr.', strftime('%s', '1937-06-01'));
INSERT INTO ACTED_IN VALUES (0, 5, 'Ellis Boyd ''Red'' Redding');
/* this movie made him famous: */
UPDATE DIRECTOR
SET famous_for_MID = 0
WHERE UID = 3;

/* add second movie */
/* director first: */
INSERT INTO USER VALUES (6, 'coppola', 'coppola@ymdb.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (6, NULL, 'Francis Ford Coppola', strftime('%s', '1939-04-07'));
/* then movie */
INSERT INTO MOVIE VALUES (1, 6, 'The Godfather', strftime('%s', '1972-03-24'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (7, 'brando', 'brando@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (7, 'Marlon Brando', 'Marlon Brando Jr.', strftime('%s', '1924-04-03'));
INSERT INTO ACTED_IN VALUES (1, 7, 'Don Vito Corleone');

/* add third movie */
/* same director as last movie */
/* then movie */
INSERT INTO MOVIE VALUES (2, 6, 'The Godfather', strftime('%s', '1974-12-20'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (8, 'pacino', 'pacino@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (8, 'Al Pacino', 'Alfredo James Pacino', strftime('%s', '1940-04-25'));
INSERT INTO ACTED_IN VALUES (2, 8, 'Michael');

/* add fourth movie */
/* director first: */
INSERT INTO USER VALUES (9, 'fincher', 'fincher@ymdb.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (9, NULL, 'David Fincher', strftime('%s', '1962-08-28'));
/* then movie */
INSERT INTO MOVIE VALUES (3, 9, 'Fight Club', strftime('%s', '1999-10-15'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (10, 'norton', 'norton@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (10, 'Edward Norton', 'Edward Harrison Norton', strftime('%s', '1969-08-18'));
INSERT INTO ACTED_IN VALUES (3, 10, 'The Narrator');

/* add fifth movie */
/* director first: */
INSERT INTO USER VALUES (11, 'tarantino', 'tarantino@gmail.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (11, NULL, 'Quentin Tarantino', strftime('%s', '1963-03-27'));
/* then movie */
INSERT INTO MOVIE VALUES (4, 11, 'Pulp Fiction', strftime('%s', '1994-10-14'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (12, 'roth', 'roth@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (12, 'Tim Roth', 'Timothy Simon Roth', strftime('%s', '1961-05-14'));
INSERT INTO ACTED_IN VALUES (4, 12, 'Pumpkin');

/* add sixth movie */
/* director first: */
INSERT INTO USER VALUES (13, 'jackson', 'jackson@gmail.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (13, NULL, 'Peter Jackson', strftime('%s', '1961-10-31'));
/* then movie */
INSERT INTO MOVIE
VALUES (5, 13, 'The Lord of the Rings: The Return of the King', strftime('%s', '2003-12-17'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (14, 'bloom', 'bloom@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (14, 'Orlando Bloom', 'Orlando Jonathan Blanchard Bloom', strftime('%s', '1977-01-13'));
INSERT INTO ACTED_IN VALUES (5, 14, 'Pumpkin');

/* add seventh movie */
/* director first */
INSERT INTO USER VALUES (15, 'leone', 'leone@gmail.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (15, NULL, 'Sergio Leone', strftime('%s', '1929-01-03'));
/* then movie */
INSERT INTO MOVIE
VALUES (6, 15, 'The Good, the Bad and the Ugly ', strftime('%s', '1967-12-29'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (16, 'eastwood', 'eastwood@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (16, 'Clint Eastwood', 'Clint Eastwood Jr.', strftime('%s', '1930-05-31'));
INSERT INTO ACTED_IN VALUES (6, 16, 'Blondie');

/* add eighth movie */
/* director first */
INSERT INTO USER VALUES (17, 'christopher', 'christopher@gmail.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (17, NULL, 'Christopher Nolan', strftime('%s', '1970-07-30'));
/* then movie */
INSERT INTO MOVIE VALUES (7, 17, 'The Dark Knight', strftime('%s', '2008-07-18'), 1, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (18, 'christian', 'christian@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (18, 'Christian Bale', 'Christian Charles Philip Bale', strftime('%s', '1974-01-30'));
INSERT INTO ACTED_IN VALUES (7, 18, 'Bruce Wayne');
/* now actor 2 */
INSERT INTO USER VALUES (19, 'heath', 'heath@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (19, 'Heath Ledger', 'Heathcliff Andrew Ledger', strftime('%s', '1979-04-04'));
INSERT INTO ACTED_IN VALUES (7, 19, 'The Joker');
/* now actor 3 */
INSERT INTO USER VALUES (20, 'eckhart', 'eckhart@gmail.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (20, 'Aaron Eckhart', 'Aaron Edward Eckhart', strftime('%s', '1968-03-12'));
INSERT INTO ACTED_IN VALUES (7, 20, 'Harvey Dent');

/* add ninth movie */
/* director first: */
INSERT INTO USER VALUES (21, 'lumet', 'lumet@ymdb.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (21, NULL, 'Sidney Lumet', strftime('%s', '1924-01-25'));
/* then movie */
INSERT INTO MOVIE VALUES (8, 21, '12 Angry Men', strftime('%s', '1957-04-01'), 1, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (22, 'martin', 'martin@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (22, 'Martin Balsam', 'Martin Henry Balsam', strftime('%s', '1919-11-04'));
INSERT INTO ACTED_IN VALUES (8, 22, 'Juror 1');
/* now actor 2 */
INSERT INTO USER VALUES (23, 'john', 'john@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (23, 'John Fiedler', 'John Donald Fiedler', strftime('%s', '1925-02-03'));
INSERT INTO ACTED_IN VALUES (8, 23, 'Juror 2');
/* now actor 3 */
INSERT INTO USER VALUES (24, 'cobb', 'cobb@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (24, 'Lee J. Cobb', 'Leo Jacoby', strftime('%s', '1979-02-11'));
INSERT INTO ACTED_IN VALUES (8, 24, 'Juror 3');

/* add tenth movie */
/* director first: */
INSERT INTO USER VALUES (25, 'spielberg', 'spielberg@ymdb.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (25, NULL, 'Steven Spielberg', strftime('%s', '1946-12-18'));
/* then movie */
INSERT INTO MOVIE VALUES (9, 25, 'Schindler''s List', strftime('%s', '1994-02-04'), 1, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (26, 'neeson', 'neeson@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (26, 'Liam Neeson', 'Liam John Neeson', strftime('%s', '1952-06-07'));
INSERT INTO ACTED_IN VALUES (9, 26, 'Oskar Schindler');
/* now actor 2 */
INSERT INTO USER VALUES (27, 'kingsley', 'kingsley@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (27, 'Ben Kingsley', 'Krishna Pandit Bhanji', strftime('%s', '1941-12-31'));
INSERT INTO ACTED_IN VALUES (9, 27, 'Itzhak Stern');
/* now actor 3 */
INSERT INTO USER VALUES (28, 'fiennes', 'fiennes@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR
VALUES (28, 'Ralph Fiennes', 'Ralph Nathaniel Twisleton-Wykeham-Fiennes', strftime('%s', '1962-12-22'));
INSERT INTO ACTED_IN VALUES (9, 28, 'Amon Goeth');

/* add eleventh movie */
/* director first: */
INSERT INTO USER VALUES (29, 'zemeckis', 'zemeckis@ymdb.com', strftime('%s', 'now'));
INSERT INTO DIRECTOR VALUES (29, NULL, 'Robert Zemeckis', strftime('%s', '1952-05-14'));
/* then movie */
INSERT INTO MOVIE VALUES (10, 29, 'Forrest Gump', strftime('%s', '1994-07-06'), 0, strftime('%s', 'now'));
/* now actor 1 */
INSERT INTO USER VALUES (30, 'thanks', 'thanks@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (30, 'Tom Hanks', 'Thomas Jeffrey Hanks', strftime('%s', '1956-07-09'));
INSERT INTO ACTED_IN VALUES (9, 30, 'Forrest Gump');
/* now a fake actor with the same birthdate as tom hanks */
INSERT INTO USER VALUES (38, 'thanks2', 'thanks2@ymdb.com', strftime('%s', 'now'));
INSERT INTO ACTOR VALUES (38, 'Hom Thanks', 'Homas Jeffrey Thanks', strftime('%s', '1956-07-09'));
INSERT INTO ACTED_IN VALUES (9, 38, 'Forrest Gump');


/* add more admins */
INSERT INTO USER VALUES (31, 'data_enterer1', 'data1@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (31, 'data entry');
INSERT INTO USER VALUES (32, 'data_enterer2', 'data2@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (32, 'data entry');
INSERT INTO USER VALUES (33, 'data_enterer3', 'data3@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (33, 'data entry');
INSERT INTO USER VALUES (34, 'data_enterer4', 'data4@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (34, 'data entry');
INSERT INTO USER VALUES (35, 'supervisor1', 'super1@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (35, 'supervisor');
INSERT INTO USER VALUES (36, 'supervisor2', 'super2@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (36, 'supervisor');
INSERT INTO USER VALUES (37, 'supervisor3', 'super3@ymdb.com', strftime('%s', 'now'));
INSERT INTO ADMIN VALUES (37, 'supervisor');

/* add some random reviews */
INSERT INTO REVIEW VALUES (0, 0, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (0, 1, 'awesome', 5, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (1, 0, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (1, 1, 'liked it, but didn''t love it', 3, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (2, 0, 'ok', 2, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (2, 1, 'terrible', 1, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (3, 0, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (3, 1, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (4, 0, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (4, 33, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (5, 34, 'pretty good', 5, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (5, 35, 'pretty good', 3, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (6, 31, 'pretty good', 2, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (6, 32, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (7, 2, 'pretty good', 4, strftime('%s', 'now'));
INSERT INTO REVIEW VALUES (7, 3, 'pretty good', 4, strftime('%s', 'now'));
