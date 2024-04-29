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
    global user_folder_id
    global login_user_id
    global folder_note_id
    logout_user()
    folder_note_id = None
    login_user_id = None
    user_folder_id = None
    return redirect('/')


@app.route('/index')
@app.route('/', methods=["get", "post"])
def index():
    answer = ""
    ask = ""
    if request.method == "POST":
        ask = request.form.get("text")
        answer = gpt_answer(ask)
    return render_template('index.html', ask=ask, answer=answer)


@app.route('/enter_code/<nickname>/<email>/<code>')
def enter_code(nickname, email, code):
    if request.method == 'POST':
        if hash(request.form.get('code')) == code:
            user = User.from_dict(
                {
                    'nickname': nickname,
                    'email': email,
                    'password': '1234'
                }
            )
            login_user(user)
        return '<h1>Your new password: 1234</h1><a href="/main">Главная</a>'
    return render_template('enter_code.html')


@app.route('/forgot_password')
def get_code():
    if request.method == 'POST':
        code = send_msg(request.form.get('email'))
        return redirect(f'/enter_code/{request.form.get('nick')}/{request.form.get('email')}/{hash(str(code))}')
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
        req = requests.post('http://127.0.0.1:9999/api/users', json=json_data)
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
        req = requests.get(f'http://127.0.0.1:9999/api/user/{user_id}', json=json_data)
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
@app.route('/load_folder_id/<folder_id>')
def load_folder_id(folder_id):
    global user_folder_id
    global folder_note_id
    user_folder_id = folder_id
    folder_note_id = None
    return redirect('/main')


@login_required
@app.route('/load_note_id/<note_id>')
def load_note_id(note_id):
    global folder_note_id
    folder_note_id = note_id
    return redirect('/main')


@login_required
@app.route('/add_note')
def add_note():
    if user_folder_id:
        unique_name = note_resources.get_unique_name_of_note(login_user_id, user_folder_id)
        json_data = {
            'apikey': admin,
            'content': f'{unique_name}\n\n',
            'name': unique_name
        }
        note_req = requests.post(f'http://127.0.0.1:9999/api/notes/{user_folder_id}', json=json_data)
        if not note_req:
            print('Сайт упал')
            print(f'Причина: {note_req.text}, asadsadasdas')
            print(note_req.url, login_user_id)
            quit()
        return redirect('/main')
    return render_template('/main', message='Before adding note - select folder')


@login_required
@app.route('/add_folder')
def add_folder():
    unique_name = folder_resources.get_unique_name_of_folder(login_user_id)
    json_data = {
        'apikey': admin,
        'name': unique_name
    }
    folder_req = requests.post(f'http://127.0.0.1:9999/api/folders/{login_user_id}', json=json_data)
    if not folder_req:
        print('Сайт упал')
        print(f'Причина: {folder_req.text}')
        quit()
    return redirect('/main')


@app.route('/main', methods=['GET', 'POST'])
def main():
    notes = []
    content = ''
    if request.method == 'POST':
        if folder_note_id:
            save_content = request.form.get('content')
            json_save = {
                'apikey': admin,
                'name': save_content[:save_content.find('\n')],
                'content': save_content
            }
            save_req = requests.put(f'http://127.0.0.1:9999/api/note/{folder_note_id}', json=json_save)
            if not save_req:
                print('Сайт упал')
                print(f'Причина: {save_req.text}')
                quit()
        else:
            return render_template('/main.html', message='Before saving smth select note')
    json_data = {
        'apikey': admin
    }
    folders_req = requests.get(f'http://127.0.0.1:9999/api/folders/{login_user_id}', json=json_data)
    if folders_req:
        folders = folders_req.json()['folders']
    else:
        folders = []
    if user_folder_id:
        notes_req = requests.get(f'http://127.0.0.1:9999/api/notes/{user_folder_id}', json=json_data)
        if notes_req:
            notes = notes_req.json()['notes']
        if folder_note_id:
            content_req = requests.get(f'http://127.0.0.1:9999/api/note/{folder_note_id}', json=json_data)
            if content_req:
                content = content_req.json()['note']['content']
    return render_template('main.html', list_of_folders=folders, list_of_notes=notes, note_content=content)


@login_required
@app.route('/prev_main', methods=['GET', 'POST'])
def prev_main():
    if request.method == 'POST':
        content = request.form.get('content')
        json_data = {
            'apikey': admin,
            'name': content[:content.find('\n')],
            'content': content
        }
        print(login_user_id, user_folder_id, folder_note_id)
        req = requests.put(
            f'http://127.0.0.1:9999/api/notes/{login_user_id}/{user_folder_id}/{folder_note_id}',
            json=json_data
        )
        if not req:
            print(req.text)



    json_data = {
        'apikey': admin
    }
    folders_req = requests.get(f'http://127.0.0.1:9999/api/folders/{login_user_id}', json=json_data)
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
            f'http://127.0.0.1:9999/api/notes/{login_user_id}/{user_folder_id}', json=json_data
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
                f'http://127.0.0.1:9999/api/notes/{login_user_id}/{user_folder_id}/'
                f'{folder_note_id}', json=json_data
            )
            content_json = content_req.json()
            try:
                content = content_json['note']['content']
            except KeyError:
                print(content_req.text)
    return render_template('main.html', list_of_folders=folders, list_of_notes=notes, note_content=content)


api.add_resource(user_resources.UsersListResource, '/api/users')
api.add_resource(user_resources.UsersResource, '/api/user/<int:user_id>')
api.add_resource(folder_resources.FoldersListResource, '/api/folders/<int:user_id>')
api.add_resource(folder_resources.FoldersResource, '/api/folder/<int:folder_id>')
api.add_resource(note_resources.NotesListResource, '/api/notes/<int:folder_id>')
api.add_resource(note_resources.NotesResource, '/api/note/<int:note_id>')


if __name__ == '__main__':
    login_user_id = None
    user_folder_id = None
    folder_note_id = None
    global_init('db/online_notebook.db')
    db_sess = create_session()
    app.run(host='127.0.0.1', port='9999')
    db_sess.close()