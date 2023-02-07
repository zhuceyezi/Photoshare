CREATE DATABASE IF NOT exists PA1;
use PA1;
DROP TABLE IF EXISTS user_create_comment CASCADE;
DROP TABLE IF EXISTS comments_comment_on_picture CASCADE;
DROP TABLE IF EXISTS album_contain_picture CASCADE;
DROP TABLE IF EXISTS user_like_picture CASCADE;
DROP TABLE IF EXISTS be_friend CASCADE;
DROP TABLE IF EXISTS create_album CASCADE;
DROP TABLE IF EXISTS associate CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;



CREATE TABLE Users ( -- capitalized entitys for notations
	user_id INT4 AUTO_INCREMENT,
	first_name VARCHAR(20),
	last_name VARCHAR(20),
    email VARCHAR(30) UNIQUE,
    job VARCHAR(10),
    hometown VARCHAR(20),
    gender VARCHAR(20),
    password VARCHAR(255),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE be_friend(
	user_id_from INT4, 
    user_id_to INT4,
    PRIMARY KEY (user_id_from, user_id_to),
    FOREIGN KEY (user_id_to) REFERENCES Users(user_id),
	FOREIGN KEY (user_id_from) REFERENCES Users(user_id)
);
 -- ALTER TABLE be_friend ADD INDEX(user_id1);
 -- ALTER TABLE be_friend CHANGE user_id1 user_id1 INT4 AUTO_INCREMENT;

CREATE TABLE Albums(
	album_id INT4 PRIMARY KEY AUTO_INCREMENT, 
	album_name VARCHAR(255),
  user_id INT4 NOT NULL, 
  date_created date
);


CREATE TABLE Pictures(
	picture_id INT4 AUTO_INCREMENT,
  user_id INT4 NOT NULL,
  album_id INT4 NOT NULL,
  imgdata LONGBLOB, -- store data in binary
  caption VARCHAR(255),
  INDEX upicture_id_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Tags(
	word VARCHAR(25) PRIMARY KEY 
);

CREATE TABLE associate(
	picture_id INT4,
    word VARCHAR(25),
    PRIMARY KEY (picture_id, word),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
    FOREIGN KEY (word) REFERENCES Tags(word)
);


CREATE TABLE user_like_picture(
	user_id INT4,
    picture_id INT4,
    PRIMARY KEY (user_id, picture_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Comments(
	comment_id INT4 PRIMARY KEY AUTO_INCREMENT,
    content VARCHAR(255),
    owner_id INT4 NOT NULL,
    date_comment date
);



INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
    
    

    
