/* handles the registration form logic (from register.html) */

global_registering = false;

document.addEventListener('DOMContentLoaded', function() {

    // get register button
    let register_button = document.getElementById('register_button');

    // callback when register button clicked:
    // *stops the form
    // *sends XML to validate data
    // *if data is good send the form, else print errors to user
    register_button.addEventListener('click',function(event){

        try_register(register_button);
    });

    document.addEventListener('keydown', function(event) {

        if(!global_registering && event.key == 'Enter') {

            try_register(register_button);
        }
    });
});

function try_register(button) {

    // disable button
    button.disabled = true;
    global_registering = true;

    // get page data
    let username = document.getElementById('register_username').value;
    let password1 = document.getElementById('register_password1').value;
    let password2 = document.getElementById('register_password2').value;

    // client side data validation
    if(username.length == 0 || password1.length == 0 ||
        password2.length == 0) {

        clear_error_history();
        add_error('Please fill out all fields.');
        button.disabled = false;
        global_registering = false;
        return;
    }

    // set up XML http request
    let xml = new XMLHttpRequest();

    xml.open('POST', '/try_register');
    xml.setRequestHeader('Content-Type', 'application/json');

    let data_to_send = {
        username: username,
        password1: password1,
        password2: password2
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
                global_registering = false;
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