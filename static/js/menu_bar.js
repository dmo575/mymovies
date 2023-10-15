/* handles the menu bar logic (from layout.html) */

document.addEventListener('DOMContentLoaded', function() {

    //get variables
    let settings_button = document.getElementById('button_settings');
    let settings_dialog = document.getElementById('settings_modal');
    let button_close = document.getElementById('settings_close');

    //opens modal on settings btn pressed
    settings_button.addEventListener('click', function() {
        settings_dialog.showModal();
    });

    //closes modal on settings's close btn pressed
    button_close.addEventListener('click', function() {
        settings_dialog.close();
    });
});

function go_to_page(link) {
    window.location.href = link;
}