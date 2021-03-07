from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def template(name=None):
    return render_template('base.html', name=name)

@app.route('/login')
def login(name=None):
    return render_template('login.html', name=name)