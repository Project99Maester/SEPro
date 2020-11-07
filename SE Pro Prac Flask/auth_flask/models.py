from . import db
from flask_login import UserMixin

# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column,Integer,String,Date,Boolean

# Base=declarative_base()
class booktable(db.Model):
    __tablename__='booktable'
    ISBN=db.Column(db.String(10),primary_key=True)
    Title=db.Column(db.String(100),nullable=False)
    Author=db.Column(db.String(100),nullable=False)
    Publisher=db.Column(db.String(100),nullable=False)
    Rack=db.Column(db.Integer,nullable=False)
    LastIssued=db.Column(db.Date,nullable=True)
    Available=db.Column(db.Boolean,nullable=False)
    Requested=db.Column(db.Boolean,nullable=False,default=False)
    RequestedBy=db.Column(db.String(10),nullable=True)
    
    def __repr__(self):
        return "<Book(title='{}',ISBN='{}', author='{}')>"\
            .format(self.Title,self.ISBN,self.Author)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    type = db.Column(db.String(10))
    activated = db.Column(db.Boolean)
    otherinfo=db.Column(db.String(50))


class MemberTable(db.Model):
    __tablename__='MemberTable'
    MembershipCode=db.Column(db.String(10),primary_key=True)
    Name=db.Column(db.String(100),nullable=False)
    Category=db.Column(db.String(20),nullable=False)
    Num_Of_Books_To_Be_Issued=db.Column(db.Integer,nullable=False)
    email=db.Column(db.String(100),nullable=False)
    
    def __repr__(self):
        return "<Member(Name='{}',MembershipCode='{}',email='{}')>"\
            .format(self.Name,self.MembershipCode,self.email)

class IssueTable(db.Model):
    __tablename__='IssueTable'
    ISBN=db.Column(db.String(10),primary_key=True)
    MembershipCode=db.Column(db.String(10),primary_key=True)
    DeadLine=db.Column(db.Date,nullable=False)
    # Available=db.Column(db.Boolean,nullable=False)
    
    def __repr__(self):
        return "<Issue(ISBN='{}', MembershipCode='{}',Deadline='{}')>"\
            .format(self.ISBN,self.MembershipCode,self.DeadLine)

class ReserveTable(db.Model):
    __tablename__='ReserveTable'
    ISBN=db.Column(db.String(10),primary_key=True)
    MembershipCode=db.Column(db.String(10),primary_key=True)
    DeadLine=db.Column(db.Date,nullable=True)
    
    def __repr__(self):
        return "<Reserve(ISBN='{}', MembershipCode='{}',Deadline='{}')>"\
            .format(self.ISBN,self.MembershipCode,self.DeadLine)