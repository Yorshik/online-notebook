import requests
from flask import Flask, render_template, request, redirect, abort
from data.db_session import global_init, create_session
from data.user import User
from data.note import Note
from data.folder import Folder
import datetime
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
from flask_restful import Api
from data import user_resources
from data import folder_resources
from data import note_resources
from scripts.api_keys import admin
from scripts.yan_gpt import gpt_answer

app = Flask(__name__)
app.secret_key = 'online_notebook_project'
api = Api(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/logout')
@login_required
def logout():
    logout_user()


@app.route('/', methods=["get", "post"])
def index():
    answer = ""
    ask = ""
    if request.method == "POST":
        ask = request.form.get("text")
        answer = gpt_answer(ask)
    return render_template('index.html', ask=ask, answer=answer)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global login_user_id
    if request.method == 'POST':
        if request.form.get('pass_1') != request.form.get('pass_2'):
            return render_template('register.html', message='Пароли не совпадают')
        json_data = {
            'apikey': admin,
            'nickname': request.form.get('nickname'),
            'password': request.form.get('pass_1'),
            'email': request.form.get('email')
        }
        req = requests.post('http://localhost:9999/api/users', json=json_data)
        match req.status_code:
            case 403 | 400:
                return render_template('register.html', message='troubles on the server')
            case 406:
                return render_template('register.html', message='user already exists')
            case 200:
                req_json = req.json()
        user = User.from_dict(req_json['user'])
        login_user_id = user.id
        login_user(user, remember=True, duration=datetime.timedelta(hours=1))
        return redirect('/main')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global login_user_id
    if request.method == 'POST':
        user_id = user_resources.get_user_by_nickname(request.form.get('nickname'))
        login_user_id = user_id
        if not user_id:
            return render_template('login.html', message='user not found')
        json_data = {
            'apikey': admin
        }
        req = requests.get(f'http://localhost:9999/api/users/{user_id}', json=json_data)
        match req.status_code:
            case 403:
                return render_template('login.html', message='troubles in the server')
            case 404:
                return render_template('login.html', message='user not found')
            case 200:
                req_json = req.json()
        user = User.from_dict(req_json['user'])
        if not user.check_password(request.form.get('password')):
            return render_template('login.html', message='incorrect login or password')
        login_user(user)
        return redirect('/main')
    return render_template('login.html')


@login_required
@app.route('/load_folder_id/<folder_name>')
def load_folder_id(folder_name):
    global user_folder_id
    folder_id = folder_resources.get_folder_by_nickname(folder_name)
    if folder_id:
        user_folder_id = folder_id
    return redirect('/main')


@login_required
@app.route('/main', methods=['GET', 'POST'])
def main():
    folders_req = requests.get(f'http://localhost:9999/api/folders/{login_user_id}')
    if folders_req:
        folders_json = folders_req.json()
    else:
        abort(404)
    if user_folder_id:
        notes_req = requests.get(f'http://localhost:9999/api/notes/{login_user_id}/{user_folder_id}')
        if folders_req:
            notes_json = notes_req.json()
        else:
            abort(404)
    return render_template('main.html', list_of_folders=folders_json['folders'], list_of_notes=notes_json['notes'])


api.add_resource(user_resources.UsersListResource, '/api/users')
api.add_resource(user_resources.UsersResource, '/api/users/<int:user_id>')
api.add_resource(folder_resources.FoldersListResource, '/api/folders/<int:user_id>')
api.add_resource(folder_resources.FoldersResource, '/api/folders/<int:user_id>/<int:folder_id>')
api.add_resource(note_resources.NotesListResource, '/api/notes/<int:user_id>/<int:folder_id>')
api.add_resource(note_resources.NotesResource, '/api/notes/<int:user_id>/<int:folder_id>/<int:note_id>')


if __name__ == '__main__':
    login_user_id = None
    user_folder_id = None
    global_init('db/online_notebook.db')
    db_sess = create_session()
    app.run(host='127.0.0.1', port='9999')
    db_sess.close()
