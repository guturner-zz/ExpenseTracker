import sys
import unittest
from wsgi.app import app
from wsgi.app.models import *

pw = ""

def total(currentUser):
    #currently logged in user
    user = currentUser
    #all other users in household
    otherUsers = db.session.query(User).filter(User.hid == user.hid, User.id != user.id).all()
    #list of totals in order of household members
    totalsDict = {i.id: 0.0 for i in otherUsers}
    #all expense chunks for expenses not owned by current user
    chunkQuery = db.session.query(ExpenseChunk).join(Expense)#.filter(ExpenseChunk.uid == user.id, Expense.uid != user.id)

    for otherUser in otherUsers:
        #find which expenses are owned by other user which the current user participated in
        otherUserExpenses = chunkQuery.filter(ExpenseChunk.uid == user.id, Expense.uid == otherUser.id).all()
        otherUserExpensesTotal = sum([expense.originalAmount for expense in otherUserExpenses])
        print "otherUserExpensesTotal: " + str(otherUserExpensesTotal)
        totalsDict[otherUser.id] -= otherUserExpensesTotal

        #find which expenses are owned by the user and otherUser participated in
        userExpenses = chunkQuery.filter(ExpenseChunk.uid == otherUser.id, Expense.uid == user.id).all()
        print userExpenses
        userExpensesTotal = sum([expense.originalAmount for expense in userExpenses])
        totalsDict[otherUser.id] += userExpensesTotal
        print "userExpensesTotal: " + str(userExpensesTotal)

        #find which payments were made by current user to other user
        paymentsUserToOtherUser = db.session.query(Payment).filter_by(uidPayer = user.id, uidReceiver=otherUser.id).all()
        paymentsUserToOtherUserTotal = sum([payment.amount for payment in paymentsUserToOtherUser])
        print "paymentsUserToOtherUserTotal: " + str(paymentsUserToOtherUserTotal)
        totalsDict[otherUser.id] += paymentsUserToOtherUserTotal

        #find which payments were made by other user to current user
        paymentsOtherUserToUser = db.session.query(Payment).filter_by(uidPayer = otherUser.id, uidReceiver=user.id).all()
        paymentsOtherUserToUserTotal = sum([payment.amount for payment in paymentsOtherUserToUser])
        print "paymentsOtherUserToUserTotal: " + str(paymentsOtherUserToUserTotal)
        totalsDict[otherUser.id] -= paymentsOtherUserToUserTotal

        return totalsDict


