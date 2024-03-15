from flask import Flask, render_template
from data.db_session import global_init, create_session

app = Flask(__name__)
app.secret_key = 'online_notebook_project'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='9999')
