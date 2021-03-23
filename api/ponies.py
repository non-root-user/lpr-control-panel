from flask import abort, request
from config import Config
from helper import audit_log
import bcrypt
import ast

def ponies(app, session, db):

    @app.route('/api/ponies/<page>', methods=['GET'])
    def list_users(page):
        if 'username' in session and (session['permissions'] & 4) and (session['permissions'] & 1):
            try:
                page = int(page)
            except:
                page = 0
            cur = db.cursor()
            cur.execute("SELECT id, username, permission_level FROM ponies LIMIT {},15;".format(page * 15))
            result = cur.fetchall()
            response = []
            for n in result:
                k = list(n)
                response.append({"id": n[0], "name": n[1], "permission_level": n[2]})
            return {'users':response}
        return abort(401)

    @app.route('/api/ponies', methods=['GET'])
    def list_some_users():
        return list_users(0)

    @app.route('/api/pony', methods=['POST'])
    def add_user():
        if 'username' in session and (session['permissions'] & 4) and (session['permissions'] & 1):
            response = ast.literal_eval(request.data.decode())
            try:
                username     = db._cmysql.escape_string(response["username"]).decode()
                password     = response['password']
                permissions  = response['permission_level']
                username_low = username.lower()
            except:
                return {'result':'400','message':'Invalid request values'}, 400
            # This will accept only positive numbers, regardless of the value.
            # Even numbers are accepted, but users with even permissions won't have access to anything,
            # thus blocking their access
            try:
                if not permissions.isnumeric():
                    return {'result':'400','message':'Permissions are not numeric'}, 400
            except:
                pass
            if any(not c.isalnum() for c in username_low.replace("_", "")):
                return {'result':'400','message':'Username is not alphanumeric'}, 400
            if Config.min_password_length > len(password) or Config.max_password_length < len(password):
                return {'result':'400','message':'Invalid password length'}, 400
            if Config.min_username_length > len(username) or Config.max_username_length < len(username):
                return {'result':'400','message':'Invalid username length'}, 400
            cur = db.cursor()
            cur.execute("SELECT id FROM ponies WHERE lower(username) = '{}';".format(username_low))
            if cur.fetchall():
                return {'result':'400','message':'User with that name exists'}, 400
            values = [username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8"), permissions]
            cur.execute('INSERT INTO ponies (username, password, permission_level) VALUES (\'{}\', \'{}\', {});'.format(*values))
            new_user_id = cur.lastrowid
            db.commit()

            audit_log('Added a new user {} with permissions {}'.format(username, permissions), session, request)
            return {'result':'200','message':'User added successfuly', 'id':new_user_id}, 200
        return {'result':'401','message':'Authentication failed'}, 401

    @app.route('/api/pony', methods=['DELETE'])
    def delete_user():
        if 'username' in session:
            response = ast.literal_eval(request.data.decode())
            try:
                username     = db._cmysql.escape_string(response["username"]).decode()
                username_low = username.lower()
            except:
                return {'result':'400','message':'Invalid request values'}, 400
            if (session['permissions'] & 4) or session['username'] == username:
                cur = db.cursor()
                cur.execute("DELETE FROM ponies WHERE lower(username) = '{}';".format(username_low))
                db.commit()
                audit_log('Removed user {} '.format(username), session, request)
                return {'result':'200','message':'User deleted successfuly'}
        return {'result':'401','message':'Authentication failed'}, 401

    @app.route('/api/pony', methods=['PUT'])
    def modify_user():
        if 'username' in session and (session['permissions'] & 4) and (session['permissions'] & 1):
            response = ast.literal_eval(request.data.decode())
            try:
                username     = db._cmysql.escape_string(response["username"]).decode()
                permissions  = response['permission_level']
                username_low = username.lower()
            except:
                return {'result':'400','message':'Invalid request values'}, 400
            try:
                if not permissions.isnumeric():
                    return {'result':'400','message':'Permissions are not numeric'}, 400
            except:
                pass
            cur = db.cursor()
            cur.execute("SELECT permission_level FROM ponies WHERE lower(username) = '{}';".format(username_low))
            old = cur.fetchone()[0]
            if not old:
                return {'result':'400','message':'User with that name does not exist'}, 400
            cur.execute("UPDATE ponies SET permission_level = {} WHERE lower(username) = '{}';".format(permissions, username_low))
            db.commit()
            audit_log('Modified user {}, changed permissions from {} to {}'.format(username, old, permissions), session, request)
            return {'result':'200','message':'User modified successfully'}, 200
        return {'result':'401','message':'Authentication failed'}, 401

    @app.route('/api/password', methods=['PUT'])
    def change_password():
        if 'username' in session and (session['permissions'] & 1):
            response = ast.literal_eval(request.data.decode())
            try:
                if session['permissions'] & 4:
                    try:
                        username = db._cmysql.escape_string(response["username"]).decode().lower()
                    except:
                        username = session['username']
                else:
                    username     = session['username']
                password     = response['password']
                username_low = username.lower()
            except:
                return {'result':'400','message':'Invalid request values'}, 400
            hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
            cur = db.cursor()
            if not cur.execute("SELECT id FROM ponies WHERE lower(username) = '{}';".format(username_low)):
                return {'result': '400', 'message': 'User with that username does not exist'}, 400
            cur.execute("UPDATE ponies SET password = {} WHERE lower(username) = '{}';".format(hash_pass, username_low))
            db.commit()
            return {'result': 200, 'message':'Password changed successfully'}, 200
        return {'result':'401','message':'Authentication failed'}, 401