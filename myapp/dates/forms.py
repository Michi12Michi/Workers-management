from myapp.models import Date, Schedule
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FormField, FieldList, ValidationError
from wtforms.validators import DataRequired, NumberRange, Length

class AddSchedule(FlaskForm):

    name = StringField("Schedule tag:", validators = [DataRequired(), Length(min = 1, max = 10)])
    hours = IntegerField("Hours:", validators = [NumberRange(min = 0, max = 8)])
    submit = SubmitField("Commit")

    def check_names(self, name_field):
        if Schedule.query.filter_by(name = name_field.data).first():
            raise ValidationError("Error! Schedule already registered!")

def DynamicSchedule(*args, **kwargs):
    class FinalForm(FlaskForm):
        pass

    class MedianForm(FlaskForm):
        worker = StringField(render_kw = {'disabled': 'disabled'})
        schedule = SelectField(choices = args[1])

    FinalForm.work_sche = FieldList(FormField(MedianForm), min_entries = args[0])
    FinalForm.submit = SubmitField("Register Plan")
    return FinalForm()
