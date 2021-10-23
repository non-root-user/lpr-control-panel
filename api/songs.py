from helper import audit_log
from flask import request
from config import Config
import os.path
import ast
import base64


def songs(app, session, db):

    @app.route('/api/songs/<page>', methods=['GET'])
    def list_songs(page):
        if ('username' in session and (session['permissions'] & 2)
                and (session['permissions'] & 1)):
            try:
                page = int(page)
            except ValueError:
                page = 0
            cur = db.cursor()
            cur.execute("SELECT * FROM songs LIMIT {},5;".format(page * 15))
            result = cur.fetchall()
            response = []
            for n in result:
                response.append({"id": n[0], "artist": n[1], "title": n[2],
                                 "fs_filename": n[3], "audio_format": n[4],
                                 "genre": n[5], "date_released": n[6],
                                 "album_name": n[7], "fs_album_cover": n[8]})
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
            except ValueError:
                return {'result': '400', 'message': 'Invalid id'}, 400

            cur = db.cursor()
            cur.execute("SELECT * FROM songs WHERE id = '{}';".format(song_id))
            song = cur.fetchone()

            if not song:
                return {'result': '404', 'message':
                        'Song with that id does not exist'}, 404
            response = {"id": song[0], "artist": song[1], "title": song[2],
                        "fs_filename": song[3], "audio_format": song[4],
                        "genre": song[5], "date_released": song[6],
                        "album_name": song[7], "fs_album_cover": song[8]}

            return {'songs': response}

        return {'result': '401', 'message': 'Authentication failed'}, 401

    @app.route('/api/songs/find/<search>', methods=['GET'])
    def find_song(search):
        if 'username' in session and (session['permissions'] & 1):
            audit_log('tried song-searching for ' + search, session, request)

            if len(search) < 3 or len(search) >= 64:
                return {'result': '400', 'message':
                        'Invalid search length, must be between 3 and 64'}, 400

            clean_search = db.converter.escape(search)
            cur = db.cursor()
            query = '''SELECT * FROM songs WHERE
                CONCAT(artist,title,album_name) LIKE '{}'
                ORDER BY title ASC LIMIT 0,50;'''.format(clean_search)
            cur.execute(query)
            result = cur.fetchall()
            response = []

            for n in result:
                response.append({"id": n[0], "artist": n[1], "title": n[2],
                                 "fs_filename": n[3], "audio_format": n[4],
                                 "genre": n[5], "date_released": n[6],
                                 "album_name": n[7], "fs_album_cover": n[8]})

            return {'songs': response}

        return {'result': '401', 'message': 'Authentication failed'}, 401

    @app.route('/api/song', methods=['POST'])
    def add_song():
        if ('username' in session and (session['permissions'] & 2) and
           (session['permissions'] & 1)):

            try:
                response = ast.literal_eval(request.data.decode())
            except Exception:
                return {'result': '400', 'message': 'Invalid request'}, 400
            try:
                title = db.converter.escape(response["title"])
                artist = db.converter.escape(response["artist"])
                album_name = db.converter.escape(response["album_name"])
                genre = db.converter.escape(response["genre"])
                date_released = response["date_released"]
                audio_file = base64.b64decode(response["audio_file"])
                values = [title, artist, album_name, genre,
                          date_released, audio_file]
            except Exception:
                return {'result': '400', 'message':
                        'Invalid request values'}, 400

            for x in values:
                if not x:
                    return {'result': '400', 'message':
                            'Provided empty request values'}, 400

            filename = ",".join([artist, album_name,
                                 title + ".mp3"]).replace(" ", "_")
            if os.path.isfile(Config.song_path + filename):
                return {'result': '409', 'message':
                        'These song values are already occupied'}, 409

            file = open(Config.song_path + filename, 'wb+')
            file.write(audio_file)
            file.close()
            cur = db.cursor()
            query_arr = [artist, title, filename, 'mp3', genre, date_released,
                         album_name, 'placeholder']
            cur.execute('''INSERT INTO songs
                (artist,title,fs_filename,audio_format,genre,date_released,album_name,fs_album_cover)
                VALUES ('{}','{}','{}',
                        '{}','{}','{}','{}','{}')'''.format(*query_arr))
            db.commit()
            cur.execute('SELECT LAST_INSERT_ID();')
            new_id = cur.fetchone()
            audit_log('added a song with id:' + ''.join(
                str(x) for x in new_id), session, request)

            return {'result': '201', 'message': 'Song added succesfully',
                    'song_id': new_id}, 201

        return {'result': '401', 'message': 'Authentication failed'}, 401

    @app.route('/api/song/<song_id>', methods=['DELETE'])
    def delete_song(song_id):
        if ('username' in session and (session['permissions'] & 2) and
           (session['permissions'] & 1)):

            try:
                song_id = int(song_id)
            except ValueError:
                return {'result': '400', 'message': 'Invalid id'}, 400

            cur = db.cursor()
            cur.execute("SELECT * FROM songs WHERE id = '{}';".format(song_id))
            song = cur.fetchone()

            if not song:
                return {'result': '404', 'message':
                        'Song with that id does not exist'}, 404

            cur.execute("DELETE FROM songs WHERE id = {}".format(song_id))
            cur.execute("DELETE FROM albumarts WHERE id = {}".format(song_id))
            db.commit()
            return {'result': '200', 'message': 'Song id:' + str(song_id) +
                    ' deleted successfully'}, 200

        return {'result': '401', 'message': 'Authentication failed'}, 401

    @app.route('/api/song/<song_id>', methods=['PUT'])
    def edit_song_info(song_id):
        if ('username' in session and (session['permissions'] & 2) and
           (session['permissions'] & 1)):

            try:
                song_id = int(song_id)
            except ValueError:
                return {'result': '400', 'message': 'Invalid id'}, 400

            try:
                response = ast.literal_eval(request.data.decode())
            except Exception:
                return {'result': '400', 'message': 'Invalid request'}, 400
            cur = db.cursor()
            cur.execute("SELECT * FROM songs WHERE id = '{}';".format(song_id))
            song = cur.fetchone()

            if not song:
                return {'result': '404', 'message':
                        'Song with that id does not exist'}, 404
            if not response:
                return {'result': '400', 'message':
                        'No values to change were given'}, 400

            try:
                allowed_keys = ['title', 'artist', 'album_name', 'genre',
                                'date_released', 'audio_file']
                key_order = ['id', 'artist', 'title', 'fs_filename',
                             'audio_format', 'genre', 'date_released',
                             'album_name', 'fs_audio_cover']
                query = "UPDATE songs SET "
                changes = []

                for key, value in response.items():
                    if key not in allowed_keys:
                        return {'result': '400', 'message':
                                key + ' is not a changable value'}, 400

                    if key == 'audio_file':
                        filename = Config.song_path + song[3]
                        value = base64.b64decode(value)
                        file = open(filename, 'wb+')
                        file.write(value)
                        file.close()
                        changes.append("File has been changed")
                    else:
                        value = db.converter.escape(value)
                        query += "{} = '{}', ".format(key, value)
                        changes.append(song[key_order.index(key)] +
                                       " -> " + value)

                query = (query[:-2] + " WHERE id = '{}';".format(song_id))
                cur.execute(query)
                db.commit()
                changes_str = ', '.join(changes)
                log_msg = "Info for song id:{} has changed: {}".format(song_id, changes_str)
                audit_log(log_msg, session, request)
                return {'result': '200', 'message': 'Song info has been successfully changed'}, 200

            except IOError as err:
                audit_log("Could not save a file when updating song info: {}".format(str(err)), session, request)
                return {'result': '500', 'message':
                        'The server encountered an error when saving the song file'}, 500
            except Exception as err:
                audit_log(str(err), session, request)
                return {'result': '400', 'message':
                        'Request values are not permissible'}, 400

    # TODO fuzzy song search
    # TODO audio file check, and proper reincoding according to the config
    # TODO edit song info
    # TODO verbose audit log for deleting and editing
    # TODO error log as a separate function and a separate file
    # TODO separate access log, for things like getting a cover
    # TODO an api call for a song preview, make ffmpeg generate a short sample
    #      from the middle of a song, and serve it as a stream
