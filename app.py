######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################
import flask
from flask import Flask, Response, request, render_template, redirect, url_for, flash
from flaskext.mysql import MySQL
import flask_login
import datetime
# for image uploading
import os
import base64
import time

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'aleafy'  # Change this!

visitor_id = -1
# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zhuceyezi'             # change this 'zhuceyezi'
app.config['MYSQL_DATABASE_DB'] = 'pa1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()


def getTags(photo_id):
    c = conn.cursor()
    c.execute(f"SELECT word FROM associate WHERE photo_id = '{photo_id}'")
    conn.commit()
    result = [x[0] for x in c.fetchall()]
    return result


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()


def getCurrentDate():
    return datetime.datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d')


class User(flask_login.UserMixin):
    pass


def isNull(str):
    return str == ""


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute(
        "SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            # protected is a function defined in this file
            return flask.redirect(flask.url_for('protected'))

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier


@app.route('/create_album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == "POST":
        album_name = request.form.get('album_name')
        if album_name == "__secret__":
            return render_template('create_album.html', message='Test Good!')
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        ts = time.time()
        date_created = datetime.datetime.fromtimestamp(
            ts).strftime('%Y-%m-%d')
        cursor = conn.cursor()
        cursor.execute(
            f" INSERT INTO Albums (album_name, user_id, date_created) VALUES ('{album_name}', '{user_id}', '{date_created}')")
        conn.commit()
        return render_template('create_album.html', message='Album Created!')
    else:
        return render_template('create_album.html')


@app.route("/register", methods=['GET'])
def register():
    inUse = request.args.get('inUse')
    if inUse == None:
        inUse = False
    return render_template('register.html', inUse=inUse)


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        print(f"dob: {dob}")
        if dob == '':
            dob = None
        hometown = request.form.get('hometown')
        if hometown == '':
            hometown = None
        gender = request.form.get('gender')
        if gender == '':
            gender = None
    except:
        # this prints to shell, end users will not see this (all print statements go to shell)
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        query = "INSERT INTO Users (first_name, last_name, email, dob, hometown, gender, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (first_name, last_name, email, dob, hometown, gender, password))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register', inUse=True))


def getUsersPhotos(user_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT imgdata, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(user_id))
    # NOTE return a list of tuples, [(imgdata, photo_id, caption), ...]
    return cursor.fetchall()


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def getCurrentUserId():
    try:
        return getUserIdFromEmail(flask_login.current_user.id)
    except:
        return -1


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True
# end login code


@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        album_id = request.form.get('album_id')
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        tags = request.form.get("tags").split(" ")
        # photo_data = base64.standard_b64encode(imgfile.read())
        photo_data = imgfile.read()
        cursor = conn.cursor()
        query = "INSERT INTO Photos (user_id, album_id, imgdata, caption) VALUES (%s, %s, %s, %s)"
        # print(query)
        cursor.execute(query, (user_id, album_id, photo_data, caption))
        conn.commit()
        if tags[0] != '':
            cursor.execute(
                f"SELECT photo_id FROM Photos WHERE user_id = {user_id} AND album_id = {album_id} ORDER BY photo_id DESC LIMIT 1")
            photo_id = cursor.fetchone()[0]
            # print(photo_id)
            for tag in tags:
                createTagIfNotExist(tag)
                addTagToPhoto(tag, photo_id)
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(user_id), base64=base64)
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html', albums=getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id)))
# end photo uploading code


def isAFriend(to_user_id):
    """ Return if the user is a friend of the current user.\n
    NOTE: also returns true if current user == to_user_id """

    user_id = getCurrentUserId()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT user_id_to FROM be_friend WHERE user_id_from = '{user_id}' AND user_id_to = '{to_user_id}'")
    conn.commit()
    fetchRes = cursor.fetchone() # fetchone() returns None if no result
    if fetchRes is None and to_user_id != user_id: # if the user is not a friend and not the current user
        return False
    return True


def addFriend(from_user_user_id, to_user_user_id):
    """ 
    Input: Two user id
    User can add another user as friend
    The "Friend" here is more like "follow": it is one way instead of mutual
    """
    cursor = conn.cursor()
    query = f"INSERT INTO be_friend (user_id_from, user_id_to) VALUES ('{from_user_user_id}', '{to_user_user_id}')"
    cursor.execute(query)
    conn.commit()


@app.route('/add_friend', methods=['GET', 'POST'])
@flask_login.login_required
def route_add_friend():
    if request.method == 'GET':
        to_user_id = request.args.get('user_id')
        add = request.args.get('add')
        src = request.args.get('src')

        user_list = []
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id, first_name, last_name FROM Users")
        conn.commit()
        lst = cursor.fetchall()
        user_list = []
        for i in range(len(lst)):
            user = lst[i]
            if user[0] != -1:
                user_list.append((i+1, user[0], user[1], user[2]))
        if not to_user_id is None:
            addFriend(getCurrentUserId(), to_user_id)
            if src == 'email':
                print("hi")
                return redirect(url_for('friends', message="Friend added!"))
        if to_user_id is None:
            return render_template('add_friends.html', isAFriend=isAFriend,
                                   user_list=user_list, email='', add=add)

        return redirect(url_for('route_add_friend', add=True))
    else:
        email = request.form.get('email')
        friends = getUserInfoFromEmail(email)
        return redirect(url_for('route_add_friend'))


@app.route('/add_friend_by_email', methods=['POST'])
@flask_login.login_required
def add_friend_by_email():
    email = request.form.get('email')
    friends = getUserInfoFromEmail(email)
    return render_template('add_friends.html', isAFriend=isAFriend,
                           user_list=friends, email='', src='email')


def getUserInfoFromEmail(email=''):
    if email == '':
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id, first_name, last_name FROM Users")
        conn.commit()
        lst = cursor.fetchall()
        user_list = []
        for i in range(len(lst)):
            user = lst[i]
            user_list.append((i+1, user[0], user[1], user[2]))
        return user_list
    else:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT user_id, first_name, last_name FROM Users WHERE email = '{email}'")
        conn.commit()
        lst = cursor.fetchall()
        friends = []
        for i in range(len(lst)):
            friends.append((i+1, lst[i][0], lst[i][1], lst[i][2]))
        return friends


@app.route('/delete_friend', methods=['GET'])
@flask_login.login_required
def deleteFriend():
    from_user_user_id = getCurrentUserId()
    # print(from_user_user_id)
    to_user_user_id = request.args.get('to_user_user_id')
    # print(to_user_user_id)
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM be_friend WHERE user_id_from='{from_user_user_id}' AND user_id_to='{to_user_user_id}'")
    conn.commit()
    friends = listAllFriends(from_user_user_id)
    # print(friends)
    return render_template("friends.html", friends=friends, friend_num=len(friends), message="Friend deleted!")


def listAllFriends(user_id):
    """ 
    Input: (int) user_id of user.\n
    Output: a list of tuples (index, user_id, first_name, last_name)\n
    list all friends of an user. 
    """
    cursor = conn.cursor()
    query = f"SELECT f.user_id_to as friend_id, u.first_name, u.last_name FROM be_friend f, Users u WHERE u.user_id = f.user_id_to AND f.user_id_from = '{user_id}'"
    cursor.execute(query)
    conn.commit()
    friends = cursor.fetchall()
    # print(friends)
    friend_list = []
    for i in range(len(friends)):
        friend = friends[i]
        friend_list.append((i+1, friend[0], friend[1], friend[2]))
    return friend_list

# steven done


def getUserName(user_id):
    """ input: (int) user_id of user.\n
    output: list of str: first name, last name of user.\n
    """
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT first_name, last_name FROM Users WHERE user_id = {user_id}")
    conn.commit()
    return cursor.fetchone()


def getActivity(user_id):
    """ 
    Input: (int) user_id of user.\n
    Output: (int) activity of the user\n

    get the activity/contribution of an user\n
    Activity = number of photos uploaded by the user + number of comments by the user
    """
    cursor = conn.cursor()
    count_photos = f''' SELECT COUNT(*) FROM Photos WHERE user_id = {user_id} '''
    count_comments = f''' SELECT COUNT(*) FROM Comments WHERE user_id = {user_id} '''

    cursor.execute(count_photos)
    photos = cursor.fetchone()[0]

    cursor.execute(count_comments)
    comments = cursor.fetchone()[0]

    # checking if there are no photos or comments associated with the user specified by user_id.
    if not photos and not comments:
        return None

    activity = photos + comments
    cursor.close()
    return activity


# steven done

@app.route('/gallery', methods=["GET"])
def getAllPhotos():
    cursor = conn.cursor()
    cursor.execute(f"SELECT imgdata, photo_id, caption FROM Photos")
    conn.commit()
    photos = cursor.fetchall()
    return render_template('gallery.html', getTags=getTags, notLiked=notLiked, getOwnerId=getOwnerId, user_id=getCurrentUserId(), photos=photos, base64=base64, isMyPhoto=isMyPhoto)


def getAlbumId(photo_id):
    c = conn.cursor()
    c.execute(f"SELECT album_id FROM Photos WHERE photo_id = '{photo_id}'")
    conn.commit()
    return c.fetchone()[0]


def getUsersAlbums(user_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT album_id, album_name FROM Albums WHERE user_id = {user_id}")
    conn.commit()
    return cursor.fetchall()


@app.route('/album_gallery', methods=["GET"])
def getAllAlbums():
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT a.album_id, a.album_name, a.date_created, COUNT(p.photo_id), a.user_id\
        FROM Albums a, Photos p WHERE p.album_id=a.album_id\
        GROUP BY a.album_id\
        UNION\
        SELECT a.album_id, a.album_name, a.date_created, 0, a.user_id\
        FROM Albums a\
        EXCEPT\
        SELECT a.album_id, a.album_name, a.date_created, 0, a.user_id\
        FROM Albums a, Photos p WHERE p.album_id=a.album_id\
        GROUP BY a.album_id")
    conn.commit()
    albums = cursor.fetchall()
    return render_template('album_gallery.html', albums=albums, isMyPhoto=isMyPhoto)


def getUserNameFromId(user_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT first_name, last_name FROM Users WHERE user_id = {user_id}")
    conn.commit()
    return cursor.fetchone()[0]


@app.route('/delete_album', methods=["GET"])
@flask_login.login_required
def route_delete_album():
    album_id = request.args.get('album_id')
    deleteAlbum(album_id)
    return render_template('view_albums.html', message="album deleted!", albums=getUsersAlbums(getCurrentUserId()))


def deleteAlbum(album_id):
    c = conn.cursor()
    c.execute(f"DELETE FROM Albums WHERE album_id = {album_id}")
    conn.commit()


def createTagIfNotExist(word):
    """ 
    Input: (string) word of a tag.\n
    Output: None\n
    Creates a tag """
    cursor = conn.cursor()
    cursor.execute(f"SELECT word FROM Tags WHERE word = '{word}'")
    if cursor.fetchone() is None:
        query = f"INSERT INTO Tags (word) VALUES ('{word}')"
        cursor.execute(query)
        conn.commit()


def addTagToPhoto(word, photo_id):
    """ associates a tag with a photo """
    cursor = conn.cursor()
    query = f"INSERT INTO associate (photo_id, word) VALUES ('{photo_id}', '{word}')"
    cursor.execute(query)
    conn.commit()


def deleteTag(word):
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Tags WHERE word = '{word}'")
    conn.commit()


@app.route('/deletePhoto', methods=["GET"])
@flask_login.login_required
def deletePhoto():
    photo_id = request.args.get('photo_id')
    album_id = request.args.get('album_id')
    src = request.args.get("src")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Photos WHERE photo_id = '{photo_id}'")
    conn.commit()
    if src == 'open_album':         # if the user is coming from the open_album page
        return redirect(url_for('open_album', album_id=album_id))
    elif src == 'gallery':          # if the user is coming from the gallery page
        return redirect(url_for('getAllPhotos'))
    elif src == 'photo_recommendation':
        return redirect(url_for('photo_recommendation'))
    elif src == 'searchPhotoByTags':
        str = request.args.get('str')
        return redirect(url_for('searchPhotoByTags', str=str))
    elif src == 'viewAllByTag':
        tag = request.args.get("tag")
        return redirect(url_for('viewAllPhotosByTag', tag=tag))
    elif src == 'viewUserByTag':
        tag = request.args.get("tag")
        return redirect(url_for('viewUserPhotosByTag', tag=tag))

def unassociateTag(word, photo_id):
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM associate WHERE photo_id = '{photo_id}' AND word = '{word}'")
    conn.commit()


# @app.route('/viewPhotosByTag/<tag>', defaults={'user_id': None})

def viewAllPhotosByTag_steve():
    """ 
    Input: (str) tag of a photo.\n
    Output: a html template passing a list of photo tuples (photo_id, imgdata, caption)\n
    Exhibit all photos of a certain tag
    """
    cursor = conn.cursor()
    # get tag from url
    tag = request.args.get('tag')
    user_id = getCurrentUserId()
    # query = f"SELECT associate.photo_id, Photos.imgdata, Photos.caption FROM Photos, associate WHERE word = '{tag}'"
    # cursor.execute(query)
    # photos = cursor.fetchall()
    # return photos
    if user_id != visitor_id:
        query = f"SELECT p.imgdata, p.photo_id, p.caption, a.word FROM associate a NATURAL JOIN Photos p WHERE a.word = '{tag}' AND p.user_id = '{user_id}'"
    else:
        query = f"SELECT p.imgdata, p.photo_id, p.caption, a.word FROM associate a NATURAL JOIN Photos p WHERE a.word = '{tag}'"
    cursor.execute(query)
    photos = cursor.fetchall()

    return render_template('viewPhotosByTag.html', tag=tag, photos=photos)





def viewUserPhotosByTag_steve():
    """ 
    Input: (int) user_id of user.\n
    (str) tag of a photo.\n
    Output: a html template passing a list of photo tuples (photo_id, imgdata, caption)\n
    Exhibit all photos of a certain tag of one user
    """
    cursor = conn.cursor()
    user_id = getCurrentUserId()
    # query = f"SELECT photo_id FROM(SELECT associate.photo_id, Photos.user_id,\
    #          Photos.caption FROM Photos, associate WHERE word='{tag}') as x WHERE x.user_id = {user_id}"
    # cursor.execute(query)
    # cursor.execute(query)
    # photos = cursor.fetchall()
    # return photos
    #----------------------------------------------------------------------------------------------------
    # Query to get all tags associated with user's photos
    tags_query = f"SELECT DISTINCT word FROM associate WHERE photo_id IN \
                   (SELECT photo_id FROM Photos WHERE user_id = '{user_id}')"
    cursor.execute(tags_query)
    conn.commit()
    tags = [row[0] for row in cursor.fetchall()]

    # Query to get photos associated with selected tag
    photos_query = f"SELECT p.photo_id, p.imgdata, p.caption FROM Photos p, associate a\
                     WHERE a.word = '{tag}' AND p.photo_id = a.photo_id \
                     AND p.user_id = '{user_id}'"
    cursor.execute(photos_query)
    conn.commit()
    photos = cursor.fetchall()
    print(photos)
    cursor.close()
     # commit changes to db
    return render_template('viewUserPhotosByTag.html', photos=photos[1], base64=base64, 
                           user_id=user_id, tag=tag, tags=tags)

@app.route('/viewAllByTag', methods=['GET'])
def viewAllPhotoTags():
    # get all tags of all photo
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT word FROM Associate")
    conn.commit()
    tags = [x[0] for x in c.fetchall()]
    return render_template('viewByTag.html', tags=tags, viewType = "All")

@app.route('/viewUserByTag',methods=['GET'])
@flask_login.login_required
def viewUserPhotoTags():
    c = conn.cursor()
    user_id = getCurrentUserId()
    c.execute(f"SELECT DISTINCT a.word FROM associate a NATURAL JOIN Photos p WHERE p.user_id = {user_id}")
    conn.commit()
    tags = [x[0] for x in c.fetchall()]
    return render_template('viewByTag.html',tags=tags,viewType="User")
    
 
@app.route('/viewAllPhotosByTag', methods=['GET'])
def viewAllPhotosByTag():
    tag = request.args.get('tag')
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT word FROM Associate")
    conn.commit()
    tags = [x[0] for x in c.fetchall()]
    
    c.execute(f"SELECT p.imgdata, p.photo_id, p.caption, a.word FROM associate a NATURAL JOIN Photos p WHERE a.word = '{tag}'")
    conn.commit()
    result = c.fetchall()
    return render_template('viewByTag.html',photos=result, tag=tag, tags=tags,viewType="All",base64=base64,notLiked=notLiked,getOwnerId=getOwnerId,user_id=getCurrentUserId(),getTags=getTags)
                    
@app.route('/viewUserPhotosByTag',methods=['GET'])
@flask_login.login_required
def viewUserPhotosByTag():
    tag = request.args.get('tag')
    c = conn.cursor()
    user_id = getCurrentUserId()
    c.execute(f"SELECT DISTINCT a.word FROM associate a NATURAL JOIN Photos p WHERE p.user_id = '{user_id}'")
    conn.commit()
    tags = [x[0] for x in c.fetchall()]
    
    c.execute(f"SELECT p.imgdata, p.photo_id, p.caption, a.word FROM associate a NATURAL JOIN Photos p WHERE a.word = '{tag}' AND p.user_id='{user_id}'")
    conn.commit()
    result = c.fetchall()
    return render_template('viewByTag.html',photos=result, tag=tag, tags=tags,viewType="User",base64=base64,notLiked=notLiked,getOwnerId=getOwnerId,user_id=getCurrentUserId(),getTags=getTags)
        

@app.route('/viewMostpopularTags', methods=["GET"])
def viewMostPopularTags():
    """ List the most popular three tags, i.e., the three tags 
        that are associated with the largest number of photos, in descending
        popularity order."""
    cursor = conn.cursor()
    cursor.execute(
        f"WITH t3c(count) as (SELECT count FROM (SELECT word, COUNT(photo_id) as count FROM associate GROUP BY word ORDER BY COUNT(photo_id) DESC LIMIT 3) as x),\
tac(word,count) as (SELECT word, count FROM (SELECT word, COUNT(photo_id) as count FROM associate GROUP BY word ORDER BY COUNT(photo_id) DESC) as x)\
(SELECT DISTINCT tac.word, t3c.count FROM tac NATURAL JOIN t3c)")
    conn.commit()
    tags = cursor.fetchall()
    return render_template('viewMostPopularTags.html', tags=tags)


@app.route('/search_tags', methods=["GET","POST"])
def searchPhotoByTags():
    """ search by a list of tags.For example, a visitor could enter the words "friends boston" in an input box, click 
    the search button, and be presented with all photos that contain both the tag "friends" and the tag "boston". """
    if request.method == "POST":
        str = request.form.get("str")
    if request.method == "GET":
        str = request.args.get("str")
    tags = str.split(" ")
    lst = []
    mid = ""
    for i in range(len(tags)):
        tag = tags[i]
        if i == 0:
            mid += f"'{tag}'"
        else:
            mid += f" OR t.word = '{tag}'"
    with_clause = f"WITH qtags(word) as (SELECT t.word FROM tags t WHERE t.word ={mid}),"
    query = f"{with_clause} pids(photo_id) as (SELECT photo_id FROM Photos),\
dq(photo_id,word) as ((SELECT p.photo_id, qt.word FROM pids p, qtags qt) EXCEPT (SELECT a.photo_id, a.word FROM Associate a)),\
qualifiedPids(photo_id) as (SELECT p.photo_id FROM pids p EXCEPT (SELECT photo_id FROM dq)),\
result(imgdata, photo_id, caption, word) as (SELECT p.imgdata, p.photo_id, p.caption, a.word FROM associate a NATURAL JOIN qualifiedPids q NATURAL JOIN Photos p )\
(SELECT DISTINCT r.imgdata, r.photo_id, r.caption FROM result r)"
    c = conn.cursor()
    # check if tag exists:
    exists = True
    if allTagExists(tags):
        c.execute(query)
        conn.commit()
        lst = c.fetchall()
    else:
        lst = []
    return render_template("search_result.html", user_id=getCurrentUserId(),getOwnerId=getOwnerId,photos=lst, base64=base64, notLiked=notLiked, getTags=getTags, str=str) 

def allTagExists(tags):
    c = conn.cursor()
    for tag in tags:
        c.execute(f"SELECT word FROM tags WHERE word = '{tag}'")
        conn.commit()
        result = c.fetchone()
        if result == None:
            return False
    return True

@app.route("/comments", methods=["GET"])
def show_comments():
    photo_id = request.args.get('photo_id')
    c = conn.cursor()
    c.execute(
        f"SELECT imgdata, photo_id FROM Photos WHERE photo_id = '{photo_id}'")
    conn.commit()
    imgdata, photo_id = c.fetchone()
    comments = getCommentsFromPhoto(photo_id)
    return render_template("show_comments.html", photo=imgdata, base64=base64, comments=comments, photo_id=photo_id,
                           isMyPhoto=isMyPhoto)


def getCommentsFromPhoto(photo_id):
    """ 
    Input: (int) photo_id of a photo.\n
    Output: list of (first_name, last_name, email, content, date_comment)
    """
    c = conn.cursor()
    cursor.execute(
        f"SELECT u.first_name, u.last_name, u.email, c.content, c.date_comment FROM Comments c NATURAL JOIN Users u WHERE photo_id = '{photo_id}' ORDER BY date_comment DESC")

    conn.commit()
    comments = cursor.fetchall()
    return comments

# steven done


@app.route("/search_comment", methods=["POST"])
def search_comment():
    str = request.form.get('str')
    c = conn.cursor()
    c.execute(
        f"SELECT u.first_name, u.last_name, u.email, u.user_id, COUNT(*) as count FROM Comments c NATURAL JOIN Users u WHERE c.content = '{str}' GROUP BY u.user_id ORDER BY COUNT(*) DESC")
    conn.commit()
    results = c.fetchall()
    return render_template("search_result.html", results=results)


@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")


@app.route('/leave_comment', methods=["POST"])
def leaveComment():
    """ 
    input: (int) photo_id of a photo that user is comment on.\n
    Output: None\n

    user leaves a comment. 
    NOTE: Users cannot leave a comment own their own photo.

    """
    user_id = getCurrentUserId()
    photo_id = request.args.get('photo_id')
    comment = request.form.get('content')
    cursor = conn.cursor()
    # insert the comment into the database
    insert = f"INSERT INTO Comments (photo_id, user_id, content,date_comment) VALUES ({photo_id}, {user_id}, '{comment}','{getCurrentDate()}')"
    cursor.execute(insert)
    conn.commit()  # commit changes made to the database
    cursor.close()
    return redirect(url_for('show_comments', photo_id=photo_id))


def getOwnerId(photo_id):
    c = conn.cursor()
    c.execute(f"SELECT user_id FROM Photos WHERE photo_id = '{photo_id}'")
    return c.fetchone()[0]

# steven done


@app.route("/like", methods=['GET'])
@flask_login.login_required
def likePhoto():
    """ 
    Input: (int) photo_id \n
    Output: JSON object indicating whether the like action was successful or not.\n

    user likes a photo 
    """
    user_id = getCurrentUserId()
    photo_id = request.args.get('photo_id')
    src = request.args.get('src')
    if src == 'open_album':
        album_id = request.args.get('album_id')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_like_photo (user_id, photo_id) VALUES (%s, %s)",
                   (user_id, photo_id))  # insert the like into the database
    conn.commit()                       # commit changes made to the database
    cursor.close()                      # close the cursor

    # return success message
    if src == 'open_album':         # if the user is coming from the open_album page
        return redirect(url_for('open_album', album_id=album_id))
    elif src == 'gallery':          # if the user is coming from the gallery page
        return redirect(url_for('getAllPhotos'))
    elif src == 'photo_recommendation':
        return redirect(url_for('photo_recommendation'))
    elif src == 'searchPhotoByTags':
        str = request.args.get('str')
        return redirect(url_for('searchPhotoByTags', str=str))
    elif src == 'viewAllByTag':
        tag = request.args.get("tag")
        return redirect(url_for('viewAllPhotosByTag', tag=tag))
    elif src == 'viewUserByTag':
        tag = request.args.get("tag")
        return redirect(url_for('viewUserPhotosByTag', tag=tag))


@app.route('/unlike', methods=['GET'])
@flask_login.login_required
def unlikePhoto():
    photo_id = request.args.get('photo_id')
    src = request.args.get('src')
    user_id = getCurrentUserId()
    if src == 'open_album':
        album_id = request.args.get('album_id')
    c = conn.cursor()
    c.execute(
        f"DELETE FROM user_like_photo WHERE user_id = '{user_id}' AND photo_id = '{photo_id}'")
    conn.commit()
    if src == 'open_album':
        return redirect(url_for('open_album', album_id=album_id))
    elif src == 'gallery':
        return redirect(url_for('getAllPhotos'))
    elif src == 'photo_recommendation':
        return redirect(url_for('photo_recommendation'))
    elif src == 'searchPhotoByTags':
        str = request.args.get('str')
        return redirect(url_for('searchPhotoByTags', str=str))
    elif src == 'viewAllByTag':
        tag = request.args.get("tag")
        return redirect(url_for('viewAllPhotosByTag', tag=tag))
    elif src == 'viewUserByTag':
        tag = request.args.get("tag")
        return redirect(url_for('viewUserPhotosByTag', tag=tag))

# steven done


def searchUsersOnComment(query_text):
    """
    Input: (str) query_text, the text to search for in user comments.
    Output: (list) a list of tuples, each tuple containing the name of a user and the number of comments that match the query text. 
            The list is ordered by the number of comments in descending order.

    find the users that have created comments that exactly match the 
    input query text. Return the names of these users ordered by the number of comments that match the query 
    in descending order. 
    """
    cursor = conn.cursor()
    # query to find the users that have created comments that exactly match the input query text
    query = f'''                
        SELECT u.name, COUNT(c.comment_id)
        FROM Users u
        JOIN Comments c ON u.user_id = c.user_id
        WHERE c.content LIKE %s                         
        GROUP BY u.user_id
        ORDER BY COUNT(c.comment_id) DESC
    '''
    cursor.execute(query, ('%' + query_text + '%',)
                   )        # hold the query text in a tuple
    result = cursor.fetchall()  # get the result
    cursor.close()  # close the cursor
    return result


# steven done
def friendRecommendation(user_id):
    """
    Input: (int) user_id, the id of the input user.
    Output: (list) a list of tuples, each tuple containing the name and id of a potential friend for the input user. 
    The list is ordered by the number of mutual friends in descending order.

    recommend potential friends of a user. A potential friend of the input user is defined as some user who does not have a friend relationship with the input user, 
    AND has at least one mutual friend in between the input user and the potential friend user.
    """
    cursor = conn.cursor()
    query = '''
        SELECT 
            u.user_id, u.first_name, u.last_name, u.email
            COUNT(DISTINCT bf2.user_id_from) AS mutual_friends 
        FROM 
            Users u 
            LEFT JOIN be_friend bf1 ON bf1.user_id_to = u.user_id 
            LEFT JOIN be_friend bf2 ON bf2.user_id_from = bf1.user_id_from 
                                        AND bf2.user_id_to != %s
        WHERE 
            u.user_id != %s 
            AND bf1.user_id_from != %s 
            AND NOT EXISTS (
                SELECT * 
                FROM be_friend 
                WHERE user_id_from = %s 
                        AND user_id_to = u.user_id
            )
        GROUP BY 
            u.user_id 
        ORDER BY 
            mutual_friends DESC 
    '''
    cursor.execute(query, (user_id, user_id, user_id, user_id)
                   )  # execute the query with holders to avoid sql injection
    result = cursor.fetchall()
    cursor.close()                  # close the cursor
    return result


# steven done
def photoRecommendation(user_id):
    """
    Input: (int) user_id - the id of the user for whom to recommend photos
    Output: (list) a list of tuples, each containing the photo_id and caption of a photo that the user may like, 
    ordered by the number of similar likes in descending order.

    Recommend photos that the user with the input id may like based on their likesPhoto history.
    """
    cursor = conn.cursor()
    # The query retrieves the photo_id, caption, and the number of similar likes for each photo,
    # based on the user's liking history.
    query = '''
        SELECT 
            p.photo_id, p.caption,
            COUNT(DISTINCT ulp2.user_id) AS similar_likes
        FROM 
            Photos p 
            LEFT JOIN user_like_photo ulp1 ON ulp1.photo_id = p.photo_id 
            LEFT JOIN user_like_photo ulp2 ON ulp2.photo_id = ulp1.photo_id
                                            AND ulp2.user_id != %s
        WHERE 
            ulp1.user_id = %s
            AND NOT EXISTS (
                SELECT * 
                FROM user_like_photo 
                WHERE user_id = %s 
                    AND photo_id = p.photo_id
            )
        GROUP BY 
            p.photo_id 
        ORDER BY 
            similar_likes DESC
        '''
    cursor.execute(query, (user_id, user_id, user_id))
    result = cursor.fetchall()
    cursor.close()
    return result


@app.route('/open_album', methods=["GET"])
def open_album():
    album_id = request.args.get("album_id")
    print("----")
    print(album_id)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT imgdata, photo_id, caption FROM Photos WHERE album_id='{album_id}'")
    conn.commit()
    photos = cursor.fetchall()
    cursor.execute(
        f"SELECT album_name FROM Albums WHERE album_id='{album_id}'")
    album_name = cursor.fetchone()[0]
    return render_template('open_album.html', getTags=getTags, notLiked=notLiked, getOwnerId=getOwnerId, user_id=getCurrentUserId(), album_name=album_name, photos=photos, base64=base64, album_id=album_id, isMyPhoto=isMyPhoto)


def getPhotosFromAlbum(album_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT imgdata, photo_id, caption FROM Photos WHERE album_id='{album_id}'")
    conn.commit()
    photos = cursor.fetchall()
    cursor.execute(f"SELECT album_name FROM Albums WHERE album_id={album_id}")
    return photos

# default page


def notLiked(user_id, photo_id):
    c = conn.cursor()
    c.execute(
        f"SELECT user_id, photo_id FROM user_like_photo WHERE user_id = '{user_id}' AND photo_id = '{photo_id}'")
    conn.commit()
    result = c.fetchone()
    if result is None:
        return True
    else:
        return False


@app.route('/view_albums', methods=['GET'])
@flask_login.login_required
def listAlbums():
    user_id = getCurrentUserId()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT a.album_id, a.album_name, a.date_created, COUNT(p.photo_id)\
        FROM Albums a, Photos p WHERE p.album_id=a.album_id AND a.user_id={user_id} GROUP BY a.album_id\
        UNION\
        SELECT a.album_id, a.album_name, a.date_created, 0\
        FROM Albums a WHERE a.user_id={user_id} EXCEPT\
        SELECT a.album_id, a.album_name, a.date_created, 0\
        FROM Albums a, Photos p WHERE p.album_id=a.album_id AND a.user_id={user_id} GROUP BY a.album_id ")
    conn.commit()
    albums = cursor.fetchall()
    return render_template('view_albums.html', albums=albums, isMyPhoto=isMyPhoto)


def getUserAlbums(user_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT album_id, album_name FROM albums WHERE user_id={user_id}")
    conn.commit()
    return cursor.fetchall()


@app.route("/friends", methods=["GET"])
@flask_login.login_required
def friends():
    print("There!")
    user_id = getCurrentUserId()
    friends = listAllFriends(user_id)
    message = request.args.get('message')
    if message == None:
        message = ''
    return render_template('friends.html', friends=friends, friend_num=len(friends), message=message)


def isMyPhoto(photo_id):
    user_id = getCurrentUserId()
    c = conn.cursor()
    c.execute(
        f"SELECT photo_id FROM Photos WHERE user_id={user_id} AND photo_id={photo_id}")
    conn.commit()
    pid = c.fetchone()
    if pid is None:
        return False
    return True


@app.route('/top_users', methods=['GET'])
def top_users():
    c = conn.cursor()
    # cp as count of photos, cc as count of comments
    # consider both case that a user has only upload photos or only write comments while the other data is Null, so we use LEFT/right OUTER JOIN 
    # And union both cases as result( sum, uid)
    c.execute(f"WITH cp(cp, uid) AS(\
        SELECT COUNT(p.user_id), u.user_id FROM Photos p, Users u WHERE p.user_id=u.user_id GROUP BY u.user_id\
    ),\
        cc(cc, uid) AS(\
        SELECT COUNT(c.user_id), u.user_id FROM Comments c, Users u WHERE c.user_id=u.user_id GROUP BY u.user_id\
    ),\
        result(sum, uid) as (\
        SELECT(IFNULL(cc.cc, 0)+IFNULL(cp.cp, 0)), cc.uid FROM cp RIGHT OUTER JOIN cc ON cc.uid=cp.uid\
        UNION\
        SELECT(IFNULL(cc.cc, 0)+IFNULL(cp.cp, 0)), cp.uid FROM cp LEFT OUTER JOIN cc ON cc.uid=cp.uid\
    )\
        SELECT u.first_name, u.last_name, u.email, r.sum FROM result r JOIN Users u ON r.uid = u.user_id WHERE r.uid <> -1 ORDER BY r.sum DESC LIMIT 3\
        ")
    conn.commit()
    topten = c.fetchall()
    # rank = []
    # for user in users:
    #     uid = user[0]
    #     contribution = getActivity(uid)
    #     if contribution != None:
    #         rank.append((contribution, uid))
    # rank.sort(reverse=True)
    # topten = []
    # for user in rank[:10]:
    #     contribution, uid = user
    #     c.execute(
    #         f"select first_name, last_name, email, {contribution}  from Users where user_id = {uid}")
    #     conn.commit()
    #     result = c.fetchone()
    #     topten.append(result)
    return render_template('top_users.html', topten=topten)


@app.route("/like_data", methods=["GET"])
def like_data():
    photo_id = request.args.get('photo_id')
    c = conn.cursor()
    c.execute(
        f"SELECT u.first_name, u.last_name, u.email FROM user_like_photo l NATURAL JOIN Users u Where photo_id = '{photo_id}'")
    conn.commit()
    result = c.fetchall()
    c.execute(
        f"SELECT COUNT(*) FROM user_like_photo WHERE photo_id = '{photo_id}'")
    conn.commit()
    count = c.fetchone()[0]
    return render_template('like_data.html', results=result, count=count)


@app.route("/friend_recommendation", methods=["GET"])
@flask_login.login_required
def friend_recommendation():
    user_id = getCurrentUserId()
    fof = friends_of_friends(user_id)
    # fof = friendRecommendation(user_id)
    return render_template('friend_recommendation.html', friends=fof)


@app.route("/add_friend_friend_recommendation", methods=["GET"])
@flask_login.login_required
def add_friend_friend_recommendation():
    user_id = getCurrentUserId()
    to_user_id = request.args.get('to_user_id')
    addFriend(user_id, to_user_id)
    return redirect(url_for('friend_recommendation'))


def friends_of_friends(user_id):
    c = conn.cursor()
    c.execute(f"With f(user_id) as (SELECT u.user_id from be_friend b JOIN users u ON b.user_id_to=u.user_id WHERE b.user_id_from='{user_id}'),\
              tmp(count, user_id) as (SELECT Count(b.user_id_to), b.user_id_to FROM f JOIN be_friend b on b.user_id_from=f.user_id GROUP BY b.user_id_to)\
              (SELECT tmp.count, u.user_id, u.first_name, u.last_name, u.email FROM tmp JOIN users u ON u.user_id=tmp.user_id)\
              ")
    conn.commit()
    friends = list(c.fetchall())
    ans_f = []
    for friend in friends:
        if not isAFriend(friend[1]):
            ans_f.append(friend)
    print(ans_f)
    return ans_f
    # c = conn.cursor()
    # # Get all friend ids
    # c.execute(
    #     f"SELECT u.user_id from be_friend f JOIN users u ON f.user_id_to = u.user_id WHERE f.user_id_from = '{user_id}'")
    # conn.commit()
    # friends = c.fetchall()
    # friends_of_friends = {}
    # for friend in friends:
    #     friend_id = friend[0]
    #     # get the friends of the friend
    #     c.execute(
    #         f"SELECT u.user_id, u.first_name, u.last_name, u.email from be_friend f JOIN users u ON f.user_id_to = u.user_id WHERE f.user_id_from = '{friend_id}'")
    #     conn.commit()
    #     lst = c.fetchall()
    #     for item in lst:
    #         if isAFriend(item[0]):
    #             continue
    #         else:
    #             if friends_of_friends.get(item[0]) == None:
    #                 friends_of_friends[item[0]] = [1, item]
    #             else:
    #                 cur = friends_of_friends.get(item[0])
    #                 friends_of_friends[item[0]] = [cur[0]+1, item]
    # result = [v for v in friends_of_friends.values()]
    # result.sort(reverse=True)
    # return result


@app.route('/photo_recommendation', methods=['GET'])
@flask_login.login_required
def photo_recommendation():
    user_id = getCurrentUserId()
    photos = photoRecommendation(user_id)
    return render_template('photo_recommendation.html', photos=photos, base64=base64, isMyPhoto=isMyPhoto, getOwnerId=getOwnerId, user_id=getCurrentUserId(), notLiked=notLiked, getTags=getTags)


def photoRecommendation(user_id):
    # first get the three most common tags of the user's photos
    matchScore = 1000000
    unmatchCost = 1
    c = conn.cursor()
    c.execute(f"SELECT COUNT(a.word) as count, a.word from\
        users u NATURAL JOIN photos p NATURAL JOIN associate a WHERE u.user_id = {user_id} GROUP BY a.word ORDER BY count DESC LIMIT 3")
    conn.commit()
    fav3 = [x[1] for x in c.fetchall()]  # favorite 3 tags
    print(fav3)
    # get the photo id of all the photos except the user's
    c.execute(f"SELECT photo_id FROM photos WHERE user_id <> '{user_id}'")
    conn.commit()
    photos = [x[0] for x in c.fetchall()]

    # rate each photo
    rating = {}
    for photo_id in photos:
        # get all the tags of the photo
        c.execute(
            f"SELECT a.word FROM associate a WHERE a.photo_id = '{photo_id}'")
        conn.commit()
        tags = [x[0] for x in c.fetchall()]
        rating[photo_id] = 0
        for tag in tags:
            if tag in fav3:
                rating[photo_id] += matchScore
            else:
                rating[photo_id] -= unmatchCost
    result = [(v, k) for k, v in rating.items() if v > 0]
    result.sort(reverse=True)
    print(rating)
    print(result)
    # Now append the imgdata to the photo
    final = []
    for res in result:
        pid = res[1]
        c.execute(
            f"SELECT imgdata,photo_id,caption FROM Photos WHERE photo_id = '{pid}'")
        conn.commit()
        data = c.fetchone()
        final.append(data)
    return final


@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True, host="0.0.0.0")
