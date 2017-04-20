app = Flask(__name__) # create the application instance :)
app.config.from_object(config.py) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rating.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

#Usually, it is a good idea to load a separate, environment-specific configuration file. Flask allows you to import multiple configurations and it will use the setting defined in the last import. This enables robust configuration setups. from_envvar() can help achieve this.
#
#Simply define the environment variable FLASKR_SETTINGS that points to a config file to be loaded. The silent switch just tells Flask to not complain if no such environment key is set.
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


#@app.route('/')
#def show_entries():
#    db = get_db()
#    cur = db.execute('select title, text from entries order by id desc')
#    entries = cur.fetchall()
#    return render_template('show_entries.html', entries=entries)
