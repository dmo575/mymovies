# Flask configuration lines I copied from assignment 9
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, abort, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import re
from datetime import datetime
from flask_socketio import SocketIO, emit

############################################################################# CONFIG
############################################################################# CONFIG

# max amnt of latest msgs we will save in our database
chatroom_data_cap = 1000
# max amnt of latest msgs that we will send to the clients
chatroom_history_cap = 15

# configure application (cs50 asignment 9)
app = Flask(__name__)

# configure session to use filesystem (instead of signed cookies) (cs50 asignment 9)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuring socketio
socketio = SocketIO(app)

if __name__ == "__main__":
    socketio.run(app, debug=true)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///server.db")

# cs50 assigmnent 9 configuration code
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


############################################################################# ROUTES
############################################################################# ROUTES

# render index if user logged in, else take to login
@app.route("/")
def index():
    id = session.get("id")

    if id:
        return render_template("index.html")

    return redirect("/login")

# render mymovies if user logged in, else take to index
@app.route("/mymovies")
def mymovies():
    id = session.get("id")

    if id:
        return render_template("mymovies.html")

    return redirect("/login")


# render login if user NOT logged in, else take to index
@app.route("/login")
def log_in():
    id = session.get("id")

    if id:
        return redirect("/")

    return render_template("login.html")

# log out and take user to login
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# render register if user NOT logged in, else take to index
@app.route("/register")
def register():
    id = session.get("id")

    if id:
        return redirect("/")

    return render_template("register.html")

# render chatroom if user logged in, else take to index
@app.route("/chatroom")
def chatroom():
    id = session.get("id")

    if id is None:
        return redirect("/")

    return render_template("chatroom.html")

# render chatroom if user logged in, else take to index
@app.route("/account")
def account():
    id = session.get("id")

    if id is None:
        return redirect("/")

    return render_template("account.html")

# removes an account and its related data from the server
@app.route("/deleteaccount")
def delete_account():
    id = session.get("id")

    if id is None:
        return redirect("/")

    db.execute("DELETE FROM user_movies WHERE user_id = ?;", id)
    db.execute("DELETE FROM users WHERE id = ?;", id)

    session.clear()
    return redirect("/login")


############################################################################# API/XML
############################################################################# API/XML


# clears all movies from an account
@app.route("/clearmovies")
def clear_movies():
    id = session.get("id")

    if id is None:
        return redirect("/")

    db.execute("DELETE FROM user_movies WHERE user_id = ?;", id)


    return '0'


# given a title and an optional filter, returns a list of titles that match the
# beforementioned arguments for the signed in user as a json string
@app.route("/search_user_movies")
def search_user_movies():
    id = session.get("id")

    # checks
    if  id is None:
        abort(400, "ERROR: Must be logged in to have access.")

    # gather data
    title = request.args.get("title")
    filter = request.args.get("filter")

    # data validation
    if title is None:
        abort(400, "ERROR: No user_query found in the GET request.")

    # obtain the user movies based on the filter
    # the SQL query changes a bit depending on the filter so we separa it like this
    if filter is None:
        user_movies = db.execute("SELECT * FROM movies JOIN user_movies ON movies.id = user_movies.movie_id WHERE user_id = ? AND (title LIKE ? OR curated_title LIKE ?) ORDER BY movies.title;", id, "%" + title + "%", "%" + title + "%")
    elif filter == "fav":
        user_movies = db.execute("SELECT * FROM movies JOIN user_movies ON movies.id = user_movies.movie_id WHERE user_id = ? AND (title LIKE ? OR curated_title LIKE ?) AND fav = 1 ORDER BY movies.title;", id, "%" + title + "%", "%" + title + "%")
    elif filter == "pen":
        user_movies = db.execute("SELECT * FROM movies JOIN user_movies ON movies.id = user_movies.movie_id WHERE user_id = ? AND (title LIKE ? OR curated_title LIKE ?) AND pen = 1 ORDER BY movies.title;", id, "%" + title + "%", "%" + title + "%")
    elif filter == "saw":
        user_movies = db.execute("SELECT * FROM movies JOIN user_movies ON movies.id = user_movies.movie_id WHERE user_id = ? AND (title LIKE ? OR curated_title LIKE ?) AND (saw = 1 OR fav = 1) ORDER BY movies.title;", id, "%" + title + "%", "%" + title + "%")

    # create json string
    json_string = '{"results":['
    if len(user_movies) > 0:
        for movie in user_movies:
            json_string += '{"title":"' + movie["title"] \
            + '","description":"' + movie["description"] \
            + '","image":"' + movie["image"] \
            + '","fav":' + str(movie["fav"]) \
            + ',"pen":' + str(movie["pen"]) \
            + ',"saw":' + str(movie["saw"]) \
            + ',"id":"' + str(movie["id"]) + '"},'

        json_string = json_string[:len(json_string) - 1]

    json_string += ']}'

    return json_string


