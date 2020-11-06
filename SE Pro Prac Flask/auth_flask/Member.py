from .DataBase import DataBaseManipulation,DataBaseConnection
from .models import ReserveTable,booktable

class Member():
    def __init__(self,MembershipCode=None):
        self.__MembershipCode=MembershipCode
        self.__db=DataBaseManipulation(DataBaseConnection())

    def search(self):
        """
        Depending upon the various parameters query the DB and return Results.
        Such that ISBN found from Book_Table are not in Issue_Table.
        """
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
        print(self.__db.search(search))
        
    def reserve(self):
        """
        Call Object of Reserve Class
        """
        obj=Reserve(self.__MembershipCode,input("ENter the ISBN of Book"))
        if not obj.check_reserved():
            obj.reserve()
        

class Reserve():
    def __init__(self,MembershipCode=None,ISBN=None):
        self.__MembershipCode=MembershipCode
        self.__ISBN=ISBN
        self.__db=DataBaseManipulation(DataBaseConnection())

    def check_reserved(self):
        """
        Using the ISBN check if the Book is Issued then check if previously Reserved.
        If not return False Else Return True
        """
        if len(self.__db.IssueExists(argISBN=self.__ISBN))==0:
            print("Book is Available TO Issue.No Need to Reserve")
            return True
        else:
            if self.__db.ReserveExists(argISBN=self.__ISBN) is not None:
                print("Book is already Reserved!!! Cannot Reserve Again")
                return True
        return False

    def reserve(self):
        """
        Create an entry in the Reserve_Table with ISBN and MembershipCode
        """
        self.__db.InsertReserve(
            ReserveTable(
                ISBN=self.__ISBN,
                MembershipCode=self.__MembershipCode
            )
        )
    