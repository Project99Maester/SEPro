from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Date,Boolean

Base=declarative_base()

class booktable(Base):
    __tablename__='booktable'
    ISBN=Column(String,primary_key=True)
    Title=Column(String,nullable=False)
    Author=Column(String,nullable=False)
    Publisher=Column(String,nullable=False)
    Rack=Column(Integer,nullable=False)
    LastIssued=Column(Date,nullable=True)
    Available=Column(Boolean,nullable=False)
    
    def __repr__(self):
        return "<Book(title='{}',ISBN='{}', author='{}')>"\
            .format(self.Title,self.ISBN,self.Author)

class MemberTable(Base):
    __tablename__='MemberTable'
    MembershipCode=Column(String,primary_key=True)
    Name=Column(String,nullable=False)
    Category=Column(String,nullable=False)
    Num_Of_Books_To_Be_Issued=Column(Integer,nullable=False)
    email=Column(String,nullable=False)
    
    def __repr__(self):
        return "<Member(Name='{}',MembershipCode='{}',email='{}')>"\
            .format(self.Name,self.MembershipCode,self.email)

class IssueTable(Base):
    __tablename__='IssueTable'
    ISBN=Column(String,primary_key=True)
    MembershipCode=Column(String,primary_key=True)
    DeadLine=Column(Date,nullable=False)
    Available=Column(Boolean,nullable=False)
    
    def __repr__(self):
        return "<Issue(ISBN='{}', MembershipCode='{}',Deadline='{}')>"\
            .format(self.ISBN,self.MembershipCode,self.DeadLine)

class ReserveTable(Base):
    __tablename__='ReserveTable'
    ISBN=Column(String,primary_key=True)
    MembershipCode=Column(String,primary_key=True)
    DeadLine=Column(Date,nullable=True)
    
    def __repr__(self):
        return "<Reserve(ISBN='{}', MembershipCode='{}',Deadline='{}')>"\
            .format(self.ISBN,self.MembershipCode,self.DeadLine)