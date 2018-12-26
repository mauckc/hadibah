from flask import Flask, render_template, request, url_for, redirect, send_from_directory, after_this_request
import os
import json
from utils import readSC, colors, table_convert
from plots import plot_page_mpld3, plot_page_counts, plot_page_los, plot_page_inventory, detail_plot

import sqlite3
from werkzeug.utils import secure_filename
from werkzeug import SharedDataMiddleware
from flask import send_from_directory
from flask import Request, session, g, abort, flash
from time import localtime

# ['index','animal_id','animal_type','sex','primary_bree','dob','secondary_','kennel_no','impound_no','intake_type','intake_subtype','intake_date','s_n_date','intake_cond','weight','weight_1_week','outcome_type','outcome_subtype','outcome_date','due_out_date','outcome_cond','location_1','location_1_date','location_2','location_2_date','behavior_cond','outcome_behavior_cond','euth_reason','intake_date_form_2']

# Setup Flask
app = Flask(__name__)
app.config['DEBUG'] = 'On'

# os.environ['SC_secret'] = '123124kjfdssdffdssz3'
# app.config['SECRET_KEY'] = 'thisisthesecretkey'
# Set the secret key to some random bytes. Keep this really secret!
randomkey = os.urandom(16)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.config['DEBUG_MODE'] = 1
# app.config['SECRET_KEY'] = os.environ['SC_secret']

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['csv','xls','txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# I assume this is number of bits bytes in 1 Gigabyte
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists('uploads'):
    os.mkdir('uploads')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'hadibah.db'),
    USER_DATABASE=os.path.join(app.root_path,'hadibahUsers.db'),
    SECRET_KEY='thisisthesecretkey!215',
    ADMINUSERNAME='mossrock',
    ADMINPASSWORD='Sharpie17!',
    ADPASS = 'Sharpie17!',
    ADUSER = 'mossrock'
))

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def connect_USER_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['USER_DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_USER_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_USER_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def init_USER_db():
    db = get_USER_db()
    with app.open_resource('userSchema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.cli.command('initUSERdb')
def initUSERdb_command():
    """Initializes the database."""
    init_USER_db()
    print('Initialized the USER database.')

@app.route('/admin-reset')
def reset_dbs():
    """  Resets databases """
    init_db()
    init_USER_db()
    print('Reset the databases.')
    return redirect(url_for('homepage'))

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/entries')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/')
def homepage():
    if 'username' in session:
        print('Logged in as %s' %session['username'])
        """Home page for Hadibah with updated table"""
        df, _ = readSC()
        dfs = df.sort_values('impound_no', ascending=False)
        cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date','los','days_old','los_1','los_2','age_s_n_date','weight_difference','in_to_due_out_date_diff','due_out_to_outcome_date_diff']
        decimals = dict.fromkeys(cols, 2)
        dfs = dfs.round(decimals=decimals)
        dfs = dfs.to_dict('records')
        return render_template('main.html', rows=dfs)
    else:
        return redirect(url_for("login"))

@app.route('/animal_id/<string:animal_id>/')
def animal_iddetail(animal_id=None):
    """Page with details on the individual system"""
    if animal_id:
        df, _ = readSC()
        # t1, t2 = min(df['intake_date']), max(df['outcome_date'])
        t1, t2 = min(df['los']), max(df['los'])
        index = df['animal_id'] == animal_id
        d = df.loc[index, :].copy()
        if len(d):
            show_intake = bool(~d['los'].isnull().values[0])
            # if show_intake:
            #     s = d['los'].values
            #     s = [si.decode() if isinstance(si, bytes) else si for si in s]
            #     s = ['{} {}'.format(si[:-2], si[-1].lower()) for si in s]
                #d['exolink'] = ['http://exointake.eu/catalog/{}/'.format(si.lower().replace(' ', '_')) for si in s]

            # d['lum'] = (d.teff/5777)**4 * (d.mass/((10**d.logg)/(10**4.44)))**2
            # d['hz1'] = round(hz(d['teff'].values[0], d['lum'].values[0], model=2), 5)
            # d['hz2'] = round(hz(d['teff'].values[0], d['lum'].values[0], model=4), 5)

            if len(d) == sum(d['intake_date'].isnull()):
                plot = None
            else:
                plot = detail_plot(d, t1, t2)
            d.fillna('...', inplace=True)
            info = d.to_dict('records')

            return render_template('detail.html', info=info, show_intake=show_intake, plot=plot)
    return redirect(url_for('homepage'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login to the server """
    error = None
    if request.method == 'POST':
        # Check list of usernames and passwords to check if it matches
        db = get_USER_db()
        cur = db.execute('select username, password from users order by name desc')
        curUsernames = db.execute('select username from users order by name desc')
        curPasswords = db.execute('select password from users order by name desc')
        usernames = curUsernames.fetchall()
        passwords = curPasswords.fetchall()
        auth_list = zip(usernames,passwords)
        usernames_passwords = cur.fetchall()

        # convert cursor object of row objects to strings.
        ite = 0
        lw = []
        for z in auth_list:
            ly = []
            for x in z:
                # print(x)
                # l.append(x)
                l = []
                for y in x:
                    # print(y)
                    l.append(y)
                ly.append(l)
            lw.append(ly)

        # print(lw)
        usernames_passwords = lw
        # print(usernames_passwords[0])
        # # print(auth_list)
        # # print(cur.fetchall())
        # # print(curUsernames)
        # #
        # # print(usernames_passwords) # DBUG!_____________------
        # print((request.form['username'],request.form['password']))
        # print('\n')
        if [[request.form['username']],[request.form['password']]] not in usernames_passwords:
            error = 'Invalid username and/or password'
            flash('Sign up if you do not already have an account')
        else:
            session['username'] = request.form['username']
            session['logged_in'] = True
            flash('Welcome {}! You were successfully logged in. '.format(request.form['username']))
            session.pop('admin', None)
            return redirect(url_for('homepage'))

        # if request.form['username'] != app.config['USERNAME']:
        #     error = 'Invalid username'
        # elif request.form['password'] != app.config['PASSWORD']:
        #     error = 'Invalid password'
        # else:
        #     session['username'] = request.form['username']
        #     session['logged_in'] = True
        #     flash('You were logged in')
        #     return redirect(url_for('homepage'))
    return render_template('login.html', error=error)

@app.route('/admin-server', methods=['GET', 'POST'])
def admin_login():
    """ Login to the admin server """
    error = None

    if 'admin' not in session:
        session['admin'] = False

    if not session['admin']:
        if request.method == 'POST':
            if request.form['username'] != app.config['ADUSER'] or request.form['password'] != app.config['ADPASS']:
                if 'username' in session:
                    flash('Invalid login attempt {}'.format(session['username']))
                error = 'Invalid username and/or password.'
                flash('Invalid login attempt')
            # elif session['username'] != app.config['ADUSER']:
            #     error = 'Invalid username and/or password.'
            #     flash('Invalid login attempt')
            else:
                # session['username'] = request.form['username']
                session['admin'] = True
                session['logged_in'] = True
                flash('Welcome {}! You were successfully logged in. '.format(request.form['username']))

                db = get_USER_db()
                cur = db.execute('select name, username, password, email from users order by username desc')
                users = cur.fetchall()
                return render_template('admin.html', users=users)

        return render_template('admin.html')

    else:
        # session['admin'] = True
        # Already logged in as admin
        # session['admin'] = True
        session['logged_in'] = True
        session['username'] = 'admin'
        flash('Welcome {} Admin! You were already logged in. '.format(session['admin']))

        db = get_USER_db()
        cur = db.execute('select name, username, password, email from users order by username desc')
        users = cur.fetchall()
        return render_template('admin.html',users=users)

    return render_template('admin.html')



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    # session.pop('password', None)
    # session.pop('admin', False)
    session['admin'] = False
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/uploads', methods=['GET','POST'])
def upload_file():
    if 'username' in session:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('upload_file',
                                        filename=filename))
        return render_template('upload.html')
    else:
        return redirect(url_for("login"))

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

@app.route("/publications/")
def publications():
    """Show relevant publications for Hadibah"""
    with open('data/publications.json') as pubs:
        pubs = json.load(pubs)
    return render_template('publications.html', publications=pubs)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def error_404(error):
    """Simple handler for status code: 404"""
    return render_template('404.html')

@app.route('/download/<path:fname>')
def download(fname):
    """Download data table in different formats and clean afterwards"""
    if 'username' in session:
        if fname.startswith('animals'):
            print(fname)
            fmt = fname.split('.')[-1]
            if fmt in ['csv', 'hdf','xls']:
                table_convert(fmt=fmt)

                @after_this_request
                def remove_file(response):
                    try:
                        pass
                        # os.remove('data/{}'.format(fname))
                    except OSError:  # pragma: no cover
                        pass  # pragma: no cover
                    return response
            return send_from_directory('data', fname)
        else:
            return send_from_directory('data', fname)
    else:
        return redirect(url_for("login"))

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """ Have user go to sign up page """
    error = None
    if request.method == 'POST':
        """ Parse the input data form """
        """ MUST ADD IN ADD FORM INFO TO USERS LIST """
        """ THIS WILL REQUIRE LOGIN AUTHENTICATION TO WORK DIFFERENTLY """
        """ remove below because it is too strict"""
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']

        print('{}, {}, {}, {}'.format(username, password, email, name))

        if request.form['username'] == app.config['ADMINUSERNAME']:
            error = 'Invalid username. User already exists.'
        elif len(request.form['password']) < 6:
            error = 'Invalid password. A minimum of 5 characters are required.'
        else:
            session['username'] = request.form['username']
            session['logged_in'] = True
            flash('We have received your request!')

            db = get_USER_db()
            db.execute('insert into users (name, username, password, email) values (?, ?, ?, ?)',
                         [request.form['name'], request.form['username'], request.form['password'], request.form['email']])
            db.commit()
            flash('New entry was successfully posted')
            return redirect(url_for('homepage'))
    return render_template('signup.html', error=error)

# :5000/filter?field=alex&value=pw1
@app.route('/filter/',methods=['GET','POST'])
def filter():
    if 'username' in session:
        field = request.args.get('field')
        value = request.args.get('value')
        df, _ = readSC()
        filterdf = df[df[str(field)] == value]
        filterdfs = filterdf.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
        cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date']
        decimals = dict.fromkeys(cols, 2)
        filterdfs = filterdfs.round(decimals=decimals)
        # df = df[(df['intake_type']!="DEAD")&(df['intake_subtype']!="DEAD")&(df['intake_cond']!="DEAD")&(df['intake_type']!="DISPOSAL")&(df['intake_subtype']!="DISPOSAL")&(df['intake_cond']!="DISPOSAL")&(df['intake_type']!="DECEASED")&(df['intake_subtype']!="DECEASED")&(df['intake_cond']!="DECEASED")]
        filterdfs = filterdfs.to_dict('records')
        return render_template('main.html', rows=filterdfs)
    else:
        flash('Sign up if you do not already have an account')
        return redirect(url_for('login'))

@app.route("/linked/", methods=['GET', 'POST'])
def linked_plot():
    """Plot inventory over time"""
    if 'username' in session:
        df, columns = readSC()
        # print(", ".join(((df, columns))))
        return plot_page_mpld3(df, columns, request)
    else:
        return redirect(url_for('login'))

@app.route('/linked-filter/',methods=['GET','POST'])
def linked_plot_filter():
    if 'username' in session:
        field = request.args.get('field')
        value = request.args.get('value')
        df, columns = readSC()
        filterdf = df[df[str(field)] == value]
        return plot_page_mpld3(filterdf, columns, request, field=field, value=value)
    else:
        return redirect(url_for('login'))

@app.route("/counts/", methods=['GET', 'POST'])
def counts_plot():
    """Plot inventory over time"""
    if 'username' in session:
        df, columns = readSC()
        dfs = df.sort_values('impound_no', ascending=False)
        cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date','los','days_old','los_1','los_2','age_s_n_date','weight_difference','in_to_due_out_date_diff','due_out_to_outcome_date_diff']
        decimals = dict.fromkeys(cols, 2)
        dfs = dfs.round(decimals=decimals)
        dfs = dfs.to_dict('records')
        return plot_page_counts(df, columns, request, rows=dfs)
    else:
        return redirect(url_for('login'))

@app.route('/counts-filter/',methods=['GET','POST'])
def counts_plot_filter():
    if 'username' in session:
        field = request.args.get('field')
        value = request.args.get('value')
        df, columns = readSC()
        filterdf = df[df[str(field)] == value]
        dfs = filterdf.sort_values('impound_no', ascending=False)
        cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date','los','days_old','los_1','los_2','age_s_n_date','weight_difference','in_to_due_out_date_diff','due_out_to_outcome_date_diff']
        decimals = dict.fromkeys(cols, 2)
        dfs = dfs.round(decimals=decimals)
        dfs = dfs.to_dict('records')
        return plot_page_counts(filterdf, columns, request, field=field, value=value, rows=dfs)
    else:
        return redirect(url_for('login'))

@app.route("/length-of-stay/", methods=['GET', 'POST'])
def los_plot():
    """Plot inventory over time"""
    if 'username' in session:
        df, columns = readSC()
        dfs = df.sort_values('impound_no', ascending=False)
        cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date','los','days_old','los_1','los_2','age_s_n_date','weight_difference','in_to_due_out_date_diff','due_out_to_outcome_date_diff']
        decimals = dict.fromkeys(cols, 2)
        dfs = dfs.round(decimals=decimals)
        dfs = dfs.to_dict('records')
        return plot_page_los(df, columns, request, rows=dfs)
    else:
        return redirect(url_for('login'))

@app.route('/length-of-stay-filter/',methods=['GET','POST'])
def los_plot_filter():
    if 'username' in session:
        field = request.args.get('field')
        value = request.args.get('value')
        df, columns = readSC()
        filterdf = df[df[str(field)] == value]
        dfs = filterdf.sort_values('impound_no', ascending=False)
        cols = ['animal_id','animal_type','impound_no','intake_type','intake_subtype','intake_cond','outcome_type','outcome_subtype','outcome_cond','weight','intake_date','outcome_date','dob','primary_bree','secondary_','kennel_no','s_n_date','weight_1_week','due_out_date','location_1','location_1_date','location_2','location_2_date','los','days_old','los_1','los_2','age_s_n_date','weight_difference','in_to_due_out_date_diff','due_out_to_outcome_date_diff']
        decimals = dict.fromkeys(cols, 2)
        dfs = dfs.round(decimals=decimals)
        dfs = dfs.to_dict('records')
        return plot_page_los(filterdf, columns, request, field=field, value=value, rows=dfs)
    else:
        return redirect(url_for('login'))

@app.route("/inventory/", methods=['GET', 'POST'])
def inventory_plot():
    """Plot inventory over time"""
    if 'username' in session:
        df, columns = readSC()
        return plot_page_inventory(df, columns, request)
    else:
        return redirect(url_for('login'))

@app.route('/inventory-filter/',methods=['GET','POST'])
def inventory_plot_filter():
    if 'username' in session:
        field = request.args.get('field')
        value = request.args.get('value')
        # print(", ".join((field, value)))
        df, columns = readSC()
        filterdf = df[df[str(field)] == value]
        # filterdfs = filterdf.sort_values('impound_no', ascending=False)  # [:50]  # TODO: Remove the slicing!
        return plot_page_inventory(filterdf, columns, request, field=field, value=value)
    else:
        return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)
