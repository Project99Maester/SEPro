from .DataBase import DataBaseManipulation,DataBaseConnection
from .models import booktable,MemberTable,IssueTable
import datetime
class Librarian():
    def __init__(self,name):
        self.__name=name
        self.__db=DataBaseManipulation(DataBaseConnection())

    def Issue(self,memcode,isbn):
        # memcode=input("Enter the Membercode")
        obj=Issue(MembershipCode=memcode)
        if obj.check_if_issued():
            # isbn=input("Enter the ISBN of the BOOK")
            obj=Issue(MembershipCode=memcode,ISBN=isbn)
            if not obj.check_reserved():
                #(True,0) print("Successfully Issued Book...")
                
                return obj.issuing()
            else:
                # print("Sorry the Book is reserved by a Member!!.....")
                return (False,1)
        else:
            # print("Book is Not Available!Already Issued....")
            return (False,0)

    def Return(self,isbn,memcode,op=1):
        # memcode=input("Enter the Membercode")
        # isbn=input("Enter the ISBN of the BOOK")
        obj=Return(MembershipCode=memcode,ISBN=isbn)

        if Issue(MembershipCode=memcode,ISBN=isbn).check_if_issued():
            if op==1:
                return obj.print_bill()
            """
            check the Reserve_Table using ISBN if anyone has reserved anything
            """
            if self.__db.ISBNReserved(isbn):
                obj.alert_reserved()
            """
            Remove Entry from the Issue Table.
            """
            self.__db.RemoveIssue(argISBN=isbn,argMembershipCode=memcode)
            """
            Make the Book Available
            """
            self.__db.AvailableTrue(argISBN=isbn)
            """
            Increase the Num_Of_Books_To_Be_Issued by One in Member_Detail Table
            """
            self.__db.IncreaseIssuedBooks(argMembershipCode=memcode)
            return (True,'')
        else:
            # print("No record for the given Combination of MembershipCode and ISBN")
            return (False,"No record for the given Combination of MembershipCode and ISBN")
    
    def Stats(self):
        """
        Using the Book_table  find all Records where LastIssued is grater than 5
        years ago.
        Show the Book Info
        """
        return self.__db.RecordsGT5()
        
    def BookManage(self,choice,name=None,author=None,pub=None,rack=None,num=None,ISBN=None):
        if choice==1:
            ISBN=[]
            for _ in range(int(num)):
                ISBN.append(ManageBook(
                    name=name,
                    author=author,
                    publisher=pub,
                    RackNumber=rack,
                    Available=True
                    ).registerBook())
            return ISBN

        elif choice==0:
            return ManageBook(ISBN=ISBN).removeBook()
            
        else:
            print("Invalid Input...")
            return

    def Overdue(self):
        """
        From the Issue_Table get all the Records where Deadline is expired wrt current Date.
        Print all the Member Details.
        """
        # print("Deadline of These Members are Passed:")
        return self.__db.IssueDeadlinePassed()
        
    def ManageMember(self,choice,name=None,email=None,Category=None,MembershipCode=None):
        if choice==1:
            MembershipCode=ManageMember(
                name=name,
                Type=Category,
                email=email
            ).registerMember()
            return MembershipCode

        elif choice==0:
            return ManageMember(MembershipCode=MembershipCode).removeMember()
            
        else:
            print("Invalid Input...")
            return
    
    def __str__(self):
        return "LIB_"+self.__name


