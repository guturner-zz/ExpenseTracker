from flask import session
from ..models import *

def getTotals(user, otherUsers):
    #list of totals in order of household members
    totalsDict = {i.id: 0.0 for i in otherUsers}
    #all expense chunks for expenses not owned by current user
    chunkQuery = db.session.query(ExpenseChunk).join(Expense)

    for otherUser in otherUsers:
        #find which expenses are owned by other user which the current user participated in
        otherUserExpenses = chunkQuery.filter(ExpenseChunk.uid == user.id, Expense.uid == otherUser.id, Expense.retired == 0).all()
        otherUserExpensesTotal = sum([expense.amount for expense in otherUserExpenses])
        totalsDict[otherUser.id] -= otherUserExpensesTotal

        #find which expenses are owned by the user and otherUser participated in
        userExpenses = chunkQuery.filter(ExpenseChunk.uid == otherUser.id, Expense.uid == user.id, Expense.retired == 0).all()
        userExpensesTotal = sum([expense.amount for expense in userExpenses])
        totalsDict[otherUser.id] += userExpensesTotal

        #find which payments were made by current user to other user
        paymentsUserToOtherUser = db.session.query(Payment).filter_by(uidPayer=user.id, uidReceiver=otherUser.id, retired=0).all()
        paymentsUserToOtherUserTotal = sum([payment.amount for payment in paymentsUserToOtherUser])
        totalsDict[otherUser.id] += paymentsUserToOtherUserTotal

        #find which payments were made by other user to current user
        paymentsOtherUserToUser = db.session.query(Payment).filter_by(uidPayer=otherUser.id, uidReceiver=user.id, retired=0).all()
        paymentsOtherUserToUserTotal = sum([payment.amount for payment in paymentsOtherUserToUser])
        totalsDict[otherUser.id] -= paymentsOtherUserToUserTotal

    return totalsDict