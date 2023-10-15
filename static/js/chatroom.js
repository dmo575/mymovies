/* handles chatroom.hml logic */

// instance of socketio that we will use to stablish a connection with the server
// to send and receive data
socket = io();

document.addEventListener('DOMContentLoaded', function() {

    // the parent where the chat logs should go in the HTML doc
    chat_box = document.getElementById('chat_box');

    // users text box in the chatroom
    chat_prompt = document.getElementById('chat_prompt');

    // this method will connect the client with the server
    socket.connect();

    // now we need to define the callback functions we want for
    // our needs with the chatroom:

    // this is telling the client to listen for an event of the name
    // latest_log from the server
    socket.on('latest_log', function(data) {
        update_chatroom(data);
    });

    chat_prompt.addEventListener('keydown', function(event) {

        // whenever the user sends a chat message:
        if(event.key === 'Enter' && chat_prompt.value != '') {

            // create an object with the data
            let chat_data = {msg: chat_prompt.value};

            // clear chat text box
            chat_prompt.value = '';

            // send the message to the server
            socket.emit("chatroom_msg", chat_data);
        }
    });
});

// this will update the chatroom container with the latest chat messages
function update_chatroom(data) {

    // parse the data (it comes as a JSON from the server)
    chat_log = JSON.parse(data);

    // clear the message box
    chat_box.innerHTML = '';

    // repopulate it with the latest message data we just got from the server
    for(let i = chat_log.log.length - 1; i >= 0; i--) {

        chat_box.innerHTML += '<p class="chat_msg"><u class="chat_username">' + chat_log.log[i].username + '</u>: '+ chat_log.log[i].message + '</p>';
    }
}