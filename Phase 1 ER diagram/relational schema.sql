CREATE DATABASE PA1;
use PA1;

CREATE TABLE Users ( -- capitalized entitys for notations
	uid VARCHAR(20),
	first_ame VARCHAR(10),
	last_name VARCHAR(10),
    email VARCHAR(20) unique,
    job VARCHAR(10),
    howmtown VARCHAR(20),
    gender VARCHAR(20),
    password VARCHAR(20),
    PRIMARY KEY (uid)
);

CREATE TABLE be_friend(  -- no capitalized refers to relationships
	uid VARCHAR(20),
	PRIMARY KEY (uid),
    fOREIGN KEY (uid) REFERENCES Users(uid)
);

CREATE TABLE Albums(
	aid VARCHAR(20),
	album_name VARCHAR(20),
    owner_id VARCHAR(20),
    date_creation date,
    PRIMARY KEY (aid)
);

CREATE TABLE creating(
	uid VARCHAR(20) not null,
    aid VARCHAR(20),
    primary key (uid),   -- weak entity of album in User: Album that both have key constraint and total participation
    foreign key (aid) references Albums(aid) on delete cascade,
    foreign key (uid) references Users(uid) on delete cascade
);

CREATE TABLE Photos(
	pid VARCHAR(20),
    data_photo VARCHAR(255),
    caption VARCHAR(20),
    primary key (pid)
);

CREATE TABLE Tags(
	word VARCHAR(20),
    primary key (word)
);

CREATE TABLE associate(
	pid VARCHAR(20),
    word VARCHAR(20),
    primary key (pid, word),
    foreign key (pid) references Photos(pid),
    foreign key (word) references Tags(word)
);

CREATE TABLE contain(
	aid VARCHAR(20) not null ,  -- weak entity of photos in album : photos
    pid VARCHAR(20),
    primary key (aid),  -- key constraint that for each photo only stored in one album
    foreign key (pid) references Photos(pid) on delete cascade
);

CREATE TABLE likes(
	uid VARCHAR(20),
    pid VARCHAR(20),
    primary key (uid, pid),
    foreign key (uid) references Users(uid),
    foreign key (pid) references Photos(pid)
);

CREATE TABLE Comments(
	cid VARCHAR(20),
    text VARCHAR(255),
    owner_id VARCHAR(20),
    date_comment date,
    primary key (cid)
);

CREATE TABLE comment_on(
	pid VARCHAR(20) not null, -- weak entity of comments in photos : comments
    cid VARCHAR(20),
    primary key (pid), -- key constrant that for each comments, it can only comments on one single photo
    foreign key (cid) references Comments(cid) on update cascade
);

CREATE TABLE creates(
	uid VARCHAR(20) not null , -- weak entity of comments in users : comments
    cid VARCHAR(20),
    primary key (uid), -- key contraints that for each comments, it can only be created by onw user.
    foreign key (cid) references Comments(cid) on delete cascade
);

    
    
