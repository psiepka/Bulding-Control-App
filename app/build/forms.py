from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, IntegerField, PasswordField, BooleanField, SubmitField, PasswordField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError, Length, NumberRange
import requests
from app.models import User, Company, Build, Employee, JobApp, Post


class BuildForm(FlaskForm):
    """
    Build addding form
    Arguments:
    name - String, specification String, worth Integer, place String(place on map), start_date, end_date, creator_id, contractor_id
    """
    name = StringField('Name', validators=[DataRequired()])
    specification = StringField('Specification', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    worth = IntegerField('Value', validators=[DataRequired()])
    place = StringField('Place', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        name = Build.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('Please use a different name of Building.')



class EditBuildForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    specification = StringField('Specification', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    start_date = DateField('Start date', validators=[Optional()])
    end_date = DateField('End date',  validators=[Optional()])
    contractor = StringField('Company')
    worth = IntegerField('Value', validators=[DataRequired()])
    place = StringField('Place', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, orginal_name, *args, **kwargs):
        super(EditBuildForm, self).__init__(*args, **kwargs)
        self.orginal_name = orginal_name

    def validate_name(self, name):
        if name.data != self.orginal_name:
            name = Build.query.filter_by(name=name.data).first()
            if name is not None:
                raise ValidationError('Please use a different name of Building.')

    def validate_contractor(self, contractor):
        if contractor.data:
            company = Company.query.filter_by(name=contractor.data).first()
            if company is None:
                raise ValidationError('This company doesnt exist in app')
