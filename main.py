import datetime

import requests
from flask import Flask, render_template, request, redirect
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
from flask_restful import Api

from data import folder_resources
from data import note_resources
from data import user_resources
from data.db_session import global_init, create_session
from data.user import User
from scripts.api_keys import admin
from scripts.send_message import send_msg
from scripts.yan_gpt import gpt_answer
from data import drive_through_GPT_resources


app = Flask(__name__)
app.secret_key = 'online_notebook_project'
api = Api(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)
    return user


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


@app.route('/enter_code/<int:user_id>/<nickname>/<email>/<code>', methods=['GET', 'POST'])
def enter_code(user_id, nickname, email, code):
    if request.method == 'POST':
        if str(hash(request.form.get('code'))) == code:
            return redirect(f"/enter_password/{nickname}/{email}/{user_id}")
        return render_template('enter_code.html', message='Неверный код')
    return render_template('enter_code.html')


@app.route("/enter_password/<nickname>/<email>/<int:user_id>", methods=['GET', 'POST'])
def enter_password(nickname, email, user_id):
    if request.method == 'POST':
        if request.form.get('pass1') == request.form.get('pass2'):
            json_data = {
                'apikey': admin,
                'nickname': nickname,
                'email': email,
                'password': request.form.get('pass1')
            }
            requests.delete(f'http://127.0.0.1:9999/api/user/{user_id}', json={'apikey': admin})
            req = requests.post(f'http://127.0.0.1:9999/api/users', json=json_data)
            if not req:
                print('Сайт упал')
                print(f'Причина: {req.text}')
            new_user = User.from_dict(req.json()['user'])
            login_user(new_user)
            return redirect('/main')
        return render_template('enter_password.html', message='Пароли не совпадают')
    return render_template('enter_password.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def get_code():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        user_id = user_resources.get_user_by_nickname(nickname)
        if not user_id:
            return render_template('forgot_password.html', message='User not found')
        req = requests.get(f'http://127.0.0.1:9999/api/user/{user_id}', json={'apikey': admin})
        email = req.json()['user']['email']
        code = send_msg(email)
        return redirect(f'/enter_code/{user_id}/{nickname}/{email}/{hash(str(code))}')
    return render_template('forgot_password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global login_user_id
    if current_user.is_authenticated:
        return redirect('/main')
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
        print(user.id)
        login_user(user, remember=True, duration=datetime.timedelta(hours=1))
        return redirect('/main')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global login_user_id
    if current_user.is_authenticated:
        return redirect('/main')
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
        login_user(user, remember=True)
        return redirect('/main')
    return render_template('login.html')


@app.route('/load_folder_id/<int:folder_id>')
@login_required
def load_folder_id(folder_id):
    global user_folder_id
    global folder_note_id
    user_folder_id = folder_id
    folder_note_id = None
    return redirect('/main')


@app.route('/load_note_id/<int:note_id>')
@login_required
def load_note_id(note_id):
    global folder_note_id
    folder_note_id = note_id
    return redirect('/main')


@app.route('/add_note')
@login_required
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


@app.route('/add_folder')
@login_required
def add_folder():
    print(login_user_id, '/add_folder')
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


@app.route('/delete_note')
@login_required
def delete_note():
    global folder_note_id
    requests.delete(f'http://127.0.0.1:9999/api/note/{folder_note_id}', json={'apikey': admin})
    folder_note_id = None
    return redirect('/main')


@app.route('/delete_folder')
@login_required
def delete_folder():
    global user_folder_id
    requests.delete(f'http://127.0.0.1:9999/api/folder/{user_folder_id}', json={'apikey': admin})
    user_folder_id = None
    return redirect('/main')


@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():
    notes = []
    content = ''
    if request.method == 'POST':
        button = request.form.get('btn')
        if button == 'Сохранить':
            if folder_note_id:
                save_content = request.form.get('content')
                if "\n" in save_content:
                    name = save_content[:save_content.find('\n')]
                else:
                    name = save_content
                json_save = {
                    'apikey': admin,
                    'name': name,
                    'content': save_content
                }
                save_req = requests.put(f'http://127.0.0.1:9999/api/note/{folder_note_id}', json=json_save)
                if not save_req:
                    print('Сайт упал')
                    print(f'Причина: {save_req.text}')
                    quit()
            else:
                return render_template('/main.html', message='Before saving smth select note')
        elif button == 'Исправить':
            json_data = {
                'apikey': admin,
                "content": request.form.get('content')
            }
            content_req = requests.get(f'http://127.0.0.1:9999//api/drive_through_gpt', json=json_data)
            if content_req.status_code == 500:
                return redirect('/main')
            if content_req:
                content = content_req.json()['content']

    json_data = {
        'apikey': admin
    }
    folders_req = requests.get(f'http://127.0.0.1:9999/api/folders/{login_user_id}', json=json_data)
    if folders_req.status_code == 500:
        return redirect('/main')
    if folders_req:
        folders = folders_req.json()['folders']
    else:
        folders = []
    if user_folder_id:
        notes_req = requests.get(f'http://127.0.0.1:9999/api/notes/{user_folder_id}', json=json_data)
        if notes_req:
            notes = notes_req.json()['notes']
        if folder_note_id and not content:
            content_req = requests.get(f'http://127.0.0.1:9999/api/note/{folder_note_id}', json=json_data)
            if content_req:
                content = content_req.json()['note']['content']

    return render_template('main.html', list_of_folders=folders, list_of_notes=notes, note_content=content)


api.add_resource(user_resources.UsersListResource, '/api/users')
api.add_resource(user_resources.UsersResource, '/api/user/<int:user_id>')
api.add_resource(folder_resources.FoldersListResource, '/api/folders/<int:user_id>')
api.add_resource(folder_resources.FoldersResource, '/api/folder/<int:folder_id>')
api.add_resource(note_resources.NotesListResource, '/api/notes/<int:folder_id>')
api.add_resource(note_resources.NotesResource, '/api/note/<int:note_id>')
api.add_resource(drive_through_GPT_resources.DriveThroughGPTResource, '/api/drive_through_gpt')

if __name__ == '__main__':
    login_user_id = None
    user_folder_id = None
    folder_note_id = None
    global_init('db/online_notebook.db')
    app.run(host='127.0.0.1', port=9999)
