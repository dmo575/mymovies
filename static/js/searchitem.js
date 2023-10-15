/* handles logic related to search items */

// searches in both the server DB and in IMDB
function search(user_query, callback_func) {

    // construct the API query
    let imdb_query = 'https://imdb-api.com/API/SearchMovie/k_c3h1qnf2/' + user_query;

    // create an XML instance
    let xml = new XMLHttpRequest();

    // open the request
    xml.open('GET', imdb_query);

    // set a function to be called each time the state of the request changes
    xml.onreadystatechange = function () {

        // if the state is DONE and all went OK, search database
        if(xml.readyState === XMLHttpRequest.DONE && xml.status == 200) {

            search_db(user_query, callback_func, xml.responseText);
        }
    }

    xml.send();

    return xml;
}


// searches for movies related to the query in the database
// optionally merges the imdb results with what it finds on the database
function search_db(query, callback_func, imdb_data_string='', filter='') {

    let xml = new XMLHttpRequest();

    // open the request
    if(filter == '') {
        xml.open('GET', '/search_user_movies?title=' + query);
    }
    else {
        xml.open('GET', '/search_user_movies?title=' + query + '&filter=' + filter);
    }


    // set a function to be called each time the state of the request changes
    xml.onreadystatechange = function () {

        // if state DONE and all OK
        if(xml.readyState === XMLHttpRequest.DONE && xml.status == 200) {

            // the data that this function will return
            let data = {
                movies: [],
                query: query
            };

            // if we have movies passed trough the imdb_data_string:
            if(imdb_data_string != '') {

                // parse data from imdb and db
                let imdb_data = JSON.parse(imdb_data_string);
                let db_data = JSON.parse(xml.responseText);

                // for each movie in imdb:
                for(let i = 0; i < imdb_data.results.length; i++) {

                    let title = imdb_data.results[i].title;
                    let desc = imdb_data.results[i].description;
                    let img = imdb_data.results[i].image;
                    let id = imdb_data.results[i].id;
                    let fav = '-1';
                    let pen = '-1';
                    let saw = '-1';

                    // for each movie in the database:
                    for(let x = 0; x < db_data.results.length; x++) {

                        // if the imdb movie appears in the database:
                        if(db_data.results[x].id == imdb_data.results[i].id) {

                            // get FAV PEN SAW data
                            fav = db_data.results[x].fav;
                            pen = db_data.results[x].pen;
                            saw = db_data.results[x].saw;
                            break;
                        }
                    }

                    // populate movies
                    data.movies.push({
                            title: title,
                            description: desc,
                            image: img,
                            id: id,
                            fav: fav,
                            pen: pen,
                            saw: saw
                        });

                }

                callback_func(data);
                return;
            }
            else {

                let db_data = JSON.parse(xml.responseText);

                // for each movie in the db
                for(let i = 0; i < db_data.results.length; i++) {

                    let title = db_data.results[i].title;
                    let desc = db_data.results[i].description;
                    let img = db_data.results[i].image;
                    let id = db_data.results[i].id;
                    let fav = db_data.results[i].fav;
                    let pen = db_data.results[i].pen;
                    let saw = db_data.results[i].saw;

                    // populate movies
                    data.movies.push({
                        title: title,
                        description: desc,
                        image: img,
                        id: id,
                        fav: fav,
                        pen: pen,
                        saw: saw
                    });
                }

                callback_func(data);
                return;
            }
        }
    }

    xml.send();
}


// called when an fps button is clicked, updates db and the button color
function fps_click(button, button_type) {

    let movie_search_item = button.parentNode.parentNode.parentNode;

    // creates an object containing all the data we want to send to the server.
    // this is because we can turn objects onto JSON text and we need that
    // so that we can send it to the server
    let post_data = {
        button: button_type,
        movie_id: movie_search_item.id,
        movie_desc: movie_search_item.querySelector('#info_description').innerHTML,
        movie_title: movie_search_item.querySelector('#info_title').innerHTML,
        movie_img: movie_search_item.querySelector('#item_img').src
    };

    // create a JSON string version of the object
    post_data_json = JSON.stringify(post_data);

    //http request object instance
    let xml = new XMLHttpRequest();

    // we open a request of type POST because we will send a lot of information to the server
    // and data sent via the url has a limit
    xml.open('POST', '/update_user_movies');

    xml.onreadystatechange = function() {

        // if all went well, change button color
        if(xml.readyState === XMLHttpRequest.DONE && xml.status == 200) {

            let data = JSON.parse(xml.responseText);

            let fps = [data['fav'], data['pen'], data['saw']];

            update_fps_button_colors([button.parentNode.querySelector('#btn_fav'),
            button.parentNode.querySelector('#btn_pen'),
            button.parentNode.querySelector('#btn_saw')],
             fps);
        }
        // else log the error on the browser's console
        else if (xml.status == 400) {
            console.log(xml.responseText);
        }
    }

    // here we are changing the content-type property of the header to say that the data we are
    // sending is a json file. This is required else we will get a 415 error from the server.
    xml.setRequestHeader('Content-Type', 'application/json');

    // ee then call the send method, which initates the request and as a parameter accepts the
    // json data we want to send
    xml.send(post_data_json);
}

// updates the color of a fps button given itself and the new state
function update_fps_button_color(button, button_type, state) {

    if(state == '-1') {
        button.style.backgroundColor = '';
        return;
    }

    if(button_type == 'fav') {
        button.style.backgroundColor = 'yellow';
    }
    else if(button_type == 'pen') {
        button.style.backgroundColor = 'cyan';
    }
    else {
        button.style.backgroundColor = 'green';
    }
}

// updates the color of a fps button given itself and the new state
function update_fps_button_colors(button_elements, button_states) {

    let button_colors = ['yellow', 'cyan', 'green'];

    for(let i = 0; i < button_elements.length; i++) {

        if(button_states[i] == '-1') {
            button_elements[i].style.backgroundColor = '';
        }
        else {
            button_elements[i].style.backgroundColor = button_colors[i];
        }
    }
}

// adds a search item and returns it
function add_search_item(parent, title, desc, img, item_id) {

    parent.innerHTML +=
                    '<div class="search_item" id="' + item_id + '">' +
                    '<img class="item_img" id="item_img" src="' + img + '"/>' +
                    '<div class="item_info">' +
                        '<div class="info_text">' +
                            '<p id="info_title">' + title + '</p>' +
                            '<P id="info_description">' + desc +'</P>' +
                        '</div>' +
                        '<div class="info_rating">' +
                           '<button class="info_button" type="button" id="btn_fav" onclick="fps_click(this, \'fav\')">FAV</button>' +
                           '<button class="info_button" type="button" id="btn_pen" onclick="fps_click(this, \'pen\')">PEN</button>' +
                           '<button class="info_button" type="button" id="btn_saw" onclick="fps_click(this, \'saw\')">SAW</button>' +
                        '</div>' +
                    '</div>' +
                    '</div>';

    return parent.children[parent.children.length - 1];
}

// adds a search item placeholder and returns it
function add_search_item_ph(parent) {

    parent.innerHTML +=
                    '<div class="search_item_ph" id="placeholder">' +
                    '<div class="item_img_ph" id="item_img_ph"></div>' +
                    '<div class="item_info">' +
                        '<div class="info_text">' +
                            '<p class="info_title_ph">Tetris</p>' +
                            '<p class="info_title_ph">2023 Taron Egerton, Mara Huf</p>' +
                        '</div>' +
                        '<div class="info_rating_ph">' +
                        '</div>' +
                    '</div>' +
                '</div>';

    return parent.children[parent.children.length - 1];
}