# given movie data and the fps button pressed it updates the movies database and the
# user's button state. Returns the new value for the specified button as a string
# required json:
# {"button":"button type (fav, pen, saw)",
# "movie_id":"movie id",
# "movie_desc":"movie description",
# "movie_title":"movie title",
# "movie_img":"movie image"}
# returns: 0 or 1 as a string
@app.route("/update_user_movies", methods=["POST"])
def update_user_movies():
    id = session.get("id")

    # checks
    if  id is None:
        abort(400, "ERROR: Must be logged in to have access.")

    if request.method == "GET":
        abort(400, "ERROR: Only POST requests accepted.")

    # get data
    post_data = request.get_json()
    movie_id = post_data.get("movie_id")
    button = post_data.get("button")
    title = post_data.get("movie_title")
    desc = post_data.get("movie_desc")
    img = post_data.get("movie_img")

    # data validation
    if movie_id is None or button is None or title is None:
        abort(400, "ERROR: No btn or movie_id provided in the request.")

    # check if the movie already exists in movies, if not, add it
    movie = db.execute("SELECT * FROM movies WHERE id = ?;", movie_id)
    if len(movie) == 0:
        # get the lowecase version of the title
        curated_title = title
        curated_title = curated_title.lower()
        title_chars = []

        # get a list with all the special characters the title has
        for lt in curated_title:
            if lt < "a" or lt > "z":
                title_chars.append(lt)

        # go over that list and use it to run re.sub, this way we get rid of them
        for ch in title_chars:
            curated_title = re.sub(ch, '', curated_title)

        db.execute("INSERT INTO movies (id, title, curated_title, image, description) VALUES (?, ?, ?, ?, ?);", movie_id, title, curated_title, img, desc)

    # get user_movie data
    user_movie_data = db.execute("SELECT * FROM user_movies WHERE movie_id = ? AND user_id = ?;", movie_id, id)

    # if no user_movie data, create a row with default fps values (-1)
    if len(user_movie_data) == 0:
        db.execute("INSERT INTO user_movies (user_id, movie_id, fav, pen, saw) VALUES (?, ?, -1, -1, -1);", id, movie_id)
        fps = [-1, -1, -1]
    else:
        fps = [user_movie_data[0]["fav"], user_movie_data[0]["pen"], user_movie_data[0]["saw"]]

    # get new fps values
    print("11111 - fps values obtained from TABLE: " + str(fps[0]) + ", " + str(fps[1]) + ", " + str(fps[2]))
    fps = get_new_buttons(fps, button)
    print("22222 - NEW fps values: " + str(fps[0]) + ", " + str(fps[1]) + ", " + str(fps[2]))

    if fps[0] == -1 and fps[1] == -1 and fps[2] == -1:
        # if new fps values are all -1, delete movies_data row and check how many
        # other users have this movie in their data
        db.execute("DELETE FROM user_movies WHERE user_id = ? AND movie_id = ?;", id, movie_id)

        movie_subs = db.execute("SELECT COUNT(*) AS count FROM user_movies WHERE movie_id = ?;", movie_id)

        # if no other users have this movie in their data, delete movie
        if movie_subs[0]["count"] == 0:
            db.execute("DELETE FROM movies WHERE id = ?;", movie_id)
    else:
        # if new fps values are NOT all -1, update movie_userts row with them
        db.execute("UPDATE user_movies SET fav = ?, pen = ?, saw = ? WHERE user_id = ? AND movie_id = ?;", fps[0], fps[1], fps[2], id, movie_id)


    print(fps)
    return '{"fav":"' + str(fps[0]) + '","pen":"' + str(fps[1]) + '","saw":"' + str(fps[2]) + '"}'

