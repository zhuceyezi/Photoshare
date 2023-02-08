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
from flask import Flask, Response, request, render_template, redirect, url_for
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

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zhuceyezi'
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


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


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
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
    except:
        # this prints to shell, end users will not see this (all print statements go to shell)
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute(
            "INSERT INTO Users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))


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
        # photo_data = base64.standard_b64encode(imgfile.read())
        photo_data = imgfile.read()
        cursor = conn.cursor()
        query = "INSERT INTO Photos (user_id, album_id, imgdata, caption) VALUES (%s, %s, %s, %s)"
        # print(query)
        cursor.execute(query, (user_id, album_id, photo_data, caption))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(user_id), base64=base64)
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')
# end photo uploading code


def addFriend(from_user_user_id, to_user_user_id):
    """ User can add another user as friend
    The "Friend" here is more like "follow": it is one way instead of mutual """
    cursor = conn.cursor()
    query = f'''INSERT INTO be_friend (user_id_from, user_id_to) VALUES ({from_user_user_id}, {to_user_user_id})'''
    cursor.execute(query)
    conn.commit()


def listAllFriends(user_id):
    """ 
    Input: (int) user_id of user.\n
    Output: a list of tuples (user_id_from, user_id_to)\n
    list all friends of an user. 
    """
    cursor = conn.cursor()
    query = f''' SELECT (user_id_to) FROM be_friend WHERE user_id1 = {user_id} '''
    cursor.execute(query)
    friends = cursor.fetchall()
    return friends

# steven do


def getActivity():
    """ get the activity/contribution of an user\n
    Activity = number of photos uploaded by the user + number of comments by the user
    """
    cursor = conn.cursor()
    pass

# steven do


def getAllPhotos():
    """ get all photos on the website.\n
    ***We assume all photos are *public* """
    pass

# steven do


def createAlbum():
    """ Creates an album """
    pass


def createTag(word):
    """ 
    Input: (string) word of a tag.\n
    Output: None\n
    Creates a tag """
    cursor = conn.cursor()
    query = f"INSERT INTO Tags (word) VALUES ('{word}')"
    cursor.execute(query)
    conn.commit()


def addTagToPhoto(word, photo_id):
    """ associates a tag with a photo """
    cursor = conn.cursor()
    query = f"INSERT INTO associate (photo_id, word) VALUES ('{photo_id}', '{word}')"
    cursor.execute(query)
    conn.commit()


def viewAllPhotoByTag(tag):
    """ 
    Input: (str) tag of a photo.\n
    Output: a list of photo tuples (photo_id, imgdata, caption)\n
    Exhibit all photos of a certain tag
    """
    cursor = conn.cursor()
    query = f"SELECT associate.photo_id, Photos.imgdata, Photos.caption FROM Photos, associate WHERE word = '{tag}'"
    cursor.execute(query)
    photos = cursor.fetchall()
    return photos


def viewUserPhotoByTag(user_id, tag):
    """ 
    Input: (int) user_id of user.\n
    (str) tag of a photo.\n
    Output: a list of photo tuples (photo_id, imgdata, caption)\n
    Exhibit all photos of a certain tag of one user
    """
    cursor = conn.cursor()
    query = f"SELECT photo_id FROM(SELECT associate.photo_id, Photos.user_id,\
             Photos.caption FROM Photos, associate WHERE word='{tag}') as x WHERE x.user_id = {user_id}"
    cursor.execute(query)
    photos = cursor.fetchall()
    return photos


def viewMostPopularTags():
    """ List the most popular three tags, i.e., the three tags 
        that are associated with the largest number of photos, in descending
        popularity order."""
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT word FROM (SELECT word, COUNT(photo_id) FROM associate GROUP BY word ORDER BY COUNT(photo_id) DESC LIMIT 3) as x")
    tags = cursor.fetchall()
    return tags


def searchByTags():
    """ search by a list of tags.For example, a visitor could enter the words "friends boston" in an input box, click 
    the search button, and be presented with all photos that contain both the tag "friends" and the tag "boston". """
    pass

# steven do


def leaveComment():
    """ user leaves a comment. 
    NOTE: Users cannot leave a comment own their own photo.
    """
    pass

# steven do


def likePhoto():
    """ user likes a photo """
    pass

# steven do


def searchUsersOnComment():
    """ find the users that have created comments that exactly match the 
    input query text. Return the names of these users ordered by the number of comments that match the query 
    in descending order. """
    pass


def friendRecommendation():
    """ recommend potential friends of a user. """
    pass


def photoRecommendation():
    """ recommend photos that one user may like """
    pass

# default page


@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
