from helper import audit_log
from flask import request
import base64
import ast

def covers(app, session, db):

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
            cur.execute("SELECT id FROM albumarts WHERE id = '{}';".format(song_id))
            if not cur.fetchone():
                cur.execute("SELECT id FROM songs WHERE id = '{}';".format(song_id))
                if not cur.fetchone():
                    audit_log('has tried to change the cover of ' + str(song_id), session, request)
                    return {'result': '400', 'message': 'Song with that id does not exist'}, 400
                else:
                    cur.execute("INSERT INTO albumarts (id, image) VALUES {}, {}';".format(song_id, image))
                    db.commit()
                    audit_log('has changed the default cover of ' + str(song_id), session, request)
                    return {'result': '200', 'message': 'Cover updated succesfully, new row has been created'}
            else:
                cur.execute("UPDATE albumarts SET image = %s WHERE id = %s ;", (image, str(song_id)))
                db.commit()
                audit_log('has changed the cover of ' + str(song_id), session, request)
                return {'result': '200', 'message': 'Cover updated succesfully!'}
            
        return {'result': '401', 'message': 'Authentication failed'}, 401