# given current values for FAV PEN SAW buttons and the pressed button, returns the new values for it.
def get_new_buttons(fps, btn):

    if btn == "fav":
        fps[0] *= -1
        if fps[0] == 1:
            fps[1] = -1
            fps[2] = 1
    elif btn == "pen":
        fps[1] *= -1
        if fps[1] == 1:
            fps[2] = -1
            fps[0] = -1
    else:
        fps[2] *= -1
        if fps[2] == 1:
            fps[1] = -1
        else:
            fps[0] = -1

    return fps



# given (username, password1, password2) validates data and sends an error list back as a JSON STRING.
# {"errors":["error1", "error2", ...]}
@app.route("/try_register", methods=["POST"])
def check_register():
    id = session.get("id")

    # checks
    if id:
        return abort(400, "Error, user should not be logged in.")

    if request.method == "GET":
        return abort(400, "Error, only POST allowed.")

    # gather data
    json_data = request.get_json()
    username = json_data.get("username")
    password1 = json_data.get("password1")
    password2 = json_data.get("password2")
    errors = []

    # validate data
    if username is None or len(username) < 4:
        errors.append("Username length must be greater than 3.")
    if password1 is None or password2 is None:
        errors.append("One or the two password fields are empty.")
    if password1 != password2:
        errors.append("Passwords do not match.")
    if len(password1) < 8:
        errors.append("The password length must be greater than 7.")

    username_taken = db.execute("SELECT username FROM users WHERE username = ?", username)

    if len(username_taken) > 0:
        errors.append("This username is already taken.")

    # if no errors, register user
    if len(errors) == 0:
        hash = generate_password_hash(password1)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        session.clear()
        session["id"] = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]


    # create errors json
    json_string = '{"errors":['

    if len(errors) > 0:
        for e in errors:
            json_string += '"' + e + '",'

        json_string = json_string[:len(json_string) - 1]

    json_string += ']}'

    return json_string


# given (username, password) validates data and sends an error list back as a JSON STRING.
# {"errors":["error1", "error2", ...]}
@app.route("/try_login", methods=["POST"])
def check_login():
    id = session.get("id")

    # checks
    if id:
        return abort(400, "Error, user should not be logged in.")

    if request.method == "GET":
        return abort(400, "Error, only POST allowed.")

    # gather data
    json_data = request.get_json()
    username = json_data.get("username")
    password = json_data.get("password")
    errors = []

    # validate data
    # client handles empty fields but just in case ill be checked out here too
    if username is None or password is None:
        return '{"errors":["Please fill out all fields."]}'

    user_data = db.execute("SELECT * FROM users WHERE username = ?", username)

    invalid_credentials = False
    if len(user_data) == 0:
        invalid_credentials = True
    else:
        hash = user_data[0]["hash"]
        if check_password_hash(hash, password) is False:
            invalid_credentials = True

    # we obscure which of the two (username, password) failed. Even tho you can check a username with register
    if invalid_credentials:
        errors.append("Invalid credentials.")

    # if no errors, log in user
    if len(errors) == 0:
        session.clear()
        session["id"] = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # create errors json
    json_string = '{"errors":['

    if len(errors) > 0:
        for e in errors:
            json_string += '"' + e + '",'

        json_string = json_string[:len(json_string) - 1]

    json_string += ']}'

    return json_string


