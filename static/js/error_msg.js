/* prints error messages */

//Adds an error to the page's error error log
function add_error(msg_content) {
    let errors_list = document.getElementById('error_log');

    if(errors_list.innerHTML.length == 0) {
        errors_list.innerHTML = 'Please fix the following:';
    }

    errors_list.innerHTML += ('<li>' + msg_content + '</li>');
}

//Clears the errors from the page's error log
function clear_error_history() {
    document.getElementById('error_log').innerHTML = '';
}