/*
 * Note: SQLite has only the following data "affinities"
 * 	 -NULL
 *	 -INTEGER
 *	 -REAL
 *	 -TEXT
 *	 -BLOB
 * For this reason, all "dates" will be stored as integers using
 * the unix epoch standard (i.e., seconds from epoch).
 *
 * To convert from a date to the unix standard, use the SQLite
 * function strftime('%s', '2017-05-35') where the second
 * parameter is the date to be converted. For the current time,
 * use strftime('%s', 'now')
 */

CREATE TABLE USER (
  UID          INTEGER PRIMARY KEY,
  u_name       TEXT    NOT NULL,
  email        TEXT    NOT NULL,
  created_date INTEGER NOT NULL,
  CONSTRAINT unique_uname UNIQUE (u_name),
  CONSTRAINT unique_email UNIQUE (email)
);

CREATE TABLE ADMIN (
  UID      INTEGER PRIMARY KEY,
  position TEXT NOT NULL,
  FOREIGN KEY (UID) REFERENCES USER (UID)
);

CREATE TABLE DIRECTOR (
  UID            INTEGER PRIMARY KEY,
  famous_for_MID INTEGER,
  given_name     TEXT    NOT NULL,
  DoB            INTEGER,
  FOREIGN KEY (UID) REFERENCES USER (UID)
);

CREATE TABLE ACTOR (
  UID        INTEGER PRIMARY KEY,
  stage_name TEXT,
  given_name TEXT    NOT NULL,
  DoB        INTEGER,
  FOREIGN KEY (UID) REFERENCES USER (UID)
);

CREATE TABLE MOVIE (
  MID          INTEGER PRIMARY KEY,
  director_UID INTEGER,
  title        TEXT    NOT NULL,
  release_date INTEGER,
  entered_by   INTEGER NOT NULL,
  entered_date INTEGER NOT NULL,
  FOREIGN KEY (director_UID) REFERENCES DIRECTOR (UID),
  FOREIGN KEY (entered_by) REFERENCES ADMIN (UID)
);

CREATE TABLE REVIEW (
  MID          INTEGER NOT NULL,
  UID          INTEGER NOT NULL,
  text         TEXT    NOT NULL,
  rating       INTEGER NOT NULL,
  created_date INTEGER NOT NULL,
  PRIMARY KEY (MID, UID),
  FOREIGN KEY (MID) REFERENCES MOVIE (MID),
  FOREIGN KEY (UID) REFERENCES USER (UID)
);

CREATE TABLE ACTED_IN (
  MID            INTEGER NOT NULL,
  UID            INTEGER NOT NULL,
  character_role TEXT    NOT NULL,
  PRIMARY KEY (MID, UID),
  FOREIGN KEY (MID) REFERENCES MOVIE (MID),
  FOREIGN KEY (UID) REFERENCES USER (UID)
);

CREATE TABLE POSTER (
  MID INTEGER NOT NULL,
  img TEXT    NOT NULL,
  UID INTEGER NOT NULL,
  PRIMARY KEY (MID),
  FOREIGN KEY (MID) REFERENCES MOVIE (MID),
  FOREIGN KEY (UID) REFERENCES ADMIN (UID)
);

CREATE TABLE PASSWORD (
  UID       INTEGER NOT NULL,
  pass_hash TEXT    NOT NULL,
  PRIMARY KEY (UID),
  FOREIGN KEY (UID) REFERENCES USER (UID)
);
