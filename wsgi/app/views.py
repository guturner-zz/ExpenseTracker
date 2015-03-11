from flask import Flask
from flask import render_template, redirect, session, url_for, request
from functools import wraps
from datetime import date
from forms.SignupForm import SignupForm
from forms.LoginForm import LoginForm
from forms.MsgForm import MsgForm
from forms.CreateExpenseForm import CreateExpenseForm, ParticipantForm
from forms.CreatePaymentForm import CreatePaymentForm
from forms.DeleteExpenseForm import DeleteExpenseForm
from messaging.helper import getMessages, getUnreadMessages
from balances.helper import getTotals
from models import *
from wtforms import FieldList, FormField
import datetime
from wsgi.app import app

def login_required(funct):
    @wraps(funct)
    def theDecoratedFunction(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))

        user = User.query.filter_by(email=session["email"]).first()
        if user is None:
            return redirect(url_for("login"))

        # Things to do every time:
        session["unread"] = getUnreadMessages(user, False)

        return funct(*args, **kwargs)
    return theDecoratedFunction

# Root page:
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home Page")

@app.route("/expense/delete/<eid>")
@login_required
def deleteexpense(eid):
    expense = Expense.query.get(eid)
    #retire the expense chunks as well
    expenseChunks = ExpenseChunk.query.filter_by(eid=eid).all()
    for expenseChunk in expenseChunks:
        expenseChunk.retired = 1
        db.session.add(expenseChunk)
    expense.retired = 1
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("viewexpenses"))

@app.route("/expense/view", methods=['GET', 'POST'])
@login_required
def viewexpenses():
    user = User.query.filter_by(email=session["email"]).first()

    # Retrieve all expenses in the household in reverse order
    expenses = db.session.query(Expense).join(User).filter(User.hid == user.hid, Expense.uid == User.id, Expense.retired == 0)\
        .order_by(Expense.date.desc()).all()
    #{expenseID:participants}
    participants  = {}
    for expense in expenses:
        participants[expense.id] = db.session.query(User).join(ExpenseChunk).filter(expense.id == ExpenseChunk.eid)

    return render_template("expense/view.html", title="View Expenses", expenses=expenses, participants=participants)

@app.route("/payment/view/")
@login_required
def viewpayments():
    user = User.query.filter_by(email=session["email"]).first()

    # Retrieve a list of payments
    users = []
    for u in User.query.filter_by(hid=user.hid).all():
        users.append(u.id)

    payments = []
    for u in users:
        for p in db.session.query(Payment).filter(Payment.uidPayer == u, Payment.retired == 0):
            payments.append({'uidPayer': User.query.filter_by(id=p.uidPayer).first(), 'uidReceiver': User.query.filter_by(id=p.uidReceiver).first(), 'amount': p.amount, 'retired': p.retired, 'date': p.date, 'id':p.id})

    return render_template("payment/view.html", title="View Payments", payments=payments)

@app.route("/payment/delete/<pid>")
@login_required
def deletepayment(pid):
    payment = Payment.query.get(pid)
    payment.retired = 1
    db.session.add(payment)
    db.session.commit()
    return redirect(url_for("viewpayments"))


