from flask import Flask, g, render_template, redirect, url_for, request, flash
import os
import sqlite3

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

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


def insert_into_events():
    db = get_db()
    cur = db.execute("insert into event (event_quantity, event_type, event_occurrence) values (10.0, 'sms', CURRENT_TIMESTAMP)")
    cur = db.execute("insert into event (event_quantity, event_type, event_occurrence) values (13.45, 'call', CURRENT_TIMESTAMP)")
    cur = db.execute("insert into event (event_quantity, event_type, event_occurrence) values (19.3, 'data', CURRENT_TIMESTAMP)")
    cur = db.execute("insert into event (event_quantity, event_type, event_occurrence) values (12.0, 'call', CURRENT_TIMESTAMP)")
    db.commit()

def insert_allowed_usage():
    db = get_db()
    cur = db.execute("insert into allowed_usage (sms,calls,data) values (100.0, 1000.0, 3000.0)")
    db.commit()

@app.route('/events')
def show_events():
    db = get_db()
    #insert_into_events()
    cur = db.execute('select * from event order by event_occurrence desc')
    entries = cur.fetchall()
    print entries
    calc_curr_usage()
    cur = db.execute('select * from current_usage where id=1')
    curr_usg = cur.fetchall()
    print curr_usg
    insert_allowed_usage()
    cur = db.execute('select * from allowed_usage where id=1')
    all_usg = cur.fetchall()
    return render_template('events.html', entries=entries, curr_usg=curr_usg, all_usg=all_usg)

#@app.route('/convtable')
#def show_conversion():
#    db = get_db()
#    cur = db.execute('select * from conversion_table')
#    entries = cur.fetchall()
#    return render_template('convrt.html', entries=entries)

#Decided to comment this to remove the conversion_table, will use dict instead
#def insertconv():
#    db = get_db()
#    cur = db.execute('insert into conversion_table (sms2call, sms2data, call2data, call2sms, data2call, data2sms)
#    values (2.0, 10.0, 5.0, 0.5, 0.2, 0.1)')
#    flash('Conversion table populated with default values')

@app.route('/addevent', methods = ['POST', 'GET'])
def add_event():
    db = get_db()
    if request.method == 'POST':
        db.execute("insert into event (event_quantity, event_type, event_occurrence) values (?,?,CURRENT_TIMESTAMP)",\
                [request.form['event_quant'], request.form['event_type']])
        db.commit()
        flash('New event was successfully posted')
    return render_template('addevent.html')

def calc_curr_usage():
    db = get_db()
    curs = db.execute("update current_usage set sms =  (select sum(event_quantity) from event where event_type = 'sms')")
    db.commit()
    curs = db.execute("update current_usage set calls = (select sum(event_quantity) from event where event_type = 'call')")
    db.commit()
    curs = db.execute("update current_usage set data = (select sum(event_quantity) from event where event_type = 'data')")
    db.commit()
    return redirect(url_for('show_events'))

