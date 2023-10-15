/* handles index.html logic */

// called when a search is finished, arguments is an array of objects
// containing the movies
function on_search_finished(data) {

    // get searchitem container
    let parent = document.getElementById('results_container');

    // enable button and ENTER key for search again
    document.getElementById('search_button').disabled  = false;
    document.getElementById('search_bar').disabled = false;

    // clear the movies container from all placeholders
    parent.innerHTML = '';

    // for each movie, add it to the html and update the buttons (fav, pen, saw)
    for(let i = 0; i < data.movies.length; i++) {
        let search_item = add_search_item(parent, data.movies[i].title, data.movies[i].description, data.movies[i].image, data.movies[i].id);
        let fps = [data.movies[i].fav, data.movies[i].pen, data.movies[i].saw];

        let buttons = [search_item.querySelector('#btn_fav'),
        search_item.querySelector('#btn_pen'),
        search_item.querySelector('#btn_saw')];

        update_fps_button_colors(buttons, fps);
    }
}

function index_search(parent, search_button, search_bar) {

    // get variables
    let user_query = document.getElementById('search_bar').value;

    // disable search methods (button press and ENTER press)
    search_button.disabled = true;
    search_bar.disabled = true;

    // empty searchitem container
    parent.innerHTML = '';

    // populate searchitem conteiner with placeholders for a visual qeue
    for(let i = 0; i < 5; i++) {
        add_search_item_ph(parent);
    }

    // ask for a search
    search(user_query, on_search_finished);
}

document.addEventListener('DOMContentLoaded', function() {

    let parent = document.getElementById('results_container');
    let search_button = document.getElementById('search_button');
    let search_bar = document.getElementById('search_bar');

    //Register callback functions for CLICK (search btn) or ENTER (key press)
    search_button.addEventListener('click',function(event) { index_search(parent, search_button, search_bar); });

    document.addEventListener('keydown', function(event) {

        if(event.key === 'Enter' && search_bar.value.length > 0)
        {
            index_search(parent, search_button, search_bar);
        }
    });
});