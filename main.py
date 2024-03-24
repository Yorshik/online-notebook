from flask import Flask, render_template, redirect, url_for
from data.db_session import global_init, create_session

app = Flask(__name__)
app.secret_key = 'online_notebook_project'


@app.route('/')
@app.route('/index')
def index():
    return '<h1>Unavailable</h1>'


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    return '<h1>Unavailable</h1>'


@app.route('/main')
def main():
    return '<h1>Unavailable</h1>'


@app.route('/account')
def account():
    return '<h1>Unavailable</h1>'


if __name__ == '__main__':
    global_init('db/online_notebook.db')
    db_sess = create_session()
    app.run(host='127.0.0.1', port='9999')
    db_sess.close()
