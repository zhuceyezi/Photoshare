CREATE DATABASE PA1;
use PA1;

CREATE TABLE Users ( -- capitalized entitys for notations
	uid INT PRIMARY KEY AUTO_INCREMENT,
	first_name VARCHAR(10) NOT NULL, -- user must have a name
	last_name VARCHAR(10) NOT NULL,
    email VARCHAR(20) NOT NULL, -- user need to regiester with a email
    job VARCHAR(10),
    hometown VARCHAR(20),
    gender VARCHAR(20),
    password VARCHAR(20)
);

CREATE TABLE be_friend(  -- no capitalized refers to relationships
	uid1 INT, 
    uid2 INT,
    PRIMARY KEY (uid, uid2),
    FOREIGN KEY (uid1) REFERENCES Users(uid),
    FOREIGN KEY (uid2) REFERENCES Users(uid) -- users can be friends of other users (many to many)
);
 -- ALTER TABLE be_friend ADD INDEX(uid1);
 -- ALTER TABLE be_friend CHANGE uid1 uid1 INT AUTO_INCREMENT;

CREATE TABLE Albums(
	aid INT PRIMARY KEY AUTO_INCREMENT, 
	album_name VARCHAR(20),
    owner_id INT, 
    date_creation date
);

CREATE TABLE creating(  -- for each albums, it should be created by only one user. 
	uid INT NOT NULL,  -- total participation constraint that for each albums, it need has at least one user as owner.
    aid INT  PRIMARY KEY,-- aid is unique identify this relationship due to key constraint that for each album, it should have one user at most
    FOREIGN KEY (aid) references Albums(aid) ON DELETE NO ACTION, 
    FOREIGN KEY (uid) references Users(uid) ON DELETE NO ACTION
);

CREATE TABLE Photos(
	pid INT PRIMARY KEY AUTO_INCREMENT,
    data_photo VARCHAR(255),
    caption VARCHAR(20)
);

CREATE TABLE Tags(
	word INT PRIMARY KEY AUTO_INCREMENT
);

CREATE TABLE associate(
	pid INT,
    word INT,
    PRIMARY KEY (pid, word),
    FOREIGN KEY (pid) REFERENCES Photos(pid),
    FOREIGN KEY (word) REFERENCES Tags(word)
);

CREATE TABLE contain(  -- for each photos, it should be contained in only one album
	aid INT NOT NULL,-- total participation constraint that for each photo it should be contained at least one album
    pid INT PRIMARY KEY, -- key constraint that each photo can have at most one album
	FOREIGN KEY (pid) REFERENCES Photos(pid) ON DELETE NO ACTION,
    FOREIGN KEY (aid) REFERENCES  Albums(aid) ON DELETE NO ACTION
);

CREATE TABLE likes(
	uid INT,
    pid INT,
    PRIMARY KEY (uid, pid),
    FOREIGN KEY (uid) REFERENCES Users(uid),
    FOREIGN KEY (pid) REFERENCES Photos(pid)
);

CREATE TABLE Comments(
	cid INT PRIMARY KEY AUTO_INCREMENT,
    text VARCHAR(255),
    owner_id INT,
    date_comment date
);

CREATE TABLE comment_on( -- each comments should related to only one photo
	pid INT NOT NULL, -- participation constraint
    cid INT PRIMARY KEY, -- KEY constraint so cid is unique to identify this relationship
    FOREIGN KEY (pid) REFERENCES photos(pid) ON DELETE NO ACTION,
    FOREIGN KEY (cid) REFERENCES Comments(cid) ON DELETE NO ACTION
);

CREATE TABLE creates( -- comments for each should be created by only one user
	uid INT NOT NULL,
    cid INT PRIMARY KEY, -- key contraints that for each comments, it can only be created by onw user.
    FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE NO ACTION,
    FOREIGN KEY (cid) REFERENCES Comments(cid) ON DELETE NO ACTION
);

    
    

    
