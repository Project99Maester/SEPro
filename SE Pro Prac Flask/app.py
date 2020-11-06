from flask import Flask,render_template
from flask.globals import request
from flask_user import roles_required
app=Flask(__name__)

@app.route('/')
def home():
    return '<h1>Home Bro!</h1>'

@app.route('/Lib')
@roles_required('Li')
def Librarian():
    if request.method=='POST':
        return '<h1>Librarian Section</h1>'
    else:
        return '<h1>Not Authorized</h1>'

@app.route('/Member')
def Member():
    if request.method=='POST':
        return '<h1>Member Section</h1>'
    else:
        return '<h1>Not Authorized</h1>'

@app.route('/add_Member')
def AddMember():
    return '<h1>Add Member Section Bro</h1>'


@app.route('/rem_Member')
def RemoveMember():
    return '<h1>Remove Member Section Bro</h1>'


@app.route('/add_Book')
def AddBook():
    return '<h1>Add Book Section Bro</h1>'


@app.route('/rem_Book')
def RemoveBook():
    return '<h1>Remove Book Section Bro</h1>'
