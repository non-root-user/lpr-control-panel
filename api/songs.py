from helper import audit_log
from flask import request


def songs(app, session, db):

    @app.route('/api/songs/<page>', methods=['GET'])
    def list_songs(page):
        if 'username' in session and (session['permissions'] & 2) and (session['permissions'] & 1):
            try:
                page = int(page)
            except:
                page = 0
            cur = db.cursor()
            cur.execute("SELECT * FROM songs LIMIT {},5;".format(page * 15))
            result = cur.fetchall()
            response = []
            for n in result:
                response.append({"id": n[0], "artist": n[1], "title": n[2], "fs_filename": n[3],
                                "audio_format": n[4], "genre": n[5], "date_released": n[6], "album_name": n[7],
                                 "fs_album_cover": n[8]})
            return {'songs': response}
        return {'result': '401', 'message': 'Authentication failed'}, 401
        
    @app.route('/api/songs', methods=['GET'])
    def list_some_songs():
        return list_songs(0)

    @app.route('/api/song/<song_id>', methods=['GET'])
    def get_song(song_id):
        if 'username' in session and (session['permissions'] & 1):
            try:
                song_id = int(song_id)
            except:
                return {'result': '400', 'message': 'Invalid id'}, 400
            cur = db.cursor()
            cur.execute("SELECT * FROM songs WHERE id = '{}';".format(song_id))
            song = cur.fetchone()
            if not song:
                return {'result': '400', 'message': 'Song with that id does not exist'}, 400
            response = {"id": song[0], "artist": song[1], "title": song[2], "fs_filename": song[3],
                        "audio_format": song[4], "genre": song[5], "date_released": song[6], "album_name": song[7],
                        "fs_album_cover": song[8]}
            return {'songs': response}
        return {'result': '401', 'message': 'Authentication failed'}, 401

    @app.route('/api/songs/find/<search>', methods=['GET'])
    def find_song(search):
        if 'username' in session and (session['permissions'] & 1):
            audit_log('tried song-searching for ' + search, session, request)
            if len(search) < 3 or len(search) >= 64:
                return {'result': '400', 'message': 'Invalid search length, must be between 3 and 64'}, 400
            clean_search = db._cmysql.escape_string(search).decode()
            cur = db.cursor()
            query = '''SELECT * FROM songs WHERE 
                CONCAT(artist,title,album_name) LIKE '{}' 
                ORDER BY title ASC LIMIT 0,50;'''.format(clean_search)
            cur.execute(query)
            result = cur.fetchall()
            response = []
            for n in result:
                response.append({"id": n[0], "artist": n[1], "title": n[2], "fs_filename": n[3],
                                "audio_format": n[4], "genre": n[5], "date_released": n[6],
                                 "album_name": n[7], "fs_album_cover": n[8]})
            return {'songs': response}
        return {'result': '401', 'message': 'Authentication failed'}, 401
