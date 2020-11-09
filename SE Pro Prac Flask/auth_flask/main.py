from flask.wrappers import Request
from auth_flask.Member import Member
from datetime import timedelta
from os import name
from flask import Blueprint, render_template,flash,url_for,redirect
from flask.globals import request
# from flask.helpers import flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
# from werkzeug.utils import redirect
from . import db
from .models import MemberTable, User,booktable,IssueTable,ReserveTable
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
            books=booktable.query.with_entities(booktable.Title,booktable.RequestedBy,booktable.ISBN)\
                .filter(booktable.Requested==True).all()
            return render_template('IssueBook.html',results=books)
        else:
            books=booktable.query.with_entities(booktable.RequestedBy,booktable.ISBN)\
                .filter(booktable.ISBN==request.form['options']).first()
            resp=Librarian.Librarian(name=current_user.name).Issue(memcode=books[0],isbn=books[1])
            if not resp[0] and resp[1]==0:
                flash("Can't issue any more Book as Limit Reached for The Member!!")
            elif not resp[0] and resp[1]==1:
                flash("Can't Issue Book Already Reserved")
            else:
                flash("Request for book with ISBN {} by {} is be granted ".format(books[1],books[0]))

            booktable.query.filter_by(ISBN=request.form['options'])\
                .update({booktable.Requested:False,booktable.RequestedBy:None})
            db.session.commit()
            # print("$$$$"*100)
            # print(books)
            flash("Request for book with ISBN {} by {} is be granted ".format(books[1],books[0]))
            return redirect(url_for('main.IssueBook'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/returnBook',methods=['GET','POST'])
@login_required
def ReturnBook():
    if current_user.type=='admin':
        if request.method=='GET':
            book=IssueTable.query.with_entities(IssueTable.ISBN,IssueTable.MembershipCode,IssueTable.DeadLine).all()
            return render_template('ReturnBook.html',books=book)
        else:
            # pass
            isbn=request.form.get('options')
            book=IssueTable.query.with_entities(IssueTable.MembershipCode).filter_by(ISBN=isbn).first()
            Librarian.Librarian(name=current_user.name).Return(isbn=isbn,memcode=book[0],op=2)
            flash("Book with ISBN {} borrowed by Member with MembershipCode {} is Successfully Returned !".format(isbn,book[0]))
            return redirect(url_for('main.ReturnBook'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/bill',methods=['POST'])
@login_required
def Bill():
    if current_user.type=='admin':
        isbn=request.form.get('options')
        book=IssueTable.query.with_entities(IssueTable.MembershipCode).filter_by(ISBN=isbn).first()
        ans=Librarian.Librarian(name=current_user.name).Return(isbn=isbn,memcode=book[0],op=1)
        if ans[0]:
            flash(ans[1])
        else:
            flash("No Bill needed")
            # return redirect(url_for('main.ReturnBook'))
        return render_template('Bill.html',isbn=isbn)
    else:
        flash("You are not Authorised !!")
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

@main.route('/search',methods=['GET','POST'])
@login_required
def Search():
    if current_user.type=='user':
        if request.method == 'GET':
            return render_template('search.html')
        else:
            Name=request.form['Name']
            Author=request.form['Author']
            Publisher=request.form['Publisher']
            ISBN=request.form['ISBN']
            results=Member(MembershipCode=current_user.otherinfo).search(
                ISBN=ISBN,
                Title=Name,
                Author=Author,
                Publisher=Publisher
            )
            if len(results)!=0:
                return render_template('search.html',results=results,form=request.form)
            else:
                flash("No Matches for the Given Combo. Try and Change it.")
                return render_template('search.html',form=request.form)
            # return redirect(url_for('main.Search'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/requestIssue',methods=['POST'])
@login_required
def RequestIssue():
    if current_user.type=='user':
        mem=MemberTable.query.with_entities(MemberTable.Num_Of_Books_To_Be_Issued)\
            .filter(MemberTable.MembershipCode==current_user.otherinfo).first()
        if mem[0]!=0:
            booktable.query.filter(booktable.ISBN==request.form['options'])\
                .update({booktable.Requested:True,booktable.RequestedBy:current_user.otherinfo},synchronize_session=False)
            db.session.commit()
            # print(request.form['options'])
            flash("Book with ISBN {} is Requested to Reserve.".format(request.form['options']))
        else:
            flash("Limit Reached!!!!Cannot Issue Anymore Book!!!! Return Some!! Contact librarian!!")
        return redirect(url_for('main.Search'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))

@main.route('/reserve',methods=['GET','POST'])
@login_required
def Reserve():
    if current_user.type=='user':
        if request.method == 'GET':
            subquerys=ReserveTable.query.with_entities(ReserveTable.ISBN).subquery()
            results=IssueTable.query.with_entities(IssueTable.ISBN)\
                .filter(~IssueTable.ISBN.in_(subquerys),IssueTable.MembershipCode!=current_user.otherinfo)\
                    .subquery()
            books=booktable.query.with_entities(booktable.Title,booktable.Author,booktable.ISBN,booktable.Publisher).filter(booktable.ISBN.in_(results)).all()
            return render_template('Reserve.html',results=books)
        else:
            isbn=request.form.get('options')
            resp=Member(MembershipCode=current_user.otherinfo).reserve(isbn=isbn)

            if not resp[0]:
                flash(resp[1])
            else:
                flash("Book with ISBN {} is Reserved for You. When Alerted please drop a Issue Request within 7 Days or else Reservation will Expire!")
            return redirect(url_for('main.Reserve'))
    else:
        flash('You are Not Authorised!!')
        return redirect(url_for('main.index'))