from auth_flask.DataBase import DataBaseConnection,DataBaseManipulation
from auth_flask.models import ReserveTable,IssueTable,MemberTable,booktable
import datetime

dbConn=DataBaseConnection()

db=DataBaseManipulation(dbConn)

def TestISBNReserved():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(
            ReserveTable(
                ISBN="1234",
                MembershipCode="12345"
                )
            )
    if db.ISBNReserved("1234") and (not db.ISBNReserved("123")):
        print("ISBNReserved is Correct!!")
    else:
        print("ISBNReserved is Incorrect!!")

    dbConn.drop_db()


def TestRemoveIssue():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    is1=IssueTable(
        ISBN="1234",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is2=IssueTable(
        ISBN="12",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is3=IssueTable(
        ISBN="1234",
        MembershipCode="45",
        DeadLine=datetime.date.today()
    )

    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(is1)
        s.add(is2)
        s.add(is3)
    db.RemoveIssue(argISBN="1234",argMembershipCode="12345")
    lis=[]
    with dbConn.session_scope() as s:
        lis=s.query(IssueTable).all()
    if len(lis)==2:
        print("Correct!!!")
    dbConn.drop_db()


def TestIncreaseIssuedBooks():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(
            MemberTable(
                
                MembershipCode="12345",
                Name="Subhasish Kumar Behura",
                Category="5",
                Num_Of_Books_To_Be_Issued=4,
                email="behuracool@gmail.com"
                )
            )
    db.IncreaseIssuedBooks("12345")
    lis=0
    with dbConn.session_scope() as s:
        lis=s.query(MemberTable.Num_Of_Books_To_Be_Issued)\
            .filter(MemberTable.MembershipCode=="12345").first()
    # print(lis)
    if lis[0]==5:
        print("Correct!!!")
    else:
        print("Incorrect!!")

    dbConn.drop_db()


def TestRecordsGT5():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    b1=booktable(ISBN="12",Title="3 cha",Author="chahcha",Publisher="sare",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=6*365),Available=True)
    b2=booktable(ISBN="121",Title="3 cha1",Author="chahcha1",Publisher="sare1",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=7*365),Available=True)
    b3=booktable(ISBN="122",Title="3 cha2",Author="chahcha2",Publisher="sare2",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=5*365-1),Available=True)
    with dbConn.session_scope() as s:
        s.add(b1)
        s.add(b2)
        s.add(b3)
    
    print(db.RecordsGT5())
    

    dbConn.drop_db()

def TestIssueDeadlinePassed():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    is1=IssueTable(
        ISBN="1234",
        MembershipCode="12345",
        DeadLine=datetime.date.today()-datetime.timedelta(days=30)
    )
    with dbConn.session_scope() as s:
        s.add(is1)
        s.add(
            MemberTable(
                MembershipCode="12345",
                Name="Subhasish Kumar Behura",
                Category="5",
                Num_Of_Books_To_Be_Issued=4,
                email="behuracool@gmail.com"
                )
            )
    
    print(db.IssueDeadlinePassed())

    dbConn.drop_db()

def TestInfoBook():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    b1=booktable(ISBN="12",Title="3 cha",Author="chahcha",Publisher="sare",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=6*365),Available=True)
    b2=booktable(ISBN="121",Title="3 cha1",Author="chahcha1",Publisher="sare1",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=7*365),Available=True)
    b3=booktable(ISBN="122",Title="3 cha2",Author="chahcha2",Publisher="sare2",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=5*365-1),Available=True)
    with dbConn.session_scope() as s:
        s.add(b1)
        s.add(b2)
        s.add(b3)
    
    for i in ("12","121","122"):
        print(db.InfoBook(i))
    dbConn.drop_db()

def Testsearch(dic):
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    b1=booktable(ISBN="12",Title="3 cha",Author="chahcha",Publisher="sare",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=6*365),Available=True)
    b2=booktable(ISBN="121",Title="3 cha1",Author="chahcha1",Publisher="sare1",Rack=3,LastIssued=datetime.datetime.now() - datetime.timedelta(days=7*365),Available=True)
    b3=booktable(ISBN="122",Title="3 cha2",Author="chahcha2",Publisher="sare2",Rack=3,Available=True,LastIssued=datetime.datetime.now() - datetime.timedelta(days=5*365-1))
    with dbConn.session_scope() as s:
        s.add(b1)
        s.add(b2)
        s.add(b3)
    
    for i in db.search(dic):
        print(i)
    dbConn.drop_db()