@app.route("/expense/create", methods=['GET', 'POST'])
@login_required
def createexpense():
    user = User.query.filter_by(email=session["email"]).first()

    # Get potential expense participants (Household members)
    householdMembersRaw = User.query.filter(User.hid == user.hid).all()
    numParticipants = len(householdMembersRaw)

    #Makes enough participant form instances for every household member
    CreateExpenseForm.participant = FieldList(FormField(ParticipantForm), min_entries=numParticipants)
    form = CreateExpenseForm()

    #list to hold all household members names
    householdMemberNames = []
    for member in householdMembersRaw:
        householdMemberNames.append(member.firstName + " " + member.lastName)

    if form.validate_on_submit() == False:
        return render_template("expense/create.html", title="Create Expense", form=form, householdMemberNames=householdMemberNames, today=date.today())
    else:
        session["expense"] = True
        #Create New Expense
        expenseName = form.name.data
        expenseAmount = round(float(form.amount.data), 2)
        expenseDate = datetime.datetime.strptime(form.date.data, "%Y-%m-%d")
        newExpense = Expense(expenseName, expenseDate, expenseAmount, user.id)
        db.session.add(newExpense)
        db.session.commit()

        # Generate an Expense History item:
        createEvent = newExpense.generateCreateHistoryItem(newExpense.id, user.firstName + " " + user.lastName)
        db.session.add(createEvent)
        db.session.commit()

        i = 0 #index for householdMembersRaw Array
        #Create New Expense Chunks
        for participant in form.participant.data:
            if participant["checkBox"] == True:
                expenseChunkUid = householdMembersRaw[i].id
                expenseChunkEid = newExpense.id
                expenseAmount = round(float(participant["amount"]), 2)
                newExpenseChunk = ExpenseChunk(expenseChunkUid, expenseChunkEid, expenseAmount)
                db.session.add(newExpenseChunk)
                db.session.commit()

                # Send message:
                memo = "New Expense! [" + newExpense.name + "] - you owe $" + ("%0.2f" % expenseAmount) + "."
                msg = Message(householdMembersRaw[i].id, user.id, memo)
                db.session.add(msg)
                db.session.commit()
            i += 1
        return redirect(url_for("viewexpenses"))

@app.route("/payment/create", methods=['GET', 'POST'])
@login_required
def createpayment():
    user = User.query.filter_by(email=session["email"]).first()

    form = CreatePaymentForm()

    usersRaw = db.session.query(User).filter(User.id != user.id, User.hid == user.hid).all()
    users = []
    uids  = []
    for u in usersRaw:
        uids.append(u.id)
        users.append(u.firstName + " " + u.lastName)

    toChoices = zip([-1] + uids, ["<none selected>"] + users)
    form.receiver.choices = toChoices

    if form.validate_on_submit() == False:
        return render_template("payment/create.html", title="Make Payment", form=form, today=str(date.today()))
    else:
        session["payment"] = True
        receiver = User.query.filter_by(id=form.receiver.data).first()

        # Create payment:
        payment = Payment(user.id, form.receiver.data, float(form.amount.data))
        db.session.add(payment)
        db.session.commit()

        return redirect(url_for("viewpayments"))

@app.route("/expense/esummary/<eid>")
@login_required
def esummary(eid):
    user = User.query.filter_by(email=session["email"]).first()

    valid = True

    expense   = Expense.query.filter_by(id=eid).first()
    ownername = ""
    history   = []
    chunks    = []

    if expense == None:
        valid = False
    else:
        owner     = User.query.filter_by(id=expense.uid).first()
        ownername = owner.firstName + " " + owner.lastName
        if (owner.hid != user.hid):
            valid = False
        else:
            history = expense.getHistory()
            chunks  = expense.getChunks()

    return render_template("expense/esummary.html", title="Expense Summary", expense=expense, chunks=chunks, ownername=ownername, history=history, valid=valid)

@app.route("/user/household")
@login_required
def household():
    user = User.query.filter_by(email=session["email"]).first()

    #all other users in household
    otherUsers = db.session.query(User).filter(User.hid == user.hid, User.id != user.id).all()
    totalsDict = getTotals(user, otherUsers)

    hh = Household.query.filter_by(id=user.hid).first()
    members = []
    for member in hh.users:
        # Ignore current user:
        if member == user:
            continue
        # Find non-retired owned expenses:
        numMemberOwned = len(Expense.query.filter(Expense.uid == member.id, Expense.retired == 0).all())
        # Tuple of the form: (name, # of expenses, balance, id)
        members.append( (member.firstName + " " + member.lastName, numMemberOwned, totalsDict[member.id], member.id) )

    # Find non-retired user owned expenses:
    numOwned = len(Expense.query.filter(Expense.uid == user.id, Expense.retired == 0).all())

    return render_template("user/household.html", title="Household: " + hh.name, key=hh.key, members=members, numOwned=numOwned)

