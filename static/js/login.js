/* handles the login form logic (from login.html) */

global_logging_in = false;

document.addEventListener('DOMContentLoaded', function() {

    // get login button
    let login_button = document.getElementById('login_button');

    // callback when login button clicked:
    // *stops the form
    // *sends XML to validate data
    // *if data is good send the form, else print errors to user
    login_button.addEventListener('click',function(event){

        try_login(login_button);
    });

    document.addEventListener('keydown', function(event) {

        if(event.key == 'Enter' && !global_logging_in) {
            try_login(login_button);
        }
    });
});

function try_login(button) {

    // disable button
    button.disabled = true;
    global_logging_in = true;

    // get page data
    let username = document.getElementById('login_username').value;
    let password = document.getElementById('login_password').value;

    // client side data validation
    if(username.length == 0 || password.length == 0) {

        clear_error_history();
        add_error('Please fill out all fields.');
        button.disabled = false;
        global_logging_in = false;
        return;
    }

    // set up XML http request
    let xml = new XMLHttpRequest();

    xml.open('POST', '/try_login');
    xml.setRequestHeader('Content-Type', 'application/json');

    let data_to_send = {
        username: username,
        password: password
    };

    xml.onreadystatechange = function() {

        // if everything went OK
        if(xml.readyState == XMLHttpRequest.DONE && xml.status == 200) {

            let errors = JSON.parse(xml.responseText);

            // if server data validation found errors then print them
            if(errors.errors.length > 0) {

                clear_error_history();

                for(let i = 0; i < errors.errors.length; i++) {
                    add_error(errors.errors[i]);
                }

                button.disabled = false;
                global_logging_in = false;
            }
            else {
                // go to index
                window.location.href = '/';
            }
        }
        // if something went wrong
        else if(xml.status != 200) {
            clear_error_history();
            add_error("Someting went wrong. Please refresh the page and try again.");
        }
    }

    xml.send(JSON.stringify(data_to_send));
}