# debug
@app.route("/fakeapi")
def fakeapi():
    return '{"searchType":"Movie","expression":"tetris","results":[{"id":"0","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZmZmNTdiYjMtZDdmNi00ZGU4LThkYmQtZTFhZWNlYmUxYWZkXkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_Ratio0.6757_AL_.jpg","title":"Tetris","description":"2023 Taron Egerton, Mara Huf"},{"id":"tt24222834","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BOTc1MjY1NjktZWJhMi00MjJmLTk4YTUtNzY3ODJmNmE1ZGY0XkEyXkFqcGdeQXVyMDMyOTIyMQ@@._V1_Ratio0.6757_AL_.jpg","title":"The Tetris Murders","description":"2022– TV Series Brandon Tyler Moore, Rebecca Ray"},{"id":"tt5452216","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BOWIzYWM3ZjgtNzQwMC00Y2IwLTkxNTAtZTNkNTNlYmEzMjBhL2ltYWdlL2ltYWdlXkEyXkFqcGdeQXVyNzAxNzQ2NDE@._V1_Ratio1.7838_AL_.jpg","title":"Tetris","description":"2016 Short Anaís Furtado, Hendrik Maaß"},{"id":"tt1543151","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZDVlNjc1MTQtNmM0Ny00NjBiLWFmOWEtYzI5ZjQyZGQyZWMxXkEyXkFqcGdeQXVyMTE4MjgzNDY2._V1_Ratio0.8108_AL_.jpg","title":"Tetris","description":"2007–2009 TV Series Luca Telese"},{"id":"tt0207153","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZjA5OGMxNGQtNzhiOS00MjRkLWFjY2UtOWEzMWUzMjhmOWVlXkEyXkFqcGdeQXVyMTA0MTM5NjI2._V1_Ratio0.6757_AL_.jpg","title":"Tetris","description":"1984 Video Game"},{"id":"tt0409371","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZjkzNDE1ZmQtOWE5NC00YjUwLTk0MWItZjFkMDFhNDUxMGQxXkEyXkFqcGdeQXVyNTk1MjA5MjM@._V1_Ratio1.7838_AL_.jpg","title":"Tetris: From Russia with Love","description":"2004 TV Movie Phil Adam, Evgeni Nikolaevich Belikov"},{"id":"tt1764634","resultType":"Movie","image":"","title":"Tetris","description":"2010 Mirko Radic"},{"id":"tt11859948","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BOGQyNjE3MTEtNWZhMy00MjIwLTk4NzUtNWRkMzhmYWIzYWYyXkEyXkFqcGdeQXVyMTA0MTM5NjI2._V1_Ratio0.6757_AL_.jpg","title":"Tetris","description":"1988 Video Game"},{"id":"tt1836974","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BMTkwNTY0MDg3NV5BMl5BanBnXkFtZTcwNTQwMzI5Nw@@._V1_Ratio0.7027_AL_.jpg","title":"Ecstasy of Order: The Tetris Masters","description":"2011 Thor Aackerlund, Pat Contri"},{"id":"tt5843888","resultType":"Movie","image":"","title":"Tetris 3","description":""},{"id":"tt5843886","resultType":"Movie","image":"","title":"Tetris 2","description":""},{"id":"tt17397080","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZmRlMmVmMTMtZmRiYy00NzJjLTkwMDYtOWVjODU0OTZiYjI4XkEyXkFqcGdeQXVyMTA0MjI3Mzk4._V1_Ratio0.6757_AL_.jpg","title":"Nintendo: Tetris Effect Connected","description":"2021 Video Lileina Joy"},{"id":"tt4104020","resultType":"Movie","image":"","title":"Untitled Tetris Sci-fi Project","description":""},{"id":"tt8716570","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BODVhZTk5M2QtNWRkNy00MGM0LWJlNzEtNGJiNzY2M2ZlZmM0XkEyXkFqcGdeQXVyMjAyOTI3Njc@._V1_Ratio1.6757_AL_.jpg","title":"Tetris","description":"2006 Short Angshuman Chakrabarty, Anirban Datta"},{"id":"tt9159428","resultType":"Movie","image":"","title":"Tetris Effect","description":"2018 Video Cashmir Khawaja, Joel Linden"},{"id":"tt3874224","resultType":"Movie","image":"","title":"Tetris Commercial","description":"1989 TV Short"},{"id":"tt25406106","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BNjBhYjI4MzQtZTQ1YS00ZDczLWI1ZTYtYzVhMDdiODMyMDAyXkEyXkFqcGdeQXVyMjY2ODczNg@@._V1_Ratio1.0270_AL_.jpg","title":"Tetris 4D","description":"1998 Video Game"},{"id":"tt5907808","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZjRkZjQzOTctODFiMC00YjZiLWFhOTUtODJmNzY2N2Q4ZGY3L2ltYWdlXkEyXkFqcGdeQXVyNjM2NDIwMzQ@._V1_Ratio0.8649_AL_.jpg","title":"Puyo Puyo Tetris","description":"2014 Video Game Kira Buckland, Christine Marie Cabanos"},{"id":"tt8495686","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZWU3N2VkNWUtZDI0MC00Y2E1LWJiMjYtYjM0NThhMTRhODNiXkEyXkFqcGdeQXVyNTk2MTgzNjk@._V1_Ratio1.5946_AL_.jpg","title":"Tetris","description":"2017 Short Carmen Annibale, Daniela Camera"},{"id":"tt13082960","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BM2U3OTU5Y2MtNzcwYy00MmI2LWE4YjgtNjYwMjMxY2U1OWRmXkEyXkFqcGdeQXVyODE1OTI0Mjg@._V1_Ratio0.6757_AL_.jpg","title":"Puyo Puyo Tetris 2","description":"2020 Video Game Kira Buckland, Christine Marie Cabanos"},{"id":"tt5459538","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BN2RjNmZlYzYtYjgzYS00ODcyLThjNWQtMTZkZjAzN2IyMmZmXkEyXkFqcGdeQXVyMTgwOTE5NDk@._V1_Ratio1.3784_AL_.jpg","title":"Magical Tetris Challenge","description":"1998 Video Game Wayne Allwine, Tony Anselmo"},{"id":"tt19770150","resultType":"Movie","image":"","title":"Tetris","description":"2003 Music Video The Basement"},{"id":"tt5232628","resultType":"Movie","image":"","title":"Untitled Tetris/Biopic Project","description":""},{"id":"tt0293642","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BZjEyODRhYjYtYTcwZC00Mzg1LWI2ZDktNGJiMzMzZmJjMGNkXkEyXkFqcGdeQXVyNjExODE1MDc@._V1_Ratio0.7027_AL_.jpg","title":"Tetris Worlds","description":"2001 Video Game Kimberly Unger, Leslie Hedger"},{"id":"tt9222458","resultType":"Movie","image":"https://m.media-amazon.com/images/M/MV5BYjU1YjNjOGItYjcwNy00MzQxLWE4N2EtNjg4MTZkOTdhNDkyXkEyXkFqcGdeQXVyMTA0MTM5NjI2._V1_Ratio0.6757_AL_.jpg","title":"Tetris Effect","description":"2018 Video Game"}],"errorMessage":""}'


