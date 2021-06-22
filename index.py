from flask import Flask
from flask import request
from flask import render_template
from flask import make_response
from flask import session
from flask import redirect
from markupsafe import escape
from werkzeug.exceptions import abort
from packages.core.database import Database

import json

# app = Flask(__name__)
app = Flask(__name__, instance_relative_config=True)

model = Database()

# load config.py in root
app.config.from_object('config')
app.secret_key = 'aserer*&nbds$mori'
app.config.from_pyfile('config.py')
app.config.from_object('config.default')
# app.config['ENV'] = 'development'

# Load the default configuration
# app.config.from_object('config.default')

# Load the configuration from the instance folder
# app.config.from_pyfile('config.py')

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration

"""
--- start.sh is unique to each environment, so it should be left out of version control.
On Heroku, we’ll want to set the environment variables with the Heroku tools.
The same idea applies to other PaaS platforms. ---
# start.sh

APP_CONFIG_FILE=/var/www/yourapp/config/production.py
python run.py
app.config.from_envvar('APP_CONFIG_FILE')
"""


def login_require():
    if 'user_info' not in session:
        abort(status=404)


@app.errorhandler(404)
def error_404(error):
    return render_template('layouts/404.html'), 404


@app.errorhandler(503)
def error_404(error):
    return render_template('layouts/503.html'), 404


@app.route('/')
def index():
    return "<h1>Index Page</h1>"


@app.route('/env')
def test():
    env = app.config['ENV']
    testing = app.config['TESTING']
    return "FALSK_ENV = " + env + " "


"""
Converter Types:
    string: accept any text without a slash
    int: accept positive  integers
    float: accept positive floating point values
    path: like string but also accept slashes
    uuid: accept UUID strings
"""


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    return "Show profile for : %s" % escape(username)


@app.route('/articles/<int:article_id>')
def show_article(article_id):
    return "Article id: {}".format(article_id)


@app.route('/path/<path:subpath>')
def subpath_func(subpath):
    return "Sub path: {path}".format(path=escape(subpath))
    # return "Sub path: %s" % escape(subpath)


@app.route('/simple_post', methods=['POST'])
def simple_request():
    username = request.values.get('username', False)
    password = request.values['password']
    if username == 'mori' and password == '123':
        return "Welcome %s" % username

    return "Username: {0}, Password: {1}".format(username, password)


@app.route('/dashboard')
def dashboard():
    if 'user_info' not in session:
        abort(503)

    result = model.query("SELECT * FROM transactions")
    output = []
    for row in result:
        output.append(row)

    info = json.loads(session['user_info'])
    return render_template('dashboard/dashboard_index.html', user=info, transactions=output)


@app.route('/dashboard/add_transaction', methods=['GET'])
def add_transaction():
    if 'user_info' not in session:
        abort(503)
    params = {'title': 'Add Transaction'}
    return render_template('dashboard/transactions/transaction_add.html', param=params)


@app.route('/dashboard/transactions/<int:trans_id>')
def transaction_detail(trans_id):
    transaction = model.get_transaction(trans_id)

    if transaction is None:
        abort(404)

    return render_template('dashboard/transactions/transaction_detail.html', transaction=transaction)


@app.route('/add_transactions', methods=["POST"])
def add_transaction_row():
    amount = request.values.get('amount', False)
    title = request.values.get('title', False)
    date = request.values.get('date', False)
    return "{title} {amount} {date}".format(title=title, amount=amount, date=date)


@app.route('/login', methods=['GET'])
def login():
    invalid_up = request.values.get('invalid_up', False)
    params = {"title": 'Login Page', "invalid_up": invalid_up}

    return render_template('login.html', param=params)


@app.route('/logout', methods=['GET'])
def logout():
    if 'user_info' in session:
        session.pop('user_info', None)
    return redirect('/login', code=302)


@app.route('/login', methods=['POST'])
def login_do():
    from flask import redirect
    # input_data = request.get_json()
    username = request.values.get('username', '')
    password = request.values.get('password', '')

    if username == 'Mori' and password == '321':
        # set user_id session #
        user_info = {'username': username, 'id': 10}
        session['user_info'] = json.dumps(user_info)
        return redirect('/dashboard', code=302)

    make_response().set_cookie('invalid_up', True)
    return redirect('/login?invalid_up=True', code=302)


@app.route('/input_test', methods=['GET'])
def input_test():
    # name = request.form.get('name')
    username = request.values.get('name', False)
    print(type(username))
    return username


"""
get request items in header
"""


@app.route('/header', methods=['GET'])
def header_info():
    header_vars = request.headers
    return header_vars.get('Authorization', '')
    # return repr(header_vars)


@app.route('/config')
def config_file():
    # n_name = app.config.['N_NAME']
    # return n_name
    app_env = app.config.get('ENV', 'Default value')
    app_env = app.config.get('TEST_VAR', 'Default value')
    return app_env


@app.route('/instance_folder')
def instance_folder():
    pk = app.config['MY_PK']
    return pk


@app.route('/template')
def show_template():
    return render_template('index.html')

# with app.test_request_context():
#     # print(url_for('index'))
#     print(url_for('test', next="/"))
#     print(url_for('profile', username="mori"))
