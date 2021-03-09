from flask import abort

def api(app, session, db):

    @app.route('/api')
    def api_index():
        return {'status': 200,'message':'I work!'}

    @app.route('/api/ponies/<page>', methods=['GET'])
    def list_users(page):
        if 'username' in session and (session['permissions'] & 4):
            cur = db.cursor()
            cur.execute("SELECT id, username, permission_level FROM ponies LIMIT {},5;".format(page))
            result = cur.fetchall()
            response = []
            for n in result:
                k = list(n)
                response.append({"id": n[0], "name": n[1], "permission_level": n[2]})
            print(response)
            return {'users':response}
        return abort(401)
    @app.route('/api/ponies', methods=['GET'])
    def list_some_users():
        print(list_users(0))
        return list_users(0)
