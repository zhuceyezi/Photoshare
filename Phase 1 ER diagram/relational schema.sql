CREATE DATABASE IF NOT exists PA1;
use PA1;
-- DROP TABLE IF EXISTS user_create_comment CASCADE;
-- DROP TABLE IF EXISTS user_like_Photo CASCADE;
-- DROP TABLE IF EXISTS be_friend CASCADE;
-- DROP TABLE IF EXISTS associate CASCADE;
-- DROP TABLE IF EXISTS Tags CASCADE;
-- DROP TABLE IF EXISTS Comments CASCADE;
-- DROP TABLE IF EXISTS Photos CASCADE;
-- DROP TABLE IF EXISTS Albums CASCADE;
-- DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users ( -- capitalized entitys for notations
	user_id INT4 AUTO_INCREMENT,
	first_name VARCHAR(20),
	last_name VARCHAR(20),
    email VARCHAR(30) UNIQUE,
    dob DATE,
    hometown VARCHAR(20),
    gender VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE be_friend(
	user_id_from INT4, 
    user_id_to INT4,
    PRIMARY KEY (user_id_from, user_id_to),
    FOREIGN KEY (user_id_to) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id_from) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT diff_user 
        CHECK (user_id_from <> user_id_to)
);


CREATE TABLE Albums(
    album_id INT4 PRIMARY KEY AUTO_INCREMENT, 
	album_name VARCHAR(255),
    user_id INT4 NOT NULL, 
    date_created date,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Photos(
  photo_id INT4 AUTO_INCREMENT,
  user_id INT4 NOT NULL,
  album_id INT4 NOT NULL,
  imgdata LONGBLOB, -- store data in binary
  caption VARCHAR(255),
  INDEX uphoto_id_idx (user_id),
  CONSTRAINT photos_pk PRIMARY KEY (photo_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE Tags(
	word VARCHAR(25) PRIMARY KEY 
);

CREATE TABLE associate(
	photo_id INT4,
    word VARCHAR(25),
    PRIMARY KEY (photo_id, word),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE,
    FOREIGN KEY (word) REFERENCES Tags(word)
);


CREATE TABLE user_like_Photo(
	user_id INT4,
    photo_id INT4,
    PRIMARY KEY (user_id, photo_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE
);

CREATE TABLE Comments(
	comment_id INT4 PRIMARY KEY AUTO_INCREMENT,
    user_id INT4 NOT NULL,
    photo_id INT4 NOT NULL,
    content VARCHAR(255),
    date_comment date,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE
    -- addtional constraint: user cannot comment on own photo
    -- can't really implement in mysql
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Albums (album_name, user_id, date_created) VALUES ("test", 1, "2023-02-08");
INSERT INTO Tags (word) VALUES ("test_tag");
-- INSERT INTO Comments (user_id,photo_id,content,date_comment) VALUES (1,30,"Nice Finger!","2023-02-15");
-- INSERT INTO Comments (user_id,photo_id,content,date_comment) VALUES (2,30,"I Hate you","2023-02-15");
INSERT INTO Users (user_id,first_name, last_name) VALUES (-1, "Anonymous", "Visitor");
INSERT INTO be_friend (user_id_from,user_id_to) VALUES (2,1);
INSERT INTO be_friend (user_id_from,user_id_to) VALUES (3,1);
INSERT INTO be_friend (user_id_from,user_id_to) VALUES (3,2);

SELECT u.first_name, u.last_name, u.email, u.user_id, COUNT(*) FROM Comments c NATURAL JOIN Users u 
WHERE c.content = 'test' GROUP BY u.user_id ORDER BY COUNT(*) DESC;

ALTER TABLE Users ADD COLUMN dob DATE;

-- count photo contribution
WITH cp(cp,uid) AS (
SELECT COUNT(p.user_id), u.user_id FROM Photos p, Users u WHERE p.user_id = u.user_id GROUP BY u.user_id
),
-- count contribution 
cc(cc,uid) AS (
SELECT COUNT(c.user_id), u.user_id FROM Comments c, Users u WHERE c.user_id = u.user_id GROUP BY u.user_id
)
SELECT (IFNULL(cc.cc, 0)+IFNULL(cp.cp, 0)), cp.uid FROM cp RIGHT OUTER JOIN cc ON cc.uid = cp.uid
UNION
SELECT (IFNULL(cc.cc, 0)+IFNULL(cp.cp, 0)), cp.uid FROM cp LEFT OUTER JOIN cc ON cc.uid = cp.uid;

-- sql for u may also like: 
With f(user_id) as (SELECT u.user_id from be_friend b JOIN users u ON b.user_id_to = u.user_id WHERE b.user_id_from = 1)
(SELECT u.user_id, u.first_name,u.last_name,u.email from be_friend b JOIN users u ON b.user_id_to = u.user_id);

SELECT u.user_id, u.first_name, u.last_name, u.email from be_friend f JOIN users u ON f.user_id_to = u.user_id WHERE f.user_id_from = 1;

SELECT u.first_name, u.last_name, u.email FROM user_like_photo l NATURAL JOIN Users u Where photo_id = 1; -- -1 show status as visitor(not log in)


select * from Users;
select * from be_friend;





/* CREATE ASSERTION Comment-Constraint CHECK
(NOT EXISTS (SELECT * FROM Comments C, Photos P
WHERE C.photo_id = P.photo_id AND P.user_id = C.user_id)) */