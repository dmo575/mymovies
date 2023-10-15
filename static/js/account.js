/* handles account.html logic */

document.addEventListener('DOMContentLoaded', function() {

    let dialog = document.getElementById('options_dialog');
    let button_clear_movies = document.getElementById('button_clear_movies');
    let button_delete_account = document.getElementById('button_delete_account');
    let button_yes = document.getElementById('button_yes');
    let button_no = document.getElementById('button_no');

    // clear movies button click, open modal
    button_clear_movies.addEventListener('click', function() {
        dialog.showModal();
        button_yes.onclick = clear_movies;
    });

    // clear movies button click, open modal
    button_delete_account.addEventListener('click', function() {
        dialog.showModal();
        button_yes.onclick = delete_account;
    });
});

// called when we press yes for clearing movies, sends a XML request to perform the action
function clear_movies() {
    document.getElementById('processing_dialog').showModal();

    let xml = new XMLHttpRequest();

    xml.open('GET', '/clearmovies');

    xml.onreadystatechange = function() {

        if(xml.readyState == XMLHttpRequest.DONE && xml.status == 200) {

            document.getElementById('processing_dialog').close();
            document.getElementById('options_dialog').close();
        }
    }

    xml.send();
}

// called when we press yes for deleting the account
function delete_account() {
    document.getElementById('processing_dialog').showModal();

    window.location.href = '/deleteaccount';
}

function close_options_modal(modal) {
    modal.close();
}