class ModelTests(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://' + "root" + ':' +\
                    pw + '@' + app.config["LOCALHOST"] + ':3306/' + "expenseTest"

        self.app = app.test_client()
        db.init_app(app)
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def testUserAdd(self):
        with app.app_context():
            #user required for user
            household = Household("My House")
            db.session.add(household)
            db.session.commit()
            u = User("Zachary", "Black", "zacharybblack@outlook.com", "1234", 1)
            db.session.add(u)
            db.session.commit()
            userQuery = User.query.filter_by(firstName = "Zachary").first()
            assert userQuery.firstName == "Zachary"
            assert userQuery.lastName == "Black"
            assert userQuery.email == "zacharybblack@outlook.com"
            assert userQuery.pwdHash == u.pwdHash

    def testExpenseAdd(self):
        with app.app_context():
            #user required for user
            household = Household("My House")
            db.session.add(household)
            db.session.commit()
            #user required to make expense
            user = User("Zachary", "Black", "zacharybblack@outlook.com", "1234", 1)
            db.session.add(user)
            db.session.commit()
            userQuery = User.query.get(1)

            expense = Expense("Cable", datetime.now(), 88.44, userQuery.id)
            db.session.add(expense)
            db.session.commit()
            assert Expense.query.filter_by(name = "Cable").first().owner == User.query.get(1)
            #How to get all the expenses a user has
            User.query.get(1).expenses.all()

    def testExpenseChunkAdd(self):
        with app.app_context():
            #user required for user
            household = Household("My House")
            db.session.add(household)
            db.session.commit()
            #user required to make expense
            user = User("Zachary", "Black", "zacharybblack@outlook.com", "1234", 1)
            db.session.add(user)
            db.session.commit()
            #expense required to make expense chunk
            userQuery = User.query.get(1)
            expense = Expense("Cable", datetime.now(), 88.44, userQuery.id)
            db.session.add(expense)
            db.session.commit()
            expenseChunk = ExpenseChunk(userQuery.id, expense.id, 85.00)
            db.session.add(expenseChunk)
            db.session.commit()
            ExpenseChunk.query.get(1)

    def testPaymentAdd(self):
        with app.app_context():
            #user required for user
            household = Household("My House")
            db.session.add(household)
            db.session.commit()
            #users required to make payment
            user1 = User("Zachary", "Black", "zacharybblack@outlook.com", "1234", 1)
            user2 = User("Guy", "Turner", "guturner@indiana.edu", "1234", 1)
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            #new payment
            payment = Payment(User.query.get(1).id, User.query.get(2).id,
                              50.00)
            db.session.add(payment)
            db.session.commit()
            assert Payment.query.get(1).uidPayer == 1
            print User.query.get(1).payments.all()

    def testHouseholdAdd(self):
        with app.app_context():
            #new household
            household = Household("MyHouse")
            db.session.add(household)
            db.session.commit()
            #users to add to household
            user1 = User("Zachary", "Black", "zacharybblack@outlook.com", "1234", 1)
            user2 = User("Guy", "Turner", "guturner@indiana.edu", "1234", 1)
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            print User.query.get(1).household

def total(currentUser):
    #currently logged in user
    user = currentUser
    #all other users in household
    otherUsers = db.session.query(User).filter(User.hid == user.hid, User.id != user.id).all()
    #list of totals in order of household members
    totalsDict = {i.id: 0.0 for i in otherUsers}
    #all expense chunks for expenses not owned by current user
    chunkQuery = db.session.query(ExpenseChunk).join(Expense)#.filter(ExpenseChunk.uid == user.id, Expense.uid != user.id)

    for otherUser in otherUsers:
        #find which expenses are owned by other user which the current user participated in
        otherUserExpenses = chunkQuery.filter(ExpenseChunk.uid == user.id, Expense.uid == otherUser.id).all()
        otherUserExpensesTotal = sum([expense.originalAmount for expense in otherUserExpenses])
        totalsDict[otherUser.id] -= otherUserExpensesTotal

        #find which expenses are owned by the user and otherUser participated in
        userExpenses = chunkQuery.filter(ExpenseChunk.uid == otherUser.id, Expense.uid == user.id).all()
        userExpensesTotal = sum([expense.originalAmount for expense in userExpenses])
        totalsDict[otherUser.id] += userExpensesTotal

        #find which payments were made by current user to other user
        paymentsUserToOtherUser = db.session.query(Payment).filter_by(uidPayer = user.id, uidReceiver=otherUser.id).all()
        paymentsUserToOtherUserTotal = sum([payment.amount for payment in paymentsUserToOtherUser])
        totalsDict[otherUser.id] += paymentsUserToOtherUserTotal

        #find which payments were made by other user to current user
        paymentsOtherUserToUser = db.session.query(Payment).filter_by(uidPayer = otherUser.id, uidReceiver=user.id).all()
        paymentsOtherUserToUserTotal = sum([payment.amount for payment in paymentsOtherUserToUser])
        totalsDict[otherUser.id] -= paymentsOtherUserToUserTotal

        return totalsDict

class TotalTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://' + "root" + ':' +\
                    pw + '@' + app.config["LOCALHOST"] + ':3306/' + "expenseTest"

        self.app = app.test_client()
        db.init_app(app)
        with app.app_context():
            db.drop_all()
            db.create_all()

            #new household
            household = Household("MyHouse")
            db.session.add(household)
            db.session.commit()
            #users to add to household
            user1 = User("Zachary", "Black", "zacharybblack@outlook.com", "1234", 1)
            user2 = User("Guy", "Turner", "guturner@indiana.edu", "1234", 1)
            user3 = User("Dakotah", "Modlin", "a@a.com", "1234", 1)
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(user3)

            db.session.commit()
    @classmethod
    def tearDownClass(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test1(self):
        with app.app_context():
            #expense required to make expense chunk
            user1 = User.query.get(1)
            user2 = User.query.get(2)
            expense = Expense("Cable", datetime.now(), 1.00, user1.id)
            db.session.add(expense)
            db.session.commit()
            expenseChunk = ExpenseChunk(user2.id, expense.id, 1.00)
            db.session.add(expenseChunk)
            db.session.commit()
            #from user1's point of view
            totalDict = total(user1)
            assert totalDict[user2.id] == 1.00

            #from user2's point of view
            totalDict = total(user2)
            assert totalDict[user1.id] == -1.00

    def test2(self):
        with app.app_context():
            #50 cent payment from user2 to user1
            user1 = User.query.get(1)
            user2 = User.query.get(2)
            payment = Payment(user2.id, user1.id, .50)
            db.session.add(payment)
            db.session.commit()

            #from user1's point of view
            totalDict = total(user1)
            assert totalDict[user2.id] == .50

            #from user2's point of view
            totalDict = total(user2)
            assert totalDict[user1.id] == -.50

    def test3(self):
        with app.app_context():
            user1 = User.query.get(1)
            user2 = User.query.get(2)
            expense = Expense("Water Bill", datetime.now(), 0.75, user2.id)
            db.session.add(expense)
            db.session.commit()
            expenseChunk = ExpenseChunk(user1.id, expense.id, 0.75)
            db.session.add(expenseChunk)
            db.session.commit()

            #from user1's point of view
            totalDict = total(user1)
            assert totalDict[user2.id] == -0.25

            #from user2's point of view
            totalDict = total(user2)
            assert totalDict[user1.id] == 0.25

    def test4(self):
        with app.app_context():
            user1 = User.query.get(1)
            user2 = User.query.get(2)
            user3 = User.query.get(3)
            expense = Expense("Electric Bill", datetime.now(), 1.00, user3.id)
            db.session.add(expense)
            db.session.commit()
            expenseChunk = ExpenseChunk(user2.id, expense.id, 1.00)
            db.session.add(expenseChunk)
            db.session.commit()
            #should be same as test3, this test case does not involve both user 1 and 2
            #from user1's point of view
            totalDict = total(user1)
            assert totalDict[user2.id] == -0.25

            #from user2's point of view
            totalDict = total(user2)
            assert totalDict[user1.id] == 0.25

if __name__ == "__main__":
    global pw
    # DB Password is a script parameter:
    if len(sys.argv) == 2:
        pw = sys.argv[1]
        del sys.argv[1:]
    else:
        pw = ""
    unittest.main()