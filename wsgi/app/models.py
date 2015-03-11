from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime
import uuid


db = SQLAlchemy()

#must be defined before use to prevent error in user's relationship to Payment
class Payment(db.Model):
    __tablename__ = "Payment"
    id = db.Column(db.Integer, primary_key=True)
    uidPayer = db.Column(db.Integer, db.ForeignKey("User.id"))
    uidReceiver = db.Column(db.Integer, db.ForeignKey("User.id"))
    amount = db.Column(db.Float)
    retired = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime)

    def __init__(self, uidPayer, uidReceiver, amount):
        self.uidPayer = uidPayer
        self.uidReceiver = uidReceiver
        self.amount = amount
        self.date = datetime.today()

    def __repr__(self):
        return "%r to %r Amount: %r" % (User.query.get(self.uidPayer), User.query.get(self.uidReceiver), self.amount)

class Message(db.Model):
    __tablename__ = "Message"
    id = db.Column(db.Integer, primary_key=True)
    uidTo = db.Column(db.Integer, db.ForeignKey("User.id"))
    uidFrom = db.Column(db.Integer, db.ForeignKey("User.id"))
    memo = db.Column(db.String(128))
    time = db.Column(db.DateTime)
    isRead = db.Column(db.Integer)

    def __init__(self, toID, fromID, memo):
        self.uidTo = toID
        self.uidFrom = fromID
        self.memo = memo
        self.time = datetime.now()
        self.isRead = 0

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64))
    lastName = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    pwdHash = db.Column(db.String(100))
    hid = db.Column(db.Integer, db.ForeignKey("Household.id"))
    expenses = db.relationship("Expense", backref="owner", cascade="all,delete", lazy="dynamic")
    payments = db.relationship("Payment",  backref="payer", cascade="all,delete", lazy="dynamic",
                               foreign_keys=[Payment.uidPayer], primaryjoin=(id==Payment.uidPayer))
    received = db.relationship("Payment", backref="receiver", cascade="all,delete", lazy="dynamic",
                               foreign_keys=[Payment.uidReceiver], primaryjoin=(id==Payment.uidReceiver))
    messageSent = db.relationship("Message",  backref="sender", cascade="all,delete", lazy="dynamic",
                               foreign_keys=[Message.uidFrom], primaryjoin=(id==Message.uidFrom))
    messageReceived = db.relationship("Message",  backref="receiver", cascade="all,delete", lazy="dynamic",
                               foreign_keys=[Message.uidTo], primaryjoin=(id==Message.uidTo))

    def __init__(self, firstname, lastname, email, password, hid):
        self.firstName = firstname.title()
        self.lastName = lastname.title()
        self.email = email.lower()
        self.hid = hid
        self.set_password(password)

    def set_password(self, password):
        self.pwdHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdHash, password)

    def __repr__(self):
        return '<User> %r %r>' % (self.firstName, self.lastName)

class ExpenseHistory(db.Model):
    __tablename__ = "ExpenseHistory"
    id = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.Integer, db.ForeignKey("Expense.id"))
    memo = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    type = db.Column(db.Integer)

    def __init__(self, eid, memo, date, type):
        self.eid = eid
        self.memo = memo
        self.date = date
        self.type = type

class ExpenseChunk(db.Model):
    __tablename__ = "ExpenseChunk"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("User.id"))
    eid = db.Column(db.Integer, db.ForeignKey("Expense.id"))
    amount = db.Column(db.Float)
    retired = db.Column(db.Integer, default=0)

    def __init__(self, uid, eid, amount):
        self.uid = uid
        self.eid = eid
        self.amount = amount

    def __repr__(self):
        return "<ExpenseChunk> %r for %r amount: %r" %\
               (User.query.get(self.uid), Expense.query.get(self.eid), self.amount)

class Expense(db.Model):
    __tablename__ = "Expense"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    uid = db.Column(db.Integer, db.ForeignKey("User.id"))
    retired = db.Column(db.Integer, default=0)
    history = db.relationship("ExpenseHistory", backref="history", cascade="all,delete", lazy="dynamic",
                              foreign_keys=[ExpenseHistory.eid])
    chunks = db.relationship("ExpenseChunk", backref="chunks", cascade="all,delete", lazy="dynamic",
                             foreign_keys=[ExpenseChunk.eid])

    def __init__(self, name, date, amount, uid):
        self.name = name
        self.date = date
        self.amount = amount
        self.uid = uid
        # Update user balance:
        owner = User.query.filter_by(id=uid).first()

    def __repr__(self):
        return "<Expense> Owner:%r Name:%r Date:%r" % (self.uid, self.name, self.date)

    def getChunks(self):
        """
        :return: A list of dictionaries in the form {label: firstName, value: currentAmount}
        """
        chunkMap = []
        for chunk in self.chunks.all():
            expenseUser = User.query.filter_by(id=chunk.uid).first()
            chunkMap.append({'label': expenseUser.firstName, 'value': chunk.amount})
        return chunkMap

    def getHistory(self):
        """
        :return: A list of dictionaries in the form {date, memo}
        """
        historyMap = []
        for event in self.history.all():
            historyMap.append({'date': event.date, 'memo': event.memo})
        return historyMap

    def generateCreateHistoryItem(self, eid, owner):
        memo = owner + " created the expense."
        date = datetime.today()
        expenseHistory = ExpenseHistory(eid, memo, date, 1)

        return expenseHistory

    def generatePaymentHistoryItem(self, eid, user, amount):
        memo = user + " paid $" + ('%.2f' % amount) + " towards the expense."
        date = datetime.today()
        expenseHistory = ExpenseHistory(eid, memo, date, 2)

        return expenseHistory

class Household(db.Model):
    __tablename__ = "Household"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    key = db.Column(db.String(36), unique=True)
    users = db.relationship("User", backref="household", cascade="all,delete",  lazy="dynamic")

    def __init__(self, name):
        self.name = name
        self.key = self.generateHouseholdKey()

    def generateHouseholdKey(self):
        householdKey = uuid.uuid4()
        household = Household.query.filter_by(key=uuid).first()
        while household:
            householdKey = uuid.uuid4()
            household = Household.query.filter_by(key=uuid).first()
        return householdKey

    def __repr__(self):
        return "<Household> %r" % self.name

