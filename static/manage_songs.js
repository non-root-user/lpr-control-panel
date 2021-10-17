
window.onload = () => {
    id_bt.onclick = () => {
        if (!id_input.value) return;
        id_result.innerHTML = '';
        fetch("/api/song/" + id_input.value)
        .then(res => res.json())
        .then(async out => {
            let music_div = document.createElement('div');
            let music_cover_img = document.createElement('img');
            let music_info = document.createElement('div');
            let values = "<b>Title: </b><i>" + out.songs.title + "</i><br>" + 
                "<b>Artist: </b><i>" + out.songs.artist + "</i><br>" +
                "<b>Album: </b><i>" + out.songs.album_name + "</i><br>" +
                "<b>Date Released: </b><i>" + out.songs.date_released + "</i><br>" +
                "<b>Genre: </b><i>" + out.songs.genre + "</i><br>" +
                "<b>Filename: </b><i>" + out.songs.fs_filename + "</i><br>" +
                "<b>Id: </b><i>" + out.songs.id + "</i><br>" ;
            
            music_cover_img.setAttribute("src", "/api/song/albumart/" + id_input.value);
            music_cover_img.style.width = '256px';
            music_info.innerHTML = values;

            music_div.appendChild(music_cover_img);
            music_div.appendChild(music_info);

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