############################################################################# socketio
############################################################################# socketio


# handles the connect event sent from the client
# occurs when the client connects
@socketio.on("connect")
def handle_connect():
    socketio.emit("latest_log", get_latest_chatroom_data())


# handles the disconnect event sent from the client
# occurs when the client disconnects
@socketio.on("disconnect")
def handle_disconnect():
    return "disconnected."


# handles the chatroom_msh event sent from the client
# occurs when the client wants to send a message to the chatroom
# server will update chatroom and send latest messages to connected clients
@socketio.on("chatroom_msg")
def handle_chatroom_msg(data):
    id = session.get("id")

    # checks
    if id is None:
        return redirect("/")

    # get data
    message = data["msg"]

    # data validation
    if message is None or message == '':
        return "No message found."

    # get data about the client
    username = db.execute("SELECT username FROM users WHERE id = ?;", id)[0]["username"]
    time = datetime.now().time()

    # Update chatroom table
    db.execute("INSERT INTO chatroom (username, message, date) VALUES (?, ?, ?);", username, message, time)

    # get amnt of chats stored in db
    log_count = db.execute("SELECT COUNT(*) AS count FROM chatroom;")[0]["count"]

    # delete if the amnt exceed maximum stablished
    if log_count > chatroom_data_cap:
        db.execute("DELETE FROM chatroom ORDER BY id LIMIT 1;")

    # send latest chatroom messages to all connected clients
    socketio.emit("latest_log", get_latest_chatroom_data())


# returns the latest chatroom messages
def get_latest_chatroom_data():

    # gets the latest chatroom messages accounting for the maximum stablished to send
    # to clients
    # we separate the statement on its own variable due to a limitation with the execute function
    chatroom_history_execute = "SELECT * FROM chatroom ORDER BY id DESC LIMIT " + str(chatroom_history_cap) + ";"
    history_data = db.execute(chatroom_history_execute)

    # build json string

    messages = '{"log":['

    for msg in history_data:
        messages +='{"username":"' + msg["username"] + '",' + \
        '"message":"' + msg["message"] + '",' + \
        '"time":"' + msg["date"] + '"},'

    messages = messages[:len(messages) - 1] + ']}'

    return messages
