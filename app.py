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
app.config['MYSQL_DATABASE_PASSWORD'] = 'zhuceyezi'              # change this
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


def getCurrentUserId():
    return getUserIdFromEmail(flask_login.current_user.id)


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

# steven done


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
    return render_template('gallery.html', photos=photos, base64=base64)


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
    return render_template('album_gallery.html', albums=albums)


def getUserNameFromId(user_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT first_name, last_name FROM Users WHERE user_id = {user_id}")
    conn.commit()
    return cursor.fetchone()[0]


# steven do
"""  The fucntion below is not needed since it already be done at line 130 ~ 146
 def createAlbum():
    pass
"""


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


def unassociateTag(word, photo_id):
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM associate WHERE photo_id = '{photo_id}' AND word = '{word}'")
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


# steven done
@app.route("/photos/<int:photo_id>/comments", methods=['POST'])
def leaveComment(photo_id):
    """ 
    input: (int) photo_id of a photo that user is comment on.\n
    Output: None\n

    user leaves a comment. 
    NOTE: Users cannot leave a comment own their own photo.

    """
    user_id = request.form.get('user_id')       # get the user_id from the form
    comment = request.form.get('comment')

    cursor = conn.cursor()
    # check if the user is the owner of the photo
    check = f"SELECT user_id FROM Photos WHERE photo_id = {photo_id}"
    cursor.execute(check)
    owner = cursor.fetchone()[0]            # get the owner of the photo
    if owner == user_id:        # if the user is the owner of the photo, return error message
        return "You cannot leave a comment on your own photo.", 400

    # else insert the comment into the database
    # insert the comment into the database
    insert = f"INSERT INTO Comments (photo_id, user_id, comment) VALUES ({photo_id}, {user_id}, '{comment}')"
    cursor.execute(insert)
    conn.commit()  # commit changes made to the database
    cursor.close()
    return "Comment left successfully.", 201    # return success message


# steven done
@app.route("/like/<int:photo_id>", methods=['POST'])
def likePhoto(photo_id):
    """ 
    Input: (int) photo_id \n
    Output: JSON object indicating whether the like action was successful or not.\n

    user likes a photo 
    """
    user_id = request.form.get('user_id')       # get the user_id from the form
    if user_id is None:
        return jsonify({'error': 'User ID is required to like a photo'}), 400

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Photos WHERE photo_id = %s",
                   (photo_id,))   # check if the photo exists
    photo = cursor.fetchone()          # get the photo
    if photo is None:               # if the photo does not exist, return error message
        return jsonify({'error': 'Photo not found'}), 404

    # if the user is the owner of the photo, return error message
    if photo['user_id'] == user_id:
        return jsonify({'error': "Users cannot like their own photo"}), 400

    cursor.execute("INSERT INTO Likes (user_id, photo_id) VALUES (%s, %s)",
                   (user_id, photo_id))  # insert the like into the database
    conn.commit()                       # commit changes made to the database
    cursor.close()                      # close the cursor

    # return success message
    return jsonify({'message': 'Photo liked successfully'}), 201


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
        WHERE c.content LIKE %s                         # use place holder to avoid sql injection
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
            u.user_id, u.first_name, u.last_name,
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
def getPhotosFromAlbum():
    album_id = request.args.get("album_id")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT imgdata, photo_id, caption FROM Photos WHERE album_id='{album_id}'")
    conn.commit()
    photos = cursor.fetchall()
    cursor.execute(f"SELECT album_name FROM Albums WHERE album_id={album_id}")
    album_name = cursor.fetchone()[0]
    return render_template('open_album.html', album_name=album_name, photos=photos, base64=base64)
# default page


@app.route('/view_albums', methods=['GET'])
@flask_login.login_required
def getUserAlbums():
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
    return render_template('view_albums.html', albums=albums)


@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
