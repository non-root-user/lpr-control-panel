from flask import Flask, render_template, request, session, redirect, url_for
from config import Config
from mysql.connector import errorcode
from datetime import timedelta
import mysql.connector
import bcrypt
import string
import random

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

#@app.before_request
#check if request timed out
#def session_timeout():
    

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as {} with permissions {}'.format(session['username'], session['permissions'])
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = db.cursor()
        username = db._cmysql.escape_string(request.form.get('username')).decode()
        plain_pass = request.form.get('password').encode('utf-8')
        hash_pass = bcrypt.hashpw(plain_pass, bcrypt.gensalt())

        cur.execute("SELECT permission_level, password FROM ponies WHERE username = '{}'".format(username))
        user_info = cur.fetchone()
        print(user_info)
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
            #return '<h2>Username: {}<br>Hashed Pass: {}<br>Test Pass: {}<br>Is correct: {}</h2>'.format(username,hash_pass,test_pass,isIdentified)

        
        #return '<center><h1>Username: {}</h1><br><h1>Password: {}</h1></center>'.format(username, hash_pass)
        return render_template('login.html', error="Username or password incorrect.")

    return render_template('login.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')