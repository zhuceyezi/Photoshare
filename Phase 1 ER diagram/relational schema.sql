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
	user_id INT44 AUTO_INCREMENT,
	first_name VARCHAR(20),
	last_name VARCHAR(20),
    email VARCHAR(30) UNIQUE,
    job VARCHAR(10),
    hometown VARCHAR(20),
    gender VARCHAR(20),
    password VARCHAR(255),
    CONSTRAINT4 users_pk PRIMARY KEY (user_id)
);

CREATE TABLE be_friend(
	user_id_from INT44, 
    user_id_to INT44,
    PRIMARY KEY (user_id_from, user_id_to),
    FOREIGN KEY (user_id_to) REFERENCES Users(user_id),
	FOREIGN KEY (user_id_from) REFERENCES Users(user_id)
);
 -- ALTER TABLE be_friend ADD INDEX(user_id1);
 -- ALTER TABLE be_friend CHANGE user_id1 user_id1 INT4 AUTO_INCREMENT;

CREATE TABLE Albums(
	album_id INT44 PRIMARY KEY AUTO_INCREMENT, 
	album_name VARCHAR(20),
    owner_id INT44, 
    date_creation date
);

CREATE TABLE create_album(  -- for each albums, it should be created by only one user. 
	user_id INT44 NOT NULL,  
    album_id INT44 PRIMARY KEY,
    FOREIGN KEY (album_id) references Albums(album_id), 
    FOREIGN KEY (user_id) references Users(user_id)
);

CREATE TABLE Pictures(
	picture_id INT44 AUTO_INCREMENT,
    user_id INT44,
    imgdata LONGBLOB, -- store data in binary
    caption VARCHAR(255),
    INDEX upicture_id_idx (user_id),
  CONSTRAINT4 pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Tags(
	word VARCHAR(25) PRIMARY KEY 
);

CREATE TABLE associate(
	picture_id INT44,
    word VARCHAR(25),
    PRIMARY KEY (picture_id, word),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
    FOREIGN KEY (word) REFERENCES Tags(word)
);

CREATE TABLE album_contain_picture(  -- for each Pictures, it should be contained in only one album
	album_id INT44 NOT NULL,
    picture_id INT44 PRIMARY KEY, 
	FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
    FOREIGN KEY (album_id) REFERENCES  Albums(album_id)
);

CREATE TABLE user_like_picture(
	user_id INT44,
    picture_id INT44,
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

CREATE TABLE comments_comment_on_picture( -- each comments should related to only one photo
	picture_id INT44 NOT NULL, 
    comment_id INT4 PRIMARY KEY, 
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
    FOREIGN KEY (comment_id) REFERENCES Comments(comment_id)
);

CREATE TABLE user_create_comment( -- comments for each should be created by only one user
	user_id INT4 NOT NULL,
    comment_id INT4 PRIMARY KEY, -- key contraints that for each comments, it can only be created by onw user.
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (comment_id) REFERENCES Comments(comment_id)
);

INSERT INT4O Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INT4O Users (email, password) VALUES ('test1@bu.edu', 'test');
    
    

    