@app.route('/convert', methods = ['POST', 'GET'])
def convert():
    #sms2call, sms2data, call2data, call2sms, data2call, data2sms
    convert_dict = {'sms2call':2.0, 'sms2data':10.0, 'call2data':5.0, 'call2sms':0.5, 'data2call':0.2, 'data2sms':0.1}
    db = get_db()
    if request.method == 'POST':
        conv_req = request.form['conversion_req'] # Conversion request radio buttons
        conv_quant = request.form['conversion_quant'] # Conversion quantity user input. USER INPUT SANITY CHECK NOT IMPLEMENTED
        conv_quant = float(conv_quant)
        print conv_quant
        print conv_req
        db.execute("insert into event (event_quantity, event_type, event_occurrence) values (1.0,'conv', CURRENT_TIMESTAMP)")
        db.commit()
        flash('Conversion requested')
        cur = db.execute("select sms from allowed_usage where id=1") 
        au_sms = cur.fetchone()
        au_sms = au_sms[0]
        print au_sms
        cur = db.execute("select sms from current_usage where id=1")
        cu_sms = cur.fetchone()
        cu_sms = cu_sms[0]
        print cu_sms
        cur = db.execute("select calls from allowed_usage where id=1")
        au_call = cur.fetchone()
        au_call = au_call[0]
        print au_call
        cur = db.execute("select calls from current_usage where id=1")
        cu_call = cur.fetchone()
        cu_call = cu_call[0]
        print cu_call
        cur = db.execute("select data from allowed_usage where id=1")
        au_data = cur.fetchone()
        au_data = au_data[0]
        print au_data
        cur = db.execute("select data from current_usage where id=1")
        cu_data = cur.fetchone()
        cu_data = cu_data[0]
        print cu_data
        diff_sms = au_sms - cu_sms

        if str(conv_req) == 'sms2call':
            print "Diff is ", diff_sms
            if conv_quant < diff_sms:
                # Increase allowed call usage and decrease allowed sms usage
                print convert_dict['sms2call']
                to_increase = conv_quant * convert_dict['sms2call']
                to_decrease = conv_quant
                fin_call = (au_call - cu_call) + to_increase
                fin_sms = (au_sms - cu_sms) - to_decrease
                db.execute("update allowed_usage set calls = ?, sms = ?",(fin_call,fin_sms))
                db.commit()
        if conv_req == 'sms2data':
             if (conv_quant < (au_sms - cu_sms)):
                # Increase allowed data usage and decrease allowed sms usage
                to_increase = conv_quant * convert_dict['sms2data']
                print to_increase
                to_decrease = conv_quant
                print to_decrease
                fin_data = (au_data - cu_data) + to_increase
                fin_sms = (au_sms - cu_sms) - to_decrease
                db.execute("update allowed_usage set calls = ?, sms = ?",(fin_data, fin_sms))
                db.commit()
        if conv_req == 'call2data':
            if (conv_quant < (au_call - cu_call)):
                # Increase allowed data usage and decrease allowed call usage
                to_increase = conv_quant * convert_dict['call2data']
                print to_increase
                to_decrease = conv_quant 
                print to_decrease
                fin_data = (au_data - cu_data) + to_increase
                fin_call = (au_call - cu_call) - to_decrease
                db.execute("update allowed_usage set data= ?, calls = ?",(fin_data, fin_call))
                db.commit()
        if conv_req == 'call2sms':
            if (conv_quant < (au_call - cu_call)):
                # Increase allowed sms usage and decrease allowed call usage
                to_increase = conv_quant * convert_dict['call2sms']
                print to_increase
                to_decrease = conv_quant 
                print to_decrease
                fin_sms = (au_data - cu_data) + to_increase
                fin_call = (au_sms - cu_sms) - to_decrease
                db.execute("update allowed_usage set sms = ?, calls = ?",(fin_sms, fin_call))
                db.commit()
        if conv_req == 'data2call':
            if (conv_quant < (au_data - cu_data)):
                # Increase allowed call usage and decrease allowed data usage
                to_increase = conv_quant * convert_dict['data2call']
                print to_increase
                to_decrease = conv_quant
                print to_decrease
                fin_call = (au_call - cu_call) + to_increase
                fin_data = (au_data - cu_data) - to_decrease
                db.execute("update allowed_usage set calls = ?, data = ?",(fin_call, fin_data))
                db.commit()
        if conv_req == 'data2sms':
            if (conv_quant < (au_data - cu_data)):
                # Increase allowed sms usage and decrease allowed data usage
                to_decrease = conv_quant * convert_dict['data2sms']
                print to_increase
                to_increase = conv_quant
                print to_decrease
                fin_sms = (au_sms - cu_sms) + to_increase
                fin_data = (au_data - cu_data) - to_decrease
                db.execute("update allowed_usage set sms = ?, data = ?",(fin_sms, fin_data))
                db.commit()
    return render_template('convert.html')
