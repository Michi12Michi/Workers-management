from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, FormField, FieldList
from wtforms.validators import NumberRange

def PaymentsF(*args, **kwargs):
    class PaymentForm(FlaskForm):
        pass

    # lavoratori
    # nome turni
    class Single(FlaskForm):
        payment = FloatField(validators=[NumberRange(min = 0)])

    class In(FlaskForm):
        payment = FieldList(FormField(Single), min_entries=args[1])
 
    PaymentForm.field = FieldList(FormField(In), min_entries = args[0])
    PaymentForm.submit = SubmitField("Commit")
    return PaymentForm()