def TestInfoMember():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(
            MemberTable(
                
                MembershipCode="12345",
                Name="Subhasish Kumar Behura",
                Category="5",
                Num_Of_Books_To_Be_Issued=4,
                email="behuracool@gmail.com"
                )
            )
        s.add(
            MemberTable(
                
                MembershipCode="123",
                Name="Subhasish Kumar Behura",
                Category="5",
                Num_Of_Books_To_Be_Issued=4,
                email="behuracool@gmail.com"
                )
            )
    for i in ("12345","123"):
        print(db.InfoMember(i))
    dbConn.drop_db()

def TestIssueExists():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    is1=IssueTable(
        ISBN="1234",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is2=IssueTable(
        ISBN="12",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is3=IssueTable(
        ISBN="1234",
        MembershipCode="45",
        DeadLine=datetime.date.today()
    )

    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(is1)
        s.add(is2)
        s.add(is3)
    print('-'*45)
    print(db.IssueExists(argISBN="2"))
    print('-'*45)
    print(db.IssueExists(argISBN="1234",argMembershipCode="12345"))
    print('-'*45)
    print(db.IssueExists(argMembershipCode="12345"))
    dbConn.drop_db()

def TestReserveExists():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    is1=ReserveTable(
        ISBN="1234",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is2=ReserveTable(
        ISBN="12",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is3=ReserveTable(
        ISBN="1234",
        MembershipCode="45",
        DeadLine=datetime.date.today()
    )

    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(is1)
        s.add(is2)
        s.add(is3)
   
    print(db.ReserveExists(argISBN="1234",argMembershipCode="12345"))
    dbConn.drop_db()

def TestRemoveReserve():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    is1=ReserveTable(
        ISBN="1234",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is2=ReserveTable(
        ISBN="12",
        MembershipCode="12345",
        DeadLine=datetime.date.today()
    )
    is3=ReserveTable(
        ISBN="1234",
        MembershipCode="45",
        DeadLine=datetime.date.today()
    )

    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(is1)
        s.add(is2)
        s.add(is3)
   
    print(db.RemoveReserve(argISBN="1234",argMembershipCode="12345"))
    print('_'*45)
    print(db.ReserveExists(argISBN="1234",argMembershipCode="12345"))
    print('_'*45)
    print(db.ReserveExists(argISBN="1234",argMembershipCode="45"))
    dbConn.drop_db()


def TestChangeDateReserve():
    dbConn.drop_db()
    print("Table Dropped!!!!")
    is1=ReserveTable(
        ISBN="1234",
        MembershipCode="12345"
    )
    
    dbConn.create_db()
    print("Table Created")
    with dbConn.session_scope() as s:
        s.add(is1)
    
    print(db.ReserveExists(argISBN="1234",argMembershipCode="12345"))
    db.ChangeDateReserve(newDate=datetime.date.today(),argISBN="1234")
    print('_'*45)
    print(db.ReserveExists(argISBN="1234",argMembershipCode="12345"))
    
    dbConn.drop_db()

if __name__ == "__main__":
    # TestIssueExists()
    # ab=None
    # if ab is not None:
    #     print("Success")
    # if ab == None:
    #     print("Success1")

    # TestChangeDateReserve()
    
    # date1=datetime.date.today()-datetime.timedelta(days=30)
    # print((datetime.date.today()-date1).days)
    # dbConn.drop_db()
    # dbConn.create_db()
    search={}
    ISBN=input("Enter ISBN: ")
    if len(ISBN)!=0:
        search['ISBN']=ISBN
    Title=input("Enter Title: ")
    if len(Title)!=0:
        search['Title']=Title
    Author=input("Enter Author: ")
    if len(Author)!=0:
        search['Author']=Author
    Publisher=input("Enter Publisher: ")
    if len(Publisher)!=0:
        search['Publisher']=Publisher
    whereString=""
    str1=""
    i=0
    for keys,val in search.items():
        if i==0:
            str1='"'+keys+'"'+"="+"'"+str(val)+"'"
            i+=1
        else:
            whereString+=(" AND "+'"'+keys+'"'+"="+"'"+val+"'")
    queryString="SELECT * FROM booktable WHERE {}{}".format(str1,whereString)
    

    Testsearch(search)
    # print("Hello")


    