class Issue():
    def __init__(self,MembershipCode=None,ISBN=None):
        self.__MembershipCode=MembershipCode
        self.__ISBN=ISBN
        self.returnDate=None
        self.__db=DataBaseManipulation(DataBaseConnection())

    def check_if_issued(self):
        """
        1) If ISBN is None
        Using the MembershipCode check the number of issues and if can issue further or not.
        Print the List of Issued Book wrt the MembershipCode
        Returns True/False depending on whethter the member can issue anyother book or not.

        2)If ISBN is not None
        Using the ISBN and MembershipCode find if any entry exists for the combination in the Issue 
        If exists return True or else return False 
        
        DB
        Issue::check_if_issued
        From MemberDetails find Num_Of_Books_To_Be_Issued for given MembershipCode

        *Issue::check_if_issued
        From Issue_Table check if for the Given ISBN and MembershipCode any entry exists or 
        not.

        """
        if self.__ISBN==None:
            num_books_to_be_issued=self.__db.NumIssuedBooks(argMembershipCode=self.__MembershipCode)
            if num_books_to_be_issued==0:
                print("Cannot Issue Further Books as Capacity is Full")
                print("Return any of the Following Books")
                for book in self.__db.IssueExists(argMembershipCode=self.__MembershipCode):
                    print(self.__db.InfoBook(book['ISBN']))
                return False
            else:
                books=self.__db.IssueExists(argMembershipCode=self.__MembershipCode)
                if books is not None:
                    print("The Following Books are Issued..")
                    for book in books:
                        # print(book)
                        print(self.__db.InfoBook(book['ISBN']))
                return True
        else:
            lis=self.__db.IssueExists(argMembershipCode=self.__MembershipCode,argISBN=self.__ISBN)
            if lis is not None:
                return True
            return False

        
    
    def check_reserved(self):
        """
        Using the ISBN and Membership code there can be 3 cases
            1) Entry in the reserve table matches both the ISBN and MembershipCode then
            remove the entry and return False.

            2) If only ISBN matches for the entry and not the MembershipCode then check the Following:
                if the deadline mentioned in the Reserve table has passed.if passed delete the entry and return False
                Else just return True
            DB
            Issue::check_reserved
            Using the ISBN and MembershipCode check if entry exists in Reserve_Table

            Issue::check_reserved
            Using the ISBN and MembershipCode remove the tuple from the Reserve_Table

            Issue::check_reserved
            Using ISBN get the Row and pass all info to the calling function

        """
        if self.__db.ReserveExists(argMembershipCode=self.__MembershipCode,argISBN=self.__ISBN) is not None:
            self.__db.RemoveReserve(argISBN=self.__ISBN,argMembershipCode=self.__MembershipCode)
            return False
        else:
            reservation=self.__db.ReturnReserve(argISBN=self.__ISBN)
            if reservation and reservation['DeadLine'] and reservation['DeadLine'] > datetime.date.today():
                print("Someone has reserved this Book... Check After {}".format(reservation['DeadLine']))
                return True
            else:
                self.__db.RemoveReserve(argISBN=self.__ISBN)
                return False

            

    def issuing(self):
        """
        1) Extract member  Type using membership Code
        2) Calculate Deadline acc to Current Date and Member type. 
        3) Create an entry in issue_Table with MembershipCode and ISBN also put in the 
        Deadline
        4) Update the Last_Issued with Current Date. 
        5) Using the MembershipCode decrease the value of Num_of_Books_To_Be_Issued inthe 
        Member_Detail Table.
        
        DB
        Issue::issuing
        Using MembershipCode return Member type to calling Functions

        """
        #1
        mem=self.__db.CheckMemberType(argMembershipCode=self.__MembershipCode)
        #2
        dates=ManageMember(Type=mem).getBooks()
        Deadl=datetime.date.today()+datetime.timedelta(days=dates[1])
        #3
        IssueObj=IssueTable(
            ISBN=self.__ISBN,
            MembershipCode=self.__MembershipCode,
            DeadLine=Deadl
            )
        self.__db.InsertIssue(IssueObj)
        #4
        self.__db.ChangeLastIssued(argISBN=self.__ISBN,CurrDate=datetime.date.today())
        #5
        num=self.__db.NumIssuedBooks(argMembershipCode=self.__MembershipCode)
        if num==0:
            # print("Dont Decrease Further")
            return (True,0)
        self.__db.DecreaseIssuedBooks(argMembershipCode=self.__MembershipCode)
        self.__db.AvailableFalse(argISBN=self.__ISBN)
        return (True,0)


class Return():
    def __init__(self,MembershipCode=None,ISBN=None):
        self.__MembershipCode=MembershipCode
        self.__ISBN=ISBN
        self.__db=DataBaseManipulation(DataBaseConnection())
        
    def print_bill(self):
        """
        1) Fetch the Return Date From Issue Table
        2) If Return Date Expired then Calculate the Number of Days Overdue wrt CurrentDate
        3) Rate is Rupees 10/Day Calculate the penalty
        4) Print the Penalty.
        
        DB
        *Return::print_bill
        Using the ISBN and MembershipCode find an entry in the Issue_Table

        """
        ret=self.__db.IssueExists(argISBN=self.__ISBN,argMembershipCode=self.__MembershipCode)
        ans=''
        if ret[0]['DeadLine'] < datetime.date.today():
            
            ans+="You have missed the Deadline.You have to pay the Fine. \nCalulating Fine"
            pen_day=(datetime.date.today()-ret[0]['DeadLine']).days
            ans+=" Number of Days past Return Date is {}. Penalty is {} Rupees. Pay Upfront Please".format(pen_day,pen_day*10)
            return (True,ans)
        return (False,'')    
    def alert_reserved(self):
        """
        1) Using the ISBN check in Reserve_Table and get their MembershipCode from the entry.
        2) Calculate the date 7 days from current date and store it in a variable
        3) Using the MembershipCode extract contact detials from Members_Details Table.
        4) Notify the Members
        5) Then put the date into the Reserve_Table. 
        
        DB
        
        #Return::alert_reserved
        Using ISBN in the Reserve_Table the row and return it.

        Return::alert_reserved
        Using the MembershipCode in the MemberDetails table return Contact detials.

        Return::alert_reserved
        Using ISBN change the Date to the date given by Calling Function in Reserve_Table
        """        
        reserved=self.__db.CheckReserveISBN(argISBN=self.__ISBN)
        self.__db.ChangeDateReserve(newDate=datetime.date.today()+datetime.timedelta(days=7),argMembershipCode=reserved['MembershipCode'],argISBN=self.__ISBN)
        Email=self.__db.ReturnEmail(argMembershipCode=reserved['MembershipCode'])
        
        # Send Mail



