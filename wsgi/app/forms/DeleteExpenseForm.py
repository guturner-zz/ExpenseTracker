from flask.ext.wtf import Form
from wtforms.validators import Required
from wtforms import TextField
from flask import session
from ..models import Expense, User, db

class DeleteExpenseForm(Form):
    errors = []

    expenseID = TextField("Expense (ID) to be deleted", [Required("Please enter an Expense ID")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_on_submit(self):

        if not Form.validate_on_submit(self):
            return False
        failed = False
        user = User.query.filter_by(email=session["email"]).first()

        try:
            int(self.expenseID.data)

            if int(self.expenseID.data) < 1 and not failed:
                self.expenseID.errors.append("Expense ID must be greater than 0")
                failed = True

            expenseId = int(self.expenseID.data)
            #expense must be part of your household (can't delete other households expenses)
            if expenseId not in [expense.id for expense in db.session.query(Expense).join(User).filter(User.hid == user.hid, Expense.uid == User.id).all()] and not failed:
                self.expenseID.errors.append("Expense does not exist. Please enter an Expense ID on this page.")
                failed = True

        except ValueError:
            self.expenseID.errors.append("Expense ID must be an integer.")
            failed = True

        self.errors.append(self.expenseID.errors)
        return not failed



