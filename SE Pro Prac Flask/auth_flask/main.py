from datetime import timedelta
from os import name
from flask import Blueprint, render_template,flash,url_for,redirect
from flask.globals import request
# from flask.helpers import flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
# from werkzeug.utils import redirect
from . import db
from .models import User,booktable
from . import Librarian
import datetime
main = Blueprint('main', __name__)

@main.route('/')
def index():
    if User.query.filter_by(email='admin@admin.com').first() is None:
        db.session.add(
        User(email='admin@admin.com', name='Superuser', password=generate_password_hash('Admin', method='sha256'),type='superuser',activated=True)
        )
        db.session.add(
            booktable(
                ISBN="123",
                Title="Title",
                Author="Author",
                Publisher="Publisher",
                Rack=1,
                LastIssued=datetime.date.today(),#-timedelta(days=6*365),
                Available=True
            )
        )
        db.session.commit()
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html',name=current_user.name)


@main.route('/newAdmin',methods=['GET','POST'])
@login_required
def LibrarianGeneration():
    if current_user.type=='superuser':
        if request.method=='GET':
            return render_template('newAdmin.html')
        elif request.method=='POST':
            # code to validate and add user to database goes here
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')
            if password == '' or password=='Password':
                flash('Enter Valid Password')
                return redirect(url_for('main.LibrarianGeneration'))

            user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

            if user: # if a user is found, we want to redirect back to signup page so user can try again
                flash('Email address already exists')
                return redirect(url_for('main.LibrarianGeneration'))

            # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'),type='admin',activated=True)

            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index'))


@main.route('/addMem',methods=['GET','POST'])
@login_required
def AddMember():
    if current_user.type=='admin':
        if request.method=='GET':
            users=User.query.filter_by(activated=False).all()
            return render_template('AddMember.html',users=users)
        else:
            email=request.form['options']
            if email:
                user=User.query.filter_by(email=email).first()
                
                # Call Add Member Function from the Bussiness Logic
                MembershipCode=Librarian.Librarian(name=current_user.name).ManageMember(
                    choice=1,
                    name=user.name,
                    Category=user.otherinfo,
                    email=user.email
                    )
                db.session.query(User).filter(User.email==email)\
                    .update({User.activated:True,User.otherinfo:MembershipCode},synchronize_session=False)
                db.session.commit()
                flash('Member Added')
            return redirect(url_for('main.AddMember'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/removeMem',methods=['GET','POST'])
@login_required
def RemoveMember():
    if current_user.type=='admin':
        if request.method=='GET':
            users=User.query.filter_by(type='user').all()
            return render_template('RemoveMember.html',users=users)
        else:
            email=request.form['options']
            if email:
                user=User.query.filter_by(email=email).first()
                db.session.query(User).filter(User.email==email)\
                    .delete(synchronize_session=False)
                # Call Remove Member Function from the Bussiness Logic
                Librarian.Librarian(name=current_user.name).ManageMember(
                    choice=0,
                    MembershipCode=user.otherinfo
                    )
                db.session.commit()
                flash('Member Removed')
            return redirect(url_for('main.RemoveMember'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/addBook',methods=['GET','POST'])
@login_required
def AddBook():
    if current_user.type=='admin':
        if request.method == 'GET':
            return render_template('AddBook.html')
        else:
            name=request.form['Name']
            if name == "":
                flash('Enter a Book Name Please')
                return redirect(url_for('main.AddBook'))
            author=request.form['Author']
            if author == "":
                flash('Enter a Book Author Please')
                return redirect(url_for('main.AddBook'))
            Pub=request.form['Publisher']
            if Pub == "":
                flash('Enter a Book Publisher Please')
                return redirect(url_for('main.AddBook'))
            rack=request.form['Rack']
            if rack == "":
                flash('Enter Rack Number Please')
                return redirect(url_for('main.AddBook'))
            num=request.form.get('NumOfBooks')
            if  num== "":
                flash('Enter Number of Books Please')
                return redirect(url_for('main.AddBook'))
            lis=Librarian.Librarian(name=current_user.name).BookManage(
                choice=1,
                name=name,
                author=author,
                pub=Pub,
                rack=rack,
                num=num
            )
            return render_template('show.html',name=name,author=author,Pub=Pub,rack=rack,lis=lis)
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/remBook',methods=['GET','POST'])
@login_required
def RemoveBook():
    if current_user.type=='admin':
        if request.method == 'GET':
            books=booktable.query.filter_by(Available=True).all()
            return render_template('RemoveBook.html',books=books)
        else:
            isbn=request.form['options']
            if isbn:
                # Call Remove Member Function from the Bussiness Logic
                resp=Librarian.Librarian(name=current_user.name).BookManage(
                    choice=0,
                    ISBN=isbn
                    )
                if resp[0]:
                    flash('Book with ISBN {} is Removed'.format(isbn))
                else:
                    if resp[1]==1:
                        flash('Book with ISBN {} Cannot Be Removed as Issued to Member with ISBN {}'.format(isbn,resp[2]))
                    else:
                        flash('Book with ISBN {} Cannot Be Removed as Reserved by Member with ISBN {}. Check after 7 days.'.format(isbn,resp[2]))
            return redirect(url_for('main.RemoveBook'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/issueBook',methods=["GET","POST"])
@login_required
def IssueBook():
    if current_user.type=='admin':
        if request.method=='GET':
            # return render_template('IssueBook.html')
            pass
        else:
            pass
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/returnBook')
@login_required
def ReturnBook():
    if current_user.type=='admin':
        pass
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/stats',methods=['GET','POST'])
@login_required
def Statistics():
    if current_user.type=='admin':
        if request.method=='GET':
            lis=Librarian.Librarian(name=current_user.name).Stats()
            return render_template('Stats.html',books=lis)
        else:
            isbn=request.form['options']
            if isbn:
                # Call Remove Member Function from the Bussiness Logic
                resp=Librarian.Librarian(name=current_user.name).BookManage(
                    choice=0,
                    ISBN=isbn
                    )
                if resp[0]:
                    flash('Book with ISBN {} is Removed'.format(isbn))
                else:
                    if resp[1]==1:
                        flash('Book with ISBN {} Cannot Be Removed as Issued to Member with ISBN {}'.format(isbn,resp[2]))
                    else:
                        flash('Book with ISBN {} Cannot Be Removed as Reserved by Member with ISBN {}. Check after 7 days.'.format(isbn,resp[2]))
            return redirect(url_for('main.Statistics'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/overdue',methods=['GET','POST'])
@login_required
def Overdue():
    if current_user.type=='admin':
        lis=Librarian.Librarian(name=current_user.name).Overdue()
        if request.method == 'GET':
            # ALERT ALERT CHANGE IT AFTERWARDS
            return render_template('Overdue.html',lis=[{'name':'Subhasish','MembershipCode':'123'}])
        else:
            """
            Send Email
            """
            # ALERT ALERT CHANGE IT AFTERWARDS
            flash("Message Sent to All the Defaulters.")
            return redirect(url_for('main.Overdue'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/search')
@login_required
def Search():
    if current_user.type=='user':
        pass
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/reserve')
@login_required
def Reserve():
    if current_user.type=='user':
        pass
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))