@app.route("/messaging/hub/")
@login_required
def hub():
    user = User.query.filter_by(email=session["email"]).first()

    return render_template("messaging/hub.html", title="Messaging Hub", messages=getMessages(user))

@app.route("/messaging/hub/<mid>")
@login_required
def markMsgStatus(mid):
    user = User.query.filter_by(email=session["email"]).first()

    msg = Message.query.filter_by(id=mid).first()
    if msg is None:
        return redirect(url_for("hub"))

    failed = False
    if msg.uidTo != user.id:
        failed = True

    if not failed:
        newVal = 0
        if msg.isRead == 0:
            newVal = 1
        db.session.query(Message).filter(Message.id == msg.id).update({"isRead": newVal})
        db.session.commit()

    return redirect(url_for("hub"))

@app.route("/messaging/send/", methods=['GET', 'POST'])
@login_required
def sendMsg():
    user = User.query.filter_by(email=session["email"]).first()

    form = MsgForm()

    usersRaw = db.session.query(User).filter(User.id != user.id, User.hid == user.hid).all()
    users = []
    uids  = []
    for u in usersRaw:
        uids.append(u.id)
        users.append(u.firstName)

    toChoices = zip([-1] + uids, ["<none selected>"] + users)
    form.to.choices = toChoices

    if form.validate_on_submit() == False:
        return render_template("messaging/send.html", title="Send a Message", form=form, user=user)
    else:
        msg = Message(form.to.data, user.id, form.memo.data)
        db.session.add(msg)
        db.session.commit()
        session["sent"] = True
        return redirect(url_for("hub"))

@app.route("/messaging/send/<uid>/<amount>")
@login_required
def sendReminder(uid, amount):
    user = User.query.filter_by(email=session["email"]).first()
    memo = "This is a reminder that you owe me $" + ("%0.2f" % float(amount)) + "."
    msg = Message(uid, user.id, memo)
    db.session.add(msg)
    db.session.commit()
    session["reminder"] = True
    return redirect(url_for("household"))

@app.route("/security/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit() == False:
        return render_template("security/signup.html", title="Signup", form=form, submitted=True)
    else:
        # User is creating a new user
        if bool(form.householdName.data):
            newHousehold = Household(form.householdName.data)
            db.session.add(newHousehold)
            db.session.commit()
            #necessary to create a new user
            newUserHid = Household.query.filter_by(key=newHousehold.key).first().id

        # User is joining a pre-existing user:
        else:
            #neccessary to create new user
            newUserHid = Household.query.filter_by(key=form.key.data).first().id


        newUser = User(form.firstName.data, form.lastName.data, form.email.data, form.pwd.data, newUserHid)
        db.session.add(newUser)
        db.session.commit()

        session["email"]     = newUser.email
        session["firstName"] = newUser.firstName
        session["new"]       = True
        session["unread"]    = getUnreadMessages(newUser, False)
        return redirect(url_for("index"))

    return render_template("security/signup.html", title="Signup", form=form, submitted=False)

@app.route("/security/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit() == False:
        return render_template("security/login.html", title="Login", form=form, submitted=True)
    else:
        user = User.query.filter_by(email=form.email.data.lower()).first()
        session["email"]     = user.email
        session["firstName"] = user.firstName
        session["login"]     = True
        session["unread"]    = getUnreadMessages(user, False)
        return redirect(url_for("index"))

    return render_template("security/login.html", title="Login", form=form, submitted=False)


@app.route("/security/logout")
@login_required
def logout():
    session.pop("email", None)
    return redirect(url_for("index"))