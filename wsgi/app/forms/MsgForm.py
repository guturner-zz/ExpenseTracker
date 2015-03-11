from flask.ext.wtf import Form
from wtforms import TextField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import Required

class MsgForm(Form):
    to = SelectField("To:", [Required("Please choose a user to send to.")], choices=[], coerce=int)
    memo = TextField("Memo (128 chars or less)", [Required("Please enter a message of 128 characters or less.")], widget=TextArea())

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False

        if self.to.data == -1:
            self.to.errors.append("Please choose a user to send to.")
            return False

        if len(self.memo.data) == 0 or len(self.memo.data) > 128:
            self.memo.errors.append("Please enter a message of 128 characters or less.")
            return