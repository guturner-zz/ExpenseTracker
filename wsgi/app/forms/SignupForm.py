from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email
from ..models import User, Household

class SignupForm(Form):
    errors = []

    firstName = TextField("First Name", [Required("Please enter your first name.")])
    lastName = TextField("Last Name (optional)")
    email = TextField("E-mail", [Required("Please enter your e-mail address."),
                                 Email("Your e-mail address must follow the form: example@website.com")])
    pwd = PasswordField("Password", [Required("Please enter a password.")])
    confirmPwd = PasswordField("Confirm Password", [Required("Please confirm your password.")])
    key = TextField("Association Key")
    householdName = TextField("New Household Name")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            self.errors = self.consolidateErrorMessage()
            return False

        failed = False

        if self.pwd.data != self.confirmPwd.data:
            self.pwd.errors.append("Your passwords don't match.")
            failed = True

        if not bool(self.key.data) and not bool(self.householdName.data):
            self.key.errors.append("You must either join a household or create a new one.")
            failed = True

        if bool(self.key.data) and bool(self.householdName.data):
            self.key.errors.append("You cannot both join and create a household, choose one.")
            failed = True

        # Ensure the provided user exists if user opts to join:
        if bool(self.key.data) and not bool(self.householdName.data):
            household = Household.query.filter_by(key=self.key.data.lower()).first()
            if not household:
                self.key.errors.append("That household association key is invalid.")
                failed = True

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken.")
            failed = True

        self.errors = self.consolidateErrorMessage()
        return not failed

    def consolidateErrorMessage(self):
        return self.firstName.errors + self.lastName.errors + self.email.errors + self.pwd.errors + self.confirmPwd.errors + self.key.errors + self.householdName.errors