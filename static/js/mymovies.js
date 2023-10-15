/* handles mymovies.html logic */

// keeps track of the latest value inside the search box
global_latest_query = '';

// called when a search is finished, arguments is an array of objects
// containing the movies
function on_search_finished(data) {

    // if the query used for this search is not the latest query, then we skip it
    if(data.query != global_latest_query) {
        return;
    }

    // clear movies container
    parent = document.getElementById('results_container');
    parent.innerHTML = '';

    // for each movie, add it to the html and update the buttons (fav, pen, saw)
    for(let i = 0; i < data.movies.length; i++) {
        let search_item = add_search_item(parent, data.movies[i].title, data.movies[i].description, data.movies[i].image, data.movies[i].id);
        let fps = [data.movies[i].fav, data.movies[i].pen, data.movies[i].saw];

        update_fps_button_colors([search_item.querySelector('#btn_fav'),
        search_item.querySelector('#btn_pen'),
        search_item.querySelector('#btn_saw')],
        fps);
    }
}

document.addEventListener('DOMContentLoaded', function() {

    // variables
    let parent = document.getElementById('results_container');
    let filter_bar = document.getElementById('search_filter');
    let search_bar = document.getElementById('search_bar');

    //Register callback functions for CLICK (search btn) or ENTER (key press)
    document.addEventListener('keyup', function(event) {

        if((event.key > 'A' && event.key < 'Z') || (event.key > 'a' && event.key < 'z')) {
            ajax_search(parent, search_bar, filter_bar);
        }
    });

    document.getElementById('search_filter').addEventListener('change', function(event) {
        ajax_search(parent, search_bar, filter_bar);
    });

    // call ajax_search to show something initially on the page
    ajax_search(parent, search_bar, filter_bar);
});

// its a wrapper function that helps keep the code above a bit more clean
function ajax_search(parent, search_bar, filter_bar) {

    // clear container
    parent.innerHTML = '';
    global_latest_query = search_bar.value;

    // start search
    search_db(search_bar.value, on_search_finished, '', filter_bar.value);
}
