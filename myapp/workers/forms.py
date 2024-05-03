from myapp.models import Worker
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class AddWorker(FlaskForm):

    name = StringField("First name:", validators = [DataRequired()])
    surname = StringField("Second name:", validators = [DataRequired()])
    role = StringField("Role:")
    phone = StringField("Telephone:")
    email = StringField("E-mail:")
    picture = FileField("Update profile picture:", validators = [FileAllowed(["jpg", "png", "jpeg"])])
    submit = SubmitField("Add worker")

class UpdateWorker(AddWorker):
    submit = SubmitField("Update")

def PaymentFunc(*args):
    class PaymentForm(FlaskForm):
        value = StringField("Monthly pay", render_kw = {'disabled': 'disabled'}, default=args[0])
        submit = SubmitField("Pay")
        
    return PaymentForm()