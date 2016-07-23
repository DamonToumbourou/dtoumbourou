import os
import sqlite3
import private
from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash

# Create application
app = Flask(__name__)
app.config.from_object(__name__)

# Load defualt config and override config from enviorment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'dtoumbourou.db'),
    SECRET_KEY=private.SECRET_KEY,
    USERNAME='admin',
    PASSWORD=private.PASSWORD,
))

app.config.from_envvar('DTOUMBOUROU_SETTINGS', silent=True)

def connect_db():
    """Coneccts to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Init the database"""
    init_db()
    print """Initialized the database."""

def get_db():
    """Opens a new database connection if there is none yet for the current app"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """closes the database at end of request"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title
