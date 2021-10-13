from helper import audit_log
from flask import request
import base64


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
            clean_search = db.converter.escape(search)
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

    @app.route('/api/song/albumart/<song_id>', methods=['GET'])
    def get_coverart(song_id):
        if 'username' in session and (session['permissions'] & 1):
            audit_log('tried getting the cover of ' + song_id, session, request)
            try:
                song_id = int(song_id)
            except:
                return {'result': '400', 'message': 'Invalid id'}, 400
            cur = db.cursor()
            cur.execute("SELECT * FROM albumarts WHERE id = '{}';".format(song_id))
            cover = cur.fetchone()
            if not cover:
                return {'result': '400', 'message': 'Song with that id does not exist, or the song has no cover art attached'}, 400
            return cover[1], 200, {'Content-Type': 'image/png'}

        return {'result': '401', 'message': 'Authentication failed'}, 401

    @app.route('/api/song/albumart/<song_id>', methods=['PUT'])
    def change_coverart(song_id):
        if 'username' in session and (session['permissions'] & 2) and (session['permissions'] & 1):
            response = ast.literal_eval(request.data.decode())
            try:
                image = response['image']
                image = base64.b64decode(image)
            except:
                audit_log('has tried to change the cover of ' + song_id, session, request)
                return {'result': '400', 'message': 'Invalid image'}, 400
            try:
                song_id = int(song_id)
            except:
                audit_log('has tried to change the cover of ' + song_id, session, request)
                return {'result': '400', 'message': 'Invalid id'}, 400
            cur = db.cursor()
            if not cur.execute("SELECT id FROM albumarts WHERE id = '{}';".format(song_id)):
                if not cur.execute("SELECT id FROM songs WHERE id = '{}';".format(song_id)):
                    audit_log('has tried to change the cover of ' + song_id, session, request)
                    return {'result': '400', 'message': 'Song with that id does not exist'}, 400
                else:
                    cur.execute("INSERT INTO albumarts (id, image) VALUES';".format(song_id, image))
                    db.commit()
                    audit_log('has changed the default cover of ' + song_id, session, request)
                    return {'result': '200', 'message': 'Cover updated succesfully, new row has been created'}
            else:
                cur.execute("UPDATE albumarts SET image = {} WHERE id = '{}';".format(image, song_id))
                db.commit()
                audit_log('has changed the cover of ' + song_id, session, request)
                return {'result': '200', 'message': 'Cover updated succesfully!'}
            
        return {'result': '401', 'message': 'Authentication failed'}, 401