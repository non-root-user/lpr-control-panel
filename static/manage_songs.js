
window.onload = () => {

    id_bt.onclick = () => {
        if (!id_input.value) return;
        id_result.innerHTML = '';
        fetch("/api/song/" + id_input.value)
        .then(res => res.json())
        .then(async out => {
            let music_div = document.createElement('div');
            var music_cover_img = document.createElement('img');
            let music_info = document.createElement('div');
            if(out.hasOwnProperty('message')){
                var values = out.message;
            }
            else{
                var values = "<b>Title: </b><i>" + out.songs.title + "</i><br>" + 
                    "<b>Artist: </b><i>" + out.songs.artist + "</i><br>" +
                    "<b>Album: </b><i>" + out.songs.album_name + "</i><br>" +
                    "<b>Date Released: </b><i>" + out.songs.date_released + "</i><br>" +
                    "<b>Genre: </b><i>" + out.songs.genre + "</i><br>" +
                    "<b>Filename: </b><i>" + out.songs.fs_filename + "</i><br>" +
                    "<b>Id: </b><i>" + out.songs.id + "</i><br>" ;
            
                music_cover_img.setAttribute("src", "/api/song/albumart/" + id_input.value);
                music_cover_img.style.width = '256px';

                var edit_button = document.createElement('button');
                edit_button.setAttribute("id", "edit_bt");
                edit_button.setAttribute("class", "inside_buttons");
                edit_button.innerHTML = "Edit";

                edit_button.addEventListener('click', () => {

                    let blur = document.createElement('div');
                    blur.setAttribute("id", "blur");
                    music_div.appendChild(blur);
                    blur.addEventListener('click', () => {
                        document.getElementById("blur").outerHTML = "";
                    });
                    var edit_panel = document.createElement('div');
                    edit_panel.setAttribute("class", "panel popup");
                    //edit_panel.classList.remove("disappear"); // makes sure the panel is visible by overriding display:none
                    edit_panel.addEventListener('click', (event) => {
                        event.stopPropagation();
                    })
                    edit_panel.innerHTML = "Edit";

                    //I absolutely hate this chunk of code, will purge the hell out of it whenever i get the chance
                    let current_cover = music_cover_img.cloneNode(false);
                    let edit_title = document.createElement('input');
                        edit_title.setAttribute('placeholder', 'song title');
                        edit_title.setAttribute('id', 'edit_title');
                    let edit_artist = document.createElement('input');
                        edit_artist.setAttribute('placeholder', 'artist');
                        edit_artist.setAttribute('id', 'edit_artist');
                    let edit_album = document.createElement('input');
                        edit_album.setAttribute('placeholder', 'album');
                        edit_album.setAttribute('id', 'edit_album');
                    let edit_genre = document.createElement('input');
                        edit_genre.setAttribute('placeholder', 'genre');
                        edit_genre.setAttribute('id', 'edit_genre');
                    let edit_date = document.createElement('input');
                        edit_date.setAttribute('placeholder', 'year of release');
                        edit_date.setAttribute('type', 'number');
                        edit_date.setAttribute('id', 'edit_date');
                    let edit_file = document.createElement('input');
                        edit_file.setAttribute('type', 'file');
                        edit_file.setAttribute('id', 'edit_file');

                    let confirm_bt = document.createElement('button');
                        confirm_bt.setAttribute("class", "inside_buttons");
                        confirm_bt.innerHTML = 'Confirm'

                    confirm_bt.addEventListener('click', () => {
                        if (!Boolean(edit_title.value + edit_artist.value + edit_album.value + edit_genre.value + edit_date.value) + (edit_file.files.length != 0)){
                            //TODO notify the user that nothing is filled in
                        }
                        else {
                            let diff_panel = document.createElement('div');
                            diff_panel.setAttribute('id', 'diff_panel');
                            diff_panel.setAttribute("class", "panel popup");
                            edit_panel.classList.add("disappear");
                            diff_panel.style.display = "block";
                            diff_panel.innerHTML = "Changes made:";
                            diff_panel.addEventListener('click', (event) => {
                                event.stopPropagation();
                            });
                            blur.appendChild(diff_panel);
                            let changes_before = document.createElement('div');
                            let changes_after = document.createElement('div');
                            let accept_bt = document.createElement('button');
                                accept_bt.innerHTML = 'Accept changes';
                            let back_bt = document.createElement('button');
                                back_bt.innerHTML = 'Cancel';
                                back_bt.addEventListener('click', () => {
                                    edit_panel.classList.remove('disappear');
                                    document.getElementById('diff_panel').outerHTML = "";
                                });

                            diff_panel.append(changes_before, changes_after, accept_bt, back_bt)
                        }
                    });

                    blur.appendChild(edit_panel);
                    edit_panel.append(current_cover, edit_title, edit_artist, edit_album, edit_genre, edit_date, edit_file, confirm_bt);
                });

                var delete_button = document.createElement('button');
                delete_button.setAttribute("id", "delete_bt");
                delete_button.setAttribute("class", "inside_buttons");
                delete_button.addEventListener('click', () => {

                    let blur = document.createElement('div');
                    blur.setAttribute("id", "blur");
                    music_div.appendChild(blur);
                    blur.addEventListener('click', () => {
                        document.getElementById("blur").outerHTML = "";
                    });
                    var warning = document.createElement('div');
                    warning.setAttribute("class", "panel popup");
                    warning.addEventListener('click', (event) => {
                        event.stopPropagation();
                    })
                    warning.innerHTML = "Are you sure you want to delete this song?"

                    let confirm_bt = document.createElement('button');
                    confirm_bt.innerHTML = "Delete";
                    confirm_bt.setAttribute("id", "delete_bt");
                    confirm_bt.setAttribute("class", "inside_buttons");
                    confirm_bt.addEventListener('click', async () => {
                        let response = await fetch('/api/song/' + out.songs.id, {method:'DELETE'});
                        warning.innerHTML = "<b>" + (await response.json()).message + "</b>";
                    });
                    
                    blur.appendChild(warning);
                    warning.appendChild(confirm_bt);

                });
                delete_button.innerHTML = "Delete";

            }
            music_info.innerHTML = values;

            if(!out.hasOwnProperty('message')){
                music_div.appendChild(music_cover_img);
                music_div.appendChild(music_info);
                music_div.appendChild(edit_button);
                music_div.appendChild(delete_button);
            }
            else{
                music_div.appendChild(music_info);
            }

            id_result.appendChild(music_div);
        });
    }
    cover_bt.onclick = () => {
        if (!id_cover.value) return;
        if (cover_file.files.length == 0) return;
        let reader = new FileReader();
        reader.onload = async event => {
            let image64 = event.target.result.split(',')[1];
            let img_json = JSON.stringify({'image':image64});

            let response = await fetch('/api/song/albumart/' + id_cover.value, {method:'PUT',body:img_json});
            document.getElementById('cover_output').innerHTML = "<b>" + (await response.json()).message + "</b>";

        }
        reader.readAsDataURL(cover_file.files[0]);

    }
    song_bt.onclick = () => {
        if ([add_title.value, add_artist.value, add_album.value, add_genre.value, add_year.value].includes('')) return;
        if (song_file.files.length == 0) return;

        let reader = new FileReader();
        reader.onload = async event => {
            let song64 = event.target.result.split(',')[1];
            let song_json = JSON.stringify({title:add_title.value,
                artist:add_artist.value,
                album_name:add_album.value,
                genre:add_genre.value,
                date_released:add_year.value,
                audio_file:song64});

            let response = await fetch('/api/song', {method:'POST',body:song_json});
            let json = await response.json();
            document.getElementById('song_output').innerHTML = "<b>" + json.message + 
                (json.song_id === undefined ? "</b>" : "<br> ID: </b><i>" + json.song_id[0] + "</i>");

        }
        reader.readAsDataURL(song_file.files[0]);
    }
}

// TODO put all big functions into a separate place, for better readability
// TODO make all variable names consistant, try to use camelCase in js
// TODO make quote marks consistant
// TODO truncate redundant code, for the love of god, make this file smaller
// TODO never write any more frontend
// TODO clicking on the cover while in edit mode should allow a new cover to be uploaded
// TODO image preview when uploading a cover
