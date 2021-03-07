from flask import Flask, render_template, request
from config import Config
from mysql.connector import errorcode
import mysql.connector
import bcrypt

app = Flask(__name__)
try:
    db = mysql.connector.connect(
       user=Config.db_user, password=Config.db_password,
       host=Config.db_host, database=Config.database
    )
except mysql.connector.Error as err:
    print(err)



@app.route('/')
def template():
    return render_template('base.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = db.cursor()
        username = db._cmysql.escape_string(request.form.get('username')).decode()
        plain_pass = request.form.get('password').encode('utf-8')
        hash_pass = bcrypt.hashpw(plain_pass, bcrypt.gensalt())

        cur.execute("SELECT username, password FROM ponies WHERE username = '{}'".format(username))
        user_info = cur.fetchone()
        print(user_info)
        if user_info != None:
            test_pass = bcrypt.hashpw(plain_pass, user_info[1].encode('utf-8'))
            isIdentified = (user_info[1].encode('utf-8') == test_pass)
            if not isIdentified:
                return render_template('login.html', error="Password incorrect.")
            return '<h2>Username: {}<br>Hashed Pass: {}<br>Test Pass: {}<br>Is correct: {}</h2>'.format(username,hash_pass,test_pass,isIdentified)
        
        #return '<center><h1>Username: {}</h1><br><h1>Password: {}</h1></center>'.format(username, hash_pass)
        return render_template('login.html', error="There is user with that username.")

    return render_template('login.html')