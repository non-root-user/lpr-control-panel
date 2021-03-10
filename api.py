from flask import abort, request
from config import Config
import bcrypt
import ast

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

    @app.route('/api/pony', methods=['POST'])
    def add_user():
        if 'username' in session and (session['permissions'] & 4):
            response = ast.literal_eval(request.data.decode())
            try:
                username    = db._cmysql.escape_string(response["username"]).decode() 
                password    = response['password']
                permissions = response['permission_level']
            except:
                print("invalid request values")
                abort(400)
            #This will accept only positive numbers, regardless of the value.
            #Even numbers are accepted, but users with even permissions won't have access to anything, thus blocking their access
            if not permissions.isnumeric():
                print("not numeric")
                abort(400)
            if Config.min_password_length > len(password) or Config.max_password_length < len(password):
                print("invalid pass length")
                abort(400)
            if Config.min_username_length > len(username) or Config.max_username_length < len(username):
                print("invalid username length")
                abort(400)
            cur = db.cursor()
            cur.execute("SELECT id FROM ponies WHERE username = '{}';".format(username))
            if cur.fetchall():
                print("user with that name exists")
                abort(400)
            values = [username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8"), permissions]
            cur.execute('INSERT INTO ponies (username, password, permission_level) VALUES (\'{}\', \'{}\', {});'.format(*values))
            db.commit()

            print(response)
            return {'result':'200','message':'User added successfuly'}
        abort(401)
