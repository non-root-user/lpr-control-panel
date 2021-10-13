import mysql.connector
import bcrypt
import string
import random
import sys
import logging
from flask import Flask, render_template, request, session, redirect, url_for, abort
from config import Config
from api import api as api
from database_init import initialize_the_database
from helper import audit_log

app = Flask(__name__)
logging.basicConfig(filename='panel.log', level=logging.DEBUG, format=f'%(message)s')
# this generates a fresh session key every time the program restarts
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
initialize_the_database(db)

all_panels = ['hello_panel', 'manage_songs', 'manage_users']

cur = db.cursor()
cur.execute('SELECT * FROM ponies')
if not cur.fetchall() and Config.admin_enabled:
    print('''
There are no users present in the database, and admin_enabled is set to True
Creating the default admin...
Please, either delete the admin account, or change its password after you're done with the configuration.
You can disable this option in config.py.
    ''')
    # this will generate an admin account and give it maximum privileges based on number of panels implemented
    admin_query = ['admin', bcrypt.hashpw(Config.admin_pass.encode('utf-8'),
                                          bcrypt.gensalt()).decode("utf-8"), (2**(len(all_panels)) - 1)]
    cur.execute('''INSERT INTO ponies (username, password, permission_level) 
                    VALUES (\'{}\', \'{}\', {});'''.format(*admin_query))
    db.commit()


@app.route('/manage_users')
def manage_users():
    if 'username' in session and (session['permissions'] & 4):
        return render_template('manage_users.html')
    abort(404)


@app.route('/manage_songs')
def manage_songs():
    if 'username' in session and (session['permissions'] & 2):
        return render_template('manage_songs.html')
    abort(404)


@app.route('/')
def index():
    if 'username' in session and (session['permissions'] & 1):

        allowed_panels = []
        for i in range(len(all_panels)):
            if session['permissions'] & 2**i:
                allowed_panels.append(all_panels[i])

        return render_template('dashboard.html', panels=allowed_panels)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login(error=""):
    if request.method == 'POST':
        cur = db.cursor()
        username = db.converter.escape(request.form.get('username')).lower()
        plain_pass = request.form.get('password').encode('utf-8')

        cur.execute("SELECT permission_level, password FROM ponies WHERE lower(username) = '{}'".format(username))
        user_info = cur.fetchone()
        if user_info is not None:
            test_pass = bcrypt.hashpw(plain_pass, user_info[1].encode('utf-8'))
            is_identified = (user_info[1].encode('utf-8') == test_pass)
            if not is_identified:
                return render_template('login.html', error="Username or password incorrect.")
            session['username'] = username
            session['permissions'] = user_info[0]

            user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr) if Config.use_reverse_proxy \
                else request.remote_addr
            audit_log('Successful login', session, request)
            app.logger.info('IP: {} logged in as user: {}'.format(user_ip, username))
            session.permanent = True
            app.permanent_session_lifetime = 3600
            return redirect(url_for('index'))
        audit_log('Unsuccessful login attempt for user {}'.format(username), session, request)
        return render_template('login.html', error="Username or password incorrect.")
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('login'))


@app.errorhandler(404)
#Flask pushes an error message as the first argument, x prevents it from crashing due to oversaturation
def not_found(x):
    return render_template('not_found.html'), 404


api.initialize(app, session, db)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5111, debug=True)
