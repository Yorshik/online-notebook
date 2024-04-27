import datetime

import requests
from flask import Flask, render_template, request, redirect, abort
from flask_login import login_user, logout_user, LoginManager, login_required
from flask_restful import Api

from data import folder_resources
from data import note_resources
from data import user_resources
from data.db_session import global_init, create_session
from data.user import User
from scripts.api_keys import admin
from scripts.send_message import send_msg
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


@app.route('/enter_code')
def enter_code():
    if request.method == 'POST':
        entered_code = request.form.get('code')
        if entered_code == code:
            user = User.from_dict(
                {
                    'nickname': 'lox_zabivshiy_parol',
                    'email': temp_email,
                }
            )


@app.route('/forgot_password')
def get_code():
    global code
    global temp_email
    if request.method == 'POST':
        code = send_msg(request.form.get('email'))
        temp_email = request.form.get('email')
        return redirect('/enter_code')
    return render_template('forgot_password.html')


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
@app.route('/load_note_id/<note_name>')
def load_note_id(note_name):
    global folder_note_id
    note_id = note_resources.get_note_by_nickname(note_name)
    if note_id:
        folder_note_id = note_id
    return redirect('/main')


@login_required
@app.route('/add_note')
def add_note():
    unique_name = note_resources.get_unique_name_of_note()
    json_data = {
        'apikey': admin,
        'content': f'{unique_name}\n\n',
        'name': unique_name
    }
    note_req = requests.post(f'http://localhost:9999/api/notes/{login_user_id}/{user_folder_id}', json=json_data)
    if not note_req:
        print(note_req.text)
    return redirect('/main')


@login_required
@app.route('/add_folder')
def add_folder():
    unique_name = folder_resources.get_unique_name_of_folder()
    json_data = {
        'apikey': admin,
        'name': unique_name
    }
    folder_req = requests.post(f'http://localhost:9999/api/folders/{login_user_id}', json=json_data)
    if not folder_req:
        print(folder_req.text)
    return redirect('/main')


@login_required
@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        content = request.form.get('content')
        json_data = {
            'apikey': admin,
            'name': content[:content.find('\n')],
            'content': content
        }
        print(login_user_id, user_folder_id, folder_note_id)
        req = requests.put(
            f'http://localhost:9999/api/notes/{login_user_id}/{user_folder_id}/{folder_note_id}',
            json=json_data
        )
        if not req:
            print(req.text)
    json_data = {
        'apikey': admin
    }
    folders_req = requests.get(f'http://localhost:9999/api/folders/{login_user_id}', json=json_data)
    if folders_req:
        folders_json = folders_req.json()
        try:
            folders = folders_json['folders']
        except KeyError:
            folders = []
    else:
        abort(404)
    notes = []
    content = ''
    if user_folder_id:
        notes_req = requests.get(
            f'http://localhost:9999/api/notes/{login_user_id}/{user_folder_id}', json=json_data
        )
        if folders_req:
            notes_json = notes_req.json()
            try:
                notes = notes_json['notes']
            except KeyError:
                notes = []
        else:
            abort(400)
        if folder_note_id:
            content_req = requests.get(
                f'http://localhost:9999/api/notes/{login_user_id}/{user_folder_id}/'
                f'{folder_note_id}', json=json_data
            )
            content_json = content_req.json()
            try:
                content = content_json['note']['content']
            except KeyError:
                print(content_req.text)
    return render_template('main.html', list_of_folders=folders, list_of_notes=notes, note_content=content)


@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        user_data = requests.get(f'http://localhost:9999/api/users/{login_user_id}', json={'apikey': admin}).json()
        user = User.from_dict(user_data['user'])
        json_data = {
            'apikey': admin,
            'nickname': user.nickname,
            'password': user.hashed_password,
            'email': user.email
        }
        req = requests.put(f'http://localhost:9999/api/users/{login_user_id}', json=json_data)
        if not req:
            print(req.text)
    return render_template('account.html')


api.add_resource(user_resources.UsersListResource, '/api/users')
api.add_resource(user_resources.UsersResource, '/api/users/<int:user_id>')
api.add_resource(folder_resources.FoldersListResource, '/api/folders/<int:user_id>')
api.add_resource(folder_resources.FoldersResource, '/api/folders/<int:user_id>/<int:folder_id>')
api.add_resource(note_resources.NotesListResource, '/api/notes/<int:user_id>/<int:folder_id>')
api.add_resource(note_resources.NotesResource, '/api/notes/<int:user_id>/<int:folder_id>/<int:note_id>')

if __name__ == '__main__':
    code = None
    temp_email = None
    login_user_id = None
    user_folder_id = None
    folder_note_id = None
    global_init('db/online_notebook.db')
    db_sess = create_session()
    app.run(host='127.0.0.1', port='9999')
    db_sess.close()
