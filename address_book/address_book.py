import os
import sqlite3
from flask import (Flask, g, render_template, request,
    flash, redirect, url_for, jsonify)

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'address_book.db'),
    )
)

def connect_db():
    """Set row factory to obtain results as a dict instead of a tuple"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()

@app.route('/', methods=['GET'])
def show_main_page():
    return render_template('main.html')

#TODO: logger
@app.route('/contacts', methods=['GET', 'PUT'])
def process_contacts():
    response = {}
    error = None

    if request.method == 'GET':
        contacts, error = list_contacts()
        response['contacts'] = [dict(contact) for contact in contacts]
        
    elif request.method == 'PUT':
        id_, error = create_contact()
        if id_:
            response['id'] = id_

    if error:
        # FIXME: We shouldn't be bubbling direct exception messages!
        return str(error), 500
    return jsonify(response)

@app.route('/contacts/<int:contact_id>', methods=['POST', 'GET', 'DELETE'])
def process_contact_id(contact_id):
    response = {}
    error = None
    status = False

    if request.method == 'POST':
        status, error = edit_contact(contact_id)
    elif request.method == 'DELETE':
        status, error = delete_contact(contact_id)

    if error:
        return str(error), 500

    response['status'] = status
    return jsonify(response)

def list_contacts():
    try:
        db = get_db()
        cur = db.execute("select * from contacts")
        contacts = cur.fetchall()
        return (contacts, '')
    except Exception as e:
        return ([], e)

def create_contact():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("insert into contacts (name, email, phone) values (?, ?, ?)", 
            [request.json['name'], request.json['email'],
             request.json.get('phone', '')])
        db.commit()
        return (cur.lastrowid, '')
    except Exception as e:
        return (False, e)
    
def read_contact():
    pass

def edit_contact(contact_id):
    try:
        db = get_db()
        db.execute("update contacts set name=?, email=?, phone=? where id=?", 
            [request.json['name'], request.json['email'],
             request.json.get('phone', ''), contact_id])
        db.commit()
        return (True, '')
    except Exception as e:
        return (False, e)

def delete_contact(contact_id):
    try:
        db = get_db()
        db.execute("delete from contacts where id=?", [contact_id])
        db.commit()
        return (True, '')
    except Exception as e:
        return (False, e)
