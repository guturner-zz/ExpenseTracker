from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email
from ..models import User

class LoginForm(Form):
    email = TextField("E-mail", [Required("Please enter your e-mail address."),
                                 Email("Your e-mail address must follow the form: example@website.com")])
    password = PasswordField("Password", [Required("Please enter your password.")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Invalid e-mail or password.")
            return False