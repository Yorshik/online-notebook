from flask import Flask, render_template, redirect, url_for
from data.db_session import global_init, create_session
from forms import *
from data.user import User
from data.note import Note
from data.folder import Folder
import datetime
from flask_login import login_user, logout_user, LoginManager, login_required

app = Flask(__name__)
app.secret_key = 'online_notebook_project'
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/')
@app.route('/index')
def index():
    return '<h1>Unavailable</h1>'


@app.route('/about')
def about():
    return '<h1>Unavailable</h1>'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.pass1.data != form.pass2.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.set_password(form.pass1.data)
        user.nickname = form.nickname.data
        user.modified_date = datetime.datetime.now()
        db_sess.add(user)
        db_sess.commit()
        db_sess.refresh(user)
        login_user(user, remember=True, duration=datetime.timedelta(hours=1))
        return redirect('/main')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data, duration=datetime.timedelta(hours=1))
            return redirect("/main")
        return render_template(
            'login.html',
            message="Неправильный логин или пароль",
            form=form
        )
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    return '<h1>Unavailable</h1>'


@app.route('/main')
@login_required
def main():
    return '<h1>Unavailable</h1>'


@app.route('/account')
@login_required
def account():
    return '<h1>Unavailable</h1>'


@app.route('/reset_pass')
def reset_pass():
    return '<h1>Unavailable</h1>'


@app.route('/add_note', methods=["GET", 'POST'])
def add_note():
    return '<h1>Unavailable</h1>'


@app.route('/add_folder', methods=["GET", 'POST'])
def add_folder():
    return '<h1>Unavailable</h1>'


@app.route('/note/<int:num>')
def note(num):
    return '<h1>Unavailable</h1>'


@app.route('/folder/<int:num>')
def folder(num):
    return '<h1>Unavailable</h1>'


@app.route('/delete_note/<int:num>')
def delete_note(num):
    return '<h1>Unavailable</h1>'


@app.route('/delete_folder/<int:num>')
def delete_folder(num):
    return '<h1>Unavailable</h1>'


if __name__ == '__main__':
    global_init('db/online_notebook.db')
    db_sess = create_session()
    app.run(host='127.0.0.1', port='9999')
    db_sess.close()
