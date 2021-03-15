from flask import Flask, render_template, request, session, redirect, url_for, abort
from config import Config
from mysql.connector import errorcode
from datetime import timedelta
import mysql.connector
import bcrypt
import string
import random
import sys
from api import api as api

app = Flask(__name__)
#this generates a fresh session key every time the program restarts
session_secret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
app.secret_key = session_secret
try:
    db = mysql.connector.connect(
       user=Config.db_user, password=Config.db_password,
       host=Config.db_host, database=Config.database
    )
except mysql.connector.Error as err:
    print(err)
    sys.exit(1)

all_panels = ['hello_panel','manage_songs','manage_users']

cur = db.cursor()
cur.execute('SELECT * FROM ponies')
if not cur.fetchall() and Config.admin_enabled:
    print('''
There are no users present in the database, and admin_enabled is set to True
Creating the default admin...
Please, either delete the admin account, or change its password after you're done with the configuration.
You can disable this option in config.py.
    ''')
    #this will generate an admin account and give it maximum privilages based on number of panels implemented
    admin_query = ['admin', bcrypt.hashpw(Config.admin_pass.encode('utf-8'), bcrypt.gensalt()).decode("utf-8"), (2**(len(all_panels)) - 1)]
    cur.execute('INSERT INTO ponies (username, password, permission_level) VALUES (\'{}\', \'{}\', {});'.format(*admin_query))
    db.commit()

#@app.before_request

@app.route('/manage_users')
def manage_users():
    if 'username' in session and (session['permissions'] & 4):
        return render_template('manage_users.html')
    abort(401)

@app.route('/manage_songs')
def manage_songs():
    if 'username' in session and (session['permissions'] & 2):
        return render_template('manage_songs.html')
    abort(401)

@app.route('/')
def index():
    if 'username' in session and (session['permissions'] & 1):

        allowed_panels = []
        for i in range(len(all_panels)):
            if session['permissions'] & 2**i:
                allowed_panels.append(all_panels[i])

        return render_template('dashboard.html', panels=allowed_panels)
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login(error = ""):
    if request.method == 'POST':
        cur = db.cursor()
        username = db._cmysql.escape_string(request.form.get('username')).decode().lower()
        plain_pass = request.form.get('password').encode('utf-8')
        hash_pass = bcrypt.hashpw(plain_pass, bcrypt.gensalt())

        cur.execute("SELECT permission_level, password FROM ponies WHERE lower(username) = '{}'".format(username))
        user_info = cur.fetchone()
        if user_info != None:
            test_pass = bcrypt.hashpw(plain_pass, user_info[1].encode('utf-8'))
            isIdentified = (user_info[1].encode('utf-8') == test_pass)
            if not isIdentified:
                return render_template('login.html', error="Username or password incorrect.")
            session['username'] = username
            session['permissions'] = user_info[0]
            session.permanent = True
            app.permanent_session_lifetime = 3600
            return redirect(url_for('index'))
            
        
        return render_template('login.html', error="Username or password incorrect.")

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

api(app, session, db)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5111, debug=True)