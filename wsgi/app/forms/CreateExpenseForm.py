from flask.ext.wtf import Form
from wtforms import TextField, FieldList, BooleanField, FormField
from wtforms.validators import Required
from flask import session
from ..models import User, Household
import datetime

class ParticipantForm(Form):
    checkBox = BooleanField(default=False)
    amount = TextField("Amount")

    #fixes validation problem
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(ParticipantForm, self).__init__(*args, **kwargs)

class CreateExpenseForm(Form):
    errors = []

    name    = TextField("Short Description (64 chars or less)", [Required("Please enter an expense description.")])
    amount  = TextField("Amount", [Required("Please enter an amount.")])
    date    = TextField("Due Date", [Required("Please enter a date for your expense.")])
    participant = FieldList(FormField(ParticipantForm), min_entries=1)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            self.errors = self.consolidateErrorMessage()
            return False
        failed = False
        #name field
        if len(self.name.data) > 64:
            self.name.errors.append("Expense name must not exceed 64 characters.")
            failed = True
        print len(self.name.data)
        #amount field
        try:
            #amount must be a number
            float(self.amount.data)
            #amount field positive, non-zero
            if float(self.amount.data) <= 0:
                self.amount.errors.append("Expense amount must be greater than 0.")
        except ValueError:
            self.amount.errors.append("Expense amount must be a number.")
            failed = True

        #date field
        try:
            minDate = datetime.date(2000, 1, 1)
            dateVal = datetime.datetime.strptime(self.date.data, "%Y-%m-%d")

            if dateVal.date() < minDate:
                self.date.errors.append("Expense date must be after " + str(minDate) + ".")
                failed = True

        except ValueError:
            self.date.errors.append("Invalid expense date format. Please use YYYY-MM-DD.")
            failed = True

        #participant field
        #make sure there is at least one non expense owner (current user) participant
        nonOwnerParticipant = False
        user = User.query.filter_by(email=session["email"]).first()
        householdMembers = User.query.filter(User.hid == user.hid).all()
        i = 0 #index for household members
        for participant in self.participant.data:
            if participant["checkBox"] == True:
                if user.id != householdMembers[i].id:
                    nonOwnerParticipant = True
                    break
            i += 1
        if not nonOwnerParticipant:
            self.participant.errors.append("You must add at least one participant besides the currently logged in user.")
            failed = True

        try:
            #make sure all participant amount values can be cast as float
            for participant in self.participant.data:
                if participant["checkBox"] == True:
                    float(participant["amount"])

            #make sure all participants amounts are greater than 0.00
            amounts = []
            negativeParticipantAmountFlag = False
            for participant in self.participant.data:
                if participant["checkBox"] == True:
                    if float(participant["amount"]) <= 0.0:
                        negativeParticipantAmountFlag = True
                    amounts.append(round(float(participant["amount"]), 2))
            if negativeParticipantAmountFlag:
                self.participant.errors.append("All Participant amounts must be greater than 0.")
                failed = True

            #sum of participant amounts must equal expense amount
            total = 0.00
            for amount in amounts:
                total += round(float(amount), 2)
            if round(float(self.amount.data), 2) != total:
                self.participant.errors.append("Participant amounts must add up to the expense total. Please correct the amounts or use the auto-split button.")
                failed = True
        except ValueError:
            self.participant.errors.append("Participant amount must be a number.")
            failed = True

        self.errors = self.consolidateErrorMessage()
        return not failed

    def consolidateErrorMessage(self):
        return self.name.errors + self.amount.errors + self.date.errors + self.participant.errors