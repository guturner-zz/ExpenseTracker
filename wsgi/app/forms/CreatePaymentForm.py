from flask.ext.wtf import Form
from flask import session
from wtforms import TextField, SelectField
from wtforms.validators import Required
from ..models import User

class CreatePaymentForm(Form):
    errors = []

    receiver = SelectField("Recipient", [Required("Please choose a user to pay.")], choices=[(0, "<none selected>")], coerce=int)
    amount   = TextField("Amount", [Required("Please enter an amount.")])
    date     = TextField("Date")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            self.errors = self.consolidateErrorMessage()
            return False

        failed = False

        if self.receiver.data == -1:
            self.receiver.errors.append("Please choose a user to pay.")
            failed = True

        try:
            float(self.amount.data)

        except ValueError:
            self.amount.errors.append("Payment amount must be a number!")
            failed = True

        self.errors = self.consolidateErrorMessage()
        return not failed

    def consolidateErrorMessage(self):
        return self.receiver.errors + self.amount.errors