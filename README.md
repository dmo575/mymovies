# PLEASE NOTE:
This is a copy of my final assignment for CS50. This repo is missing the cs50 python module that I used for this project, which was part of the cloud developer environment that we used in the course.


# MY MOVIES
#### Video Demo:  <https://youtu.be/HkbZu71cfN8>
#### Description:


## Overview:

The project its a web application that tries to be a checklist for movie fans to keep track of their watched (SAW), pending (PEN) and favorite (FAV) movies as well as a place to talk about anything users might want to talk about in a global chat group.

The project uses JavaScript, html and css for the front end and Phython for the back end. For Python I am using the Flask module and for both the front and back end I am using the socketio framework in order to create an open connection within the server and the client so that I can implement the chatroom.

I placed the priority in functionality rather than visual integrity but I made sure to make a responsive design for the page, its navegable in both PC and mobile devices.

## index.html/js/css:

This page is meant to be the home page. If the user is logged in it will show the top menu and a search bar to search movies. If not then the user will be thrown to the login page.

**Please note the search is possible at the moment thanks to an api key I bought from the imdb but it might not be working when tested. It will be active for around a month or two.**

One thing that I think is noticeable is that whenever the user searches for a movie, the results show not only the movies but also the status of them in relation to the user. Meaning that if the user had selected the movie Spider-man as watched and happened to look it up, he/she will find the movie with its watched state updated. This is possible because I keep track of every movie ID related to each user and its state, and when looking up a movie in the index page I look up both the imdb database and my own and then use both of them to come up with the final result.

I also included a placeholder for the search items to show as the search takes place for visual communication.

## login.html/js/css:

This page allows a user to log in onto the page and make use of its features. It performs a mix of client side and server side data validation and it informs the user if any of the data is incorrect.

## register.html/js/css:

Similar to login.html but the data validation is performed in the context of creating a new account.

## mymovies.html/js/css:

At first glance this looks similar to index.html but there are two major differences. The first one is that this allows the user to search for movies that he/she has tagged as favorite, seen or pending. This means that the search is performed exclusively on the project's database. The second difference is that because of the search only involving the project's database, this is a great place to use a faster AJAX search than the one we have implemented on the index.html page (which I believe also classifies as AJAX since its not a full page load either), and so that is implemented.

You will notice these is no search button, the reason is because for every letter typed a search is performed and the list automatically updated. If by any chance the user types too fast, previous XML requests get discarded, they do not affect the list shown, only the latest initiated search will show in the page.

## chatroom.html/js/css:

A chatroom that makes use of the socketio framework.

## layout.html/js/css:

Contains the menu options. It also features an html modal (the settings button)

## account.html/js/css:

Lets the user clear his account data or delete the entire account. Also features html modals.

## error_msg.js:

Contains tools for printing the error messages that appear in the login and register sections of the page. Can be used anywhere but I only make use of them there.

## menu_bar.js:

Contains logic for the menu bar (Settings button mainly)

## searchitem.js:

Contains logic for the movie items that comprise the search results. Allows the user to search both the IMDB-database and the server.



## Database:

These are the tables I have in my database:

`CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, hash TEXT);`

`CREATE TABLE user_movies (user_id INTEGER, movie_id TEXT, fav INTEGER, pen INTEGER, saw INTEGER, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (movie_id) REFERENCES movies(id));`

`CREATE TABLE movies (id TEXT PRIMARY KEY, title TEXT, curated_title TEXT, image TEXT, description TEXT);`

`CREATE TABLE chatroom (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message TEXT, date TEXT);`

### *TABLE users:

Keeps track of users' usernames and hashes (password hashes)

### *TABLE movies:

Keeps track of every movie that any user has tagged as favorite, seen or pending. This database is updated so that only movies that have any of those tags by any of the users are stored here. They do not repeat. They also have a curated_title column, this column is meant to store the name of a movie using only letter. Any special character or number is not stored here. This helps to search movies whenever a user omits its correct name, like typing "spiderman" to look up "Spider-man"

### *TABLE user-movies:

Keeps track of all data related to favorite, seen and pending. This links that data to their corresponding movie and user.

### *TABLE chatroom:

Keeps track of the chat messages. Useful to keep all clients updated in the chatroom. Im storing the latest 1K but Im only sending the latest 15 to the clients. Im letting the message id to keep track of the total, past 1k, so that I can keep track of the total messages ever stored on this table. (This would be not ideal I assume that integer has a maximum but I was sure I was not going to get to 1k on my testing journey)

## Design choices:

Many re-designs happened during the project as I kept on realizing of better ways to implement what I wanted. This usually only happened after the original idea was implemented  or almost completely implemented. I realized  that it would be better to focus on making it functional than perfect because literally each time I had something finished I would look at it and see how comboluted it was and how great it would be to re-do it this other way. One such example had to do with the error messages that the user can find in the register and loggin process:

One thing that I constantly went back and forth with was how to handle and communicate data and issues with the register and login submittion forms.

I started doing all the data validation in the client, but that felt too weak so I also double checked it on the server. I also noticed that my methods meant that I had to keep track of data rules (like how many characters should a username have as a minimum, and such) on both the client and the server, and that meant that updating it on one side forced me to go to the other side and update it as well, so I decided to just use the server since thats the best of the two places to have your data validated because the users cannot mess with it there.

However then I realized that I was putting a couple of unnecessary tasks on the server, because most people do not tamper with client code. So finally I came to my final solution:

-Client will check that fields are not empty. This does not involve data rules so a change on those will not affect this. Another benefit is that for non tempering users that forget to fill some data this will save the server from checking.

-Server will also check if the fields are empty among other things because the server must check everything.

-Server will be the only one checking data with the data rules. This ensures that those rules live in one place only.

-The server will also make sure that if the data is correct, the register or login process is completed at that moment. (The way I was doing it be fore is I was checking for the data via an XML request and then, if the data was validated, I was sending a form. But this means either checking twice in the server or giving an opening for code tampering, so the form will be no more, ill just be an XML request that checks and either returns an error array or completes the registration/login)


Another thing that took a lot of iteration was the three buttons (FAV, PEN, SAW) for Favorite, Pending and Seen. Initially that wasnt part of the plan, the idea was to let the users rate a movie and display both their individual rating and the average rating of all the users in the site. But I could not find a awy to layout the ratings that looked even passable so I decided to just use buttons.

After some brainstorming I decided that they would be the three that are in place now. But once implemented I realized that I could have a movie marked as favorite and unseen at the same time, so I changed how the buttons were stored and updated so that situations like that would not occur.


## References:

I took heavy reference from assignment 9's code when it came to setting up Flask and designing the layout.html.

For the modal I watched this video to get an understanding of it:

https://www.youtube.com/watch?v=ywtkJkxJsdg

For socketio I put together the code based on a lot of research all around the web, two of the most important places were:
https://socket.io/docs/v3/client-installation/index.html

https://stackoverflow.com/questions/11995406/socket-io-referenceerror-io-is-not-defined

The rest consisted on doing further research on topics and elements already covered in class. This involved watching several videos about CSS basics (the box model, flex, etc...), searching html tags and properties and searching for Javascript functions and elements.

## Thanks:

This has been a great course, thank you to everyone that made this course possible !