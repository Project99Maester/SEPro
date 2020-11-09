from .DataBase import DataBaseManipulation,DataBaseConnection
from .models import ReserveTable,booktable

class Member():
    def __init__(self,MembershipCode=None):
        self.__MembershipCode=MembershipCode
        self.__db=DataBaseManipulation(DataBaseConnection())

    def search(self,ISBN='',Title='',Author='',Publisher=''):
        """
        Depending upon the various parameters query the DB and return Results.
        Such that ISBN found from Book_Table are not in Issue_Table.
        """
        search=[]
        search.append(ISBN)
        search.append(Title)
        search.append(Author)
        search.append(Publisher)
        search.append(self.__MembershipCode)
        return self.__db.search(search)
        
    def reserve(self,isbn):
        """
        Call Object of Reserve Class
        """
        obj=Reserve(self.__MembershipCode,isbn)
        resp=obj.check_reserved()
        if not resp[0]:
            return obj.reserve()
        return (not resp[0],resp[1])
        

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
            return (True,"Book is Available TO Issue.No Need to Reserve")
        else:
            if self.__db.ReserveExists(argISBN=self.__ISBN) is not None:   
                return (True,"Book is already Reserved!!! Cannot Reserve Again")
        return (False,)

    def reserve(self):
        """
        Create an entry in the Reserve_Table with ISBN and MembershipCode
        """
        self.__db.InsertReserve(
            ReserveTable(
                ISBN=self.__ISBN,
                MembershipCode=self.__MembershipCode
            ),
            ISBN=self.__ISBN
        )
        return (True,)
    