class ManageBook():
    def __init__(self,lastIssued=None,ISBN=None,name=None,author=None,publisher=None,RackNumber=None,Available=True):
        self.__name=name
        self.__author=author
        self.__publisher=publisher
        self.__RackNumber=RackNumber
        self.__LastIssued=lastIssued
        self.__ISBN=ISBN
        self.__Available=Available
        self.__db=DataBaseManipulation(DataBaseConnection())
    
    def registerBook(self):
        """
        Generate a Unique ISBN Number 
        Get the Book Details into the Data base along with the ISBN
        """
        self.__ISBN=self.generate_ISBN()
        self.__db.InsertBook(
            booktable(
                ISBN=self.__ISBN,
                Title=self.__name,
                Author=self.__author,
                Publisher=self.__publisher,
                Rack=self.__RackNumber,
                LastIssued=self.__LastIssued,
                Available=self.__Available
            )
        )
        return self.__ISBN
        
    
    def generate_ISBN(self):
        ISBN=0
        with open('ISBN.bin','rb') as f:
            ch=f.read()
            if ch:
                ISBN=int.from_bytes(ch,byteorder='big')
        ISBN=ISBN+1
        with open('ISBN.bin','wb') as f:
            f.write(bytes([ISBN]))
        return ISBN

    def removeBook(self):
        """
        Using the Issue Table check if the Book is issued or not. If Issued then display
        the member deatalils and return
        Use the reserve table and See if anyone wants it, if there is someone then return and dont 
        delete.
        Using the ISBN just Remove the Book from Book_Table. 
        """
        IssuedBooks=self.__db.IssueExists(argISBN=self.__ISBN)
        if IssuedBooks:
            """Already Issued"""
            # err="Book is Issued Cannot be Removed!!!")
            # print("Book is Issued to ")
            # print()
            return (False,1,self.__db.InfoMember(argMembershipCode=IssuedBooks[0]['MembershipCode']))
        else:
            """Available..."""
            Reserved=self.__db.CheckReserveISBN(argISBN=self.__ISBN)
            if Reserved and Reserved[0]['DeadLine'] >= datetime.date.today():
                return (False,2,self.__db.InfoMember(argMembershipCode=Reserved[0]['MembershipCode']))
            # elif Reserved and Reserved[0]['DeadLine'] < datetime.date.today():
            #     print("Book is Reserved But Member Already Given 7 Days!!!")
            #     choice=input("Do you want to delete? Y or N")
            #     if choice.lower() == 'n':
            #         return
            self.__db.RemoveBook(argISBN=self.__ISBN)
            return (True,0)


class ManageMember():
    def __init__(self,name=None,Type=None,email=None,MembershipCode=None):
        self.__name=name
        self.__Type=Type
        self.__email=email
        self.__MembershipCode=MembershipCode
        if MembershipCode is None:
            self.__NumOfBooks=self.getBooks()[0] 
        self.__db=DataBaseManipulation(DataBaseConnection())
    
    def getBooks(self):
        """According to Type of the Member Return the Number of Books that can be Borrowed
        Undergraduate- 2 books x 30 days
        PG- 4 books x 30 days
        Research- 6 books x 90 days
        Facuulty- 10 books x 180 days
        """
        ans={
            'UG':(2,30),
            'PG':(4,30),
            'RS':(6,90),
            'FA':(10,180)

        }
        return ans[self.__Type]
    def generate_MembershipCode(self):
        MembershipCode=0
        with open('./MembershipCode.bin','rb') as f:
            ch=f.read()
            if ch:
                MembershipCode=int.from_bytes(ch,byteorder='big')
        MembershipCode=MembershipCode+1
        with open('./MembershipCode.bin','wb') as f:
            f.write(bytes([MembershipCode]))
        return MembershipCode
    def registerMember(self):
        """
        Generate a new MembershipCode 
        Insert the Details alongwith the MembershipCode into DataBase
        return MembershipCode
        """
        self.__MembershipCode=self.generate_MembershipCode()
        
        self.__db.InsertMember(
            MemberTable(
                MembershipCode=self.__MembershipCode,
                Name=self.__name,
                Category=self.__Type,
                Num_Of_Books_To_Be_Issued=self.__NumOfBooks,
                email=self.__email
            )
        )
        return self.__MembershipCode
    
    def removeMember(self):
        """
        check using th MembershipCode if the Member has an outstanding Books from Issue Table.
        Now if no books are issued then only Remove the member from Member_Detail and Reserve_Table.
        """
        Issue=self.__db.IssueExists(argMembershipCode=self.__MembershipCode)
        if Issue:
            resp="Person Has Issued Book.First Return Those then Deletion can occur ISBN are "
            
            for books in Issue:
                resp+=str(books['ISBN'])+" "
            return (False,resp)
        else:
            self.__db.RemoveMember(argMembershipCode=self.__MembershipCode)
            return (True,"Removed the Member!!!")
        
