from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from contextlib import contextmanager
from .models import booktable,MemberTable,IssueTable,ReserveTable
import datetime

class DataBaseConnection():
    def __init__(self):
        self.__DATABASE_URI ='postgres+psycopg2://<username>:<password>@localhost:5432/LIS'
        self.__engine=create_engine(self.__DATABASE_URI)
        self.Session=sessionmaker(bind=self.__engine)
    
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # def drop_db(self):
    #     Base.metadata.drop_all(self.__engine)
    # def create_db(self):
    #     Base.metadata.create_all(self.__engine)

class DataBaseManipulation():
    def __init__(self,DataBaseConnectionObject):
        self.__session=DataBaseConnectionObject
    def search(self,searchitems):
        whereString=""
        str1=""
        i=0
        for keys,val in searchitems.items():
            if i==0:
                str1='"'+keys+'"'+"="+"\'"+str(val)+"\'"
                i+=1
            else:
                whereString+=(" OR "+'"'+keys+'"'+"="+"'"+val+"'")
        queryString="SELECT * FROM booktable WHERE {}{}".format(str1,whereString)
        s=scoped_session(self.__session.Session)
        results=s.execute(queryString)
        s.close()
        ans=[self.InfoBook(argISBN=i[0]) for i in results if i[-1]]

        return ans
    def AvailableTrue(self,argISBN):
        with self.__session.session_scope() as s:
            s.query(booktable).filter(booktable.ISBN==argISBN)\
                .update({booktable.Available:True},synchronize_session=False)
    
    def AvailableFalse(self,argISBN):
        with self.__session.session_scope() as s:
            s.query(booktable).filter(booktable.ISBN==argISBN)\
                .update({booktable.Available:False},synchronize_session=False)

    def ChangeLastIssued(self,argISBN,CurrDate):
        with self.__session.session_scope() as s:
            s.query(booktable).filter(booktable.ISBN==argISBN)\
                    .update({
                        booktable.LastIssued:CurrDate
                        },
                    synchronize_session=False)

    def InsertIssue(self,IssueObj):
        with self.__session.session_scope() as s:
            s.add(IssueObj)
        
    def InfoBook(self,argISBN):
        lis=None
        with self.__session.session_scope() as s:
            if s.query(booktable).filter(booktable.ISBN==argISBN).first() is not None:
                lis=s.query(booktable).filter(booktable.ISBN==argISBN).first().__dict__
        return lis

    def InfoMember(self,argMembershipCode):
        lis=None
        with self.__session.session_scope() as s:
            if s.query(MemberTable).filter(MemberTable.MembershipCode==argMembershipCode).first() is not None:
                lis=s.query(MemberTable).filter(MemberTable.MembershipCode==argMembershipCode).first().__dict__
        return lis

    def ISBNReserved(self,argISBN):
        """
        return True if book with ISBN is reserved.
        """
        num=0
        with self.__session.session_scope() as s:
            num=s.query(ReserveTable.MembershipCode).filter(ReserveTable.ISBN==argISBN).count()
        if num==0:
            return False
        else:
            return True
    
    def RemoveIssue(self,argISBN,argMembershipCode):
        """
        Remove entry from Issue Table for the ISBN and MembershipCode.
        """
        with self.__session.session_scope() as s:
            num=s.query(IssueTable)\
                .filter(IssueTable.ISBN==argISBN,IssueTable.MembershipCode==argMembershipCode)\
                    .delete(synchronize_session=False)
            
            if num>1:
                print("More than one record is deleted")
        

    def IncreaseIssuedBooks(self,argMembershipCode):
        """
        Increase the Num_Of_Books_To_Be_Issued in MemberDetails
        """
        with self.__session.session_scope() as s:
            s.query(MemberTable).filter(MemberTable.MembershipCode==argMembershipCode)\
                .update({MemberTable.Num_Of_Books_To_Be_Issued:MemberTable.Num_Of_Books_To_Be_Issued+1},synchronize_session=False)
    
    def DecreaseIssuedBooks(self,argMembershipCode):
        """
        Decrease the Num_Of_Books_To_Be_Issued in MemberDetails
        """
        with self.__session.session_scope() as s:
            s.query(MemberTable).filter(MemberTable.MembershipCode==argMembershipCode)\
                .update({MemberTable.Num_Of_Books_To_Be_Issued:MemberTable.Num_Of_Books_To_Be_Issued-1},synchronize_session=False)
                


    def RecordsGT5(self):
        """
        Using Book_Table find all records where LastIssued is greater than 5 years ago
return the Book Info
datetime.datetime.now() - datetime.timedelta(days=3*365)
        """
        lis=None
        with self.__session.session_scope() as s:
            lis=s.query(booktable.ISBN).filter(booktable.LastIssued <= datetime.datetime.now() - datetime.timedelta(days=5*365)).all()
        ans=[]
        for i in lis:
            ans.append(self.InfoBook(i[0]))
        return ans
        

    def IssueDeadlinePassed(self):
        """
        From Issue_Table find all Records where the Deadline has passed.
Print all MemberDetails
        """
        lis=None
        with self.__session.session_scope() as s:
            lis=s.query(IssueTable.MembershipCode).filter(IssueTable.DeadLine < datetime.date.today()).all()
        ans=[]
        for i in lis:
            ans.append(self.InfoMember(i[0]))
        return ans

    def NumIssuedBooks(self,argMembershipCode):
        """
        From MemberDetails find Num_Of_Books_To_Be_Issued for given MembershipCode
        """
        ans=None
        with self.__session.session_scope() as s:
            ans=s.query(MemberTable.Num_Of_Books_To_Be_Issued).filter(MemberTable.MembershipCode==argMembershipCode).first()
        return ans[0]

    def IssueExists(self,argISBN=None,argMembershipCode=None):
        """
        From Issue_Table check if for the Given ISBN and MembershipCode any entry exists or 
        not.
        Using the ISBN and MembershipCode find an entry in the Issue_Table
        Using the Issue_Table the ISBN check if there is an entry or not 
        Using the MembershipCode see if there are any entries in Issue_Table
        """
        ans=[]
        if argISBN is not None and argMembershipCode is not None :
            with self.__session.session_scope() as s:
                if s.query(IssueTable).filter(IssueTable.MembershipCode==argMembershipCode,IssueTable.ISBN==argISBN).first() is not None:
                    ans.append(s.query(IssueTable).filter(IssueTable.MembershipCode==argMembershipCode,IssueTable.ISBN==argISBN).first().__dict__)
        elif argISBN is not None:
            with self.__session.session_scope() as s:
                if s.query(IssueTable).filter(IssueTable.ISBN==argISBN).first() is not None:
                    ans.append(s.query(IssueTable).filter(IssueTable.ISBN==argISBN).first().__dict__)
        else:
            with self.__session.session_scope() as s:
                for i in s.query(IssueTable).filter(IssueTable.MembershipCode==argMembershipCode).all():
                    ans.append(i.__dict__)

        return ans

    def ReserveExists(self,argISBN,argMembershipCode=None):
        """
        Using the ISBN and MembershipCode check if entry exists in Reserve_Table
        """
        ans=None
        if argMembershipCode is not None:
            with self.__session.session_scope() as s:
                if s.query(ReserveTable).filter(ReserveTable.MembershipCode==argMembershipCode,ReserveTable.ISBN==argISBN).first() is not None:
                    ans=s.query(ReserveTable).filter(ReserveTable.MembershipCode==argMembershipCode,ReserveTable.ISBN==argISBN).first().__dict__
        else:
            with self.__session.session_scope() as s:
                if s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN).first() is not None:
                    ans=s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN).first().__dict__          
        return ans

    def RemoveReserve(self,argISBN,argMembershipCode=None):
        """
        Using the ISBN and MembershipCode remove the tuple from the Reserve_Table
        """
        if argMembershipCode is None:
            with self.__session.session_scope() as s:
                num=s.query(ReserveTable)\
                        .filter(ReserveTable.ISBN==argISBN)\
                            .delete(synchronize_session=False)
        else:
            with self.__session.session_scope() as s:
                num=s.query(ReserveTable)\
                        .filter(ReserveTable.ISBN==argISBN,ReserveTable.MembershipCode==argMembershipCode)\
                            .delete(synchronize_session=False)
            if num>1:
                print("More than one record is deleted")

    def ReturnReserve(self,argISBN):
        """
        Using ISBN get the Row and pass all info to the calling function
        """
        num=None
        with self.__session.session_scope() as s:
            if s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN).first() is not None:
                num=s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN).first().__dict__
        return num
            

    def CheckMemberType(self,argMembershipCode):
        """
        Using MembershipCode return Member type to calling Functions
        """
        ans=None
        with self.__session.session_scope() as s:
            ans=s.query(MemberTable.Category).filter(MemberTable.MembershipCode==argMembershipCode).first()
        return ans[0]

    def CheckReserveISBN(self,argISBN):
        """
        Using ISBN in the Reserve_Table the row and return it.
        Using ISBN in the Reserve_Table the row and return it.
        """
        ans=None
        with self.__session.session_scope() as s:
            if s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN).first() is not None:
                ans=s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN).first().__dict__
        return ans

    def ReturnEmail(self,argMembershipCode):
        """
        Using the MembershipCode in the MemberDetails table return Contact detials.
        """
        with self.__session.session_scope() as s:
            temp=s.query(MemberTable.email).filter(MemberTable.MembershipCode==argMembershipCode).first()
        return temp[0]

    def ChangeDateReserve(self,newDate,argISBN,argMembershipCode):
        """
        Using ISBN change the Date to the date given by Calling Function in Reserve_Table
        """
        with self.__session.session_scope() as s:
            s.query(ReserveTable).filter(ReserveTable.ISBN==argISBN,ReserveTable.MembershipCode==argMembershipCode)\
                .update({ReserveTable.DeadLine:newDate},synchronize_session=False)

    def InsertBook(self,BookObject):
        """
        All details are entered into the DataBase Book_Table
        """
        with self.__session.session_scope() as s:
            s.add(BookObject)

    def RemoveBook(self,argISBN):
        """
        Using ISBN remove the Book fro Book_Table
        """
        with self.__session.session_scope() as s:
            s.query(booktable).filter(booktable.ISBN==argISBN)\
                .delete(synchronize_session=False)

    def InsertMember(self,MemberObject):
        """
        Insert all detials passed alongwith the MembershipCode into the MemberDetails
        """
        with self.__session.session_scope() as s:
            s.add(MemberObject)


    def InsertReserve(self,ReserveObject):
        """
        Insert all detials passed alongwith the MembershipCode into the MemberDetails
        """
        with self.__session.session_scope() as s:
            s.add(ReserveObject)

    def RemoveMember(self,argMembershipCode):
        """
        Using the MembershipCode delete all entry from MemberDetails and Reserve_Table 
        """
        with self.__session.session_scope() as s:
            s.query(MemberTable).filter(MemberTable.MembershipCode==argMembershipCode)\
                .delete(synchronize_session=False)
            s.query(ReserveTable).filter(ReserveTable.MembershipCode==argMembershipCode)\
                .delete(synchronize_session=False)

