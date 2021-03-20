from helper import audit_log

def songs(app, session, db):

    @app.route('/api/songs/<page>', methods=['GET'])
    def list_songs(page):
        if 'username' in session and (session['permissions'] & 2):
            try:
                page = int(page)
            except:
                page = 0
            cur = db.cursor()
            cur.execute("SELECT * FROM songs LIMIT {},5;".format(page * 15))
            result = cur.fetchall()
            response = []
            for n in result:
                k = list(n)
                response.append({"id": n[0], "artist": n[1], "title": n[2], "fs_filename": n[3],
                 "audio_format": n[4], "genre": n[5], "date_released": n[6], "album_name": n[7], "fs_album_cover": n[8]})
            return {'songs':response}
        return {'result':'401','message':'Authentication failed'}, 401
        
    @app.route('/api/songs', methods=['GET'])
    def list_some_songs(page):
        return list_songs(0)