from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from application.models import Checklist, Task

class ListAvailableNameCheck:
    def __init__(self, message=None):
        if not message:
            message = "That name is already in use. Please use another."
        self.message=message
    
    def __call__(self, form, field):
        data = Checklist.query.filter_by(name=field.data).all()

        unavailable_names = []
        for item in data:
            unavailable_names.append(item.name)
    
        if field.data in unavailable_names:
            raise ValidationError(self.message)

class TaskAvailableNameCheck:
    def __init__(self, message=None):
        if not message:
            message = "That name is already in use. Please use another."
        self.message=message
    
    def __call__(self, form, field):
        data = Task.query.filter_by(name=field.data).all()

        unavailable_names = []
        for item in data:
            unavailable_names.append(item.name)
    
        if field.data in unavailable_names:
            raise ValidationError(self.message)
        

class RestrictedWordCheck:
    def __init__(self, invalid_names, message=None):
        self.invalid_names = invalid_names
        if not message:
            message = "Invalid name - please try another!"
        self.message = message
    
    def __call__(self, form, field):
        if field.data.lower() in (word.lower() for word in self.invalid_names):
            raise ValidationError(self.message)

class SpecialCharacterCheck:
    def __init__(self, invalid_characters=None, message=None):
        if not invalid_characters:
            invalid_characters = ["!", "\"", "£", "%", "^", "&", "*", "(", ")", "_", "-", "=" "+", "{", "}", "[", "]" "@", "~", "\'", ",", ".", "\\", "/", "|", "?", "¬", ";", ":", "#"]
        self.invalid_characters = invalid_characters
        if not message:
            message = "Input cannot include special characters!"
            self.message = message

    def __call__(self, form, field):
        for item in self.invalid_characters:
            if item in field.data.lower():
                raise ValidationError(self.message)

class ListForm(FlaskForm):
    user_input = StringField("List Name", validators=[
        DataRequired(),
        Length(max=20),
        ListAvailableNameCheck(),
        RestrictedWordCheck(invalid_names=["admin", "root"]),
        SpecialCharacterCheck()
    ])
    submit = SubmitField('Add')

class RenameForm(FlaskForm):
    user_input = StringField("List Name", validators=[
        DataRequired(),
        Length(max=20),
        ListAvailableNameCheck(),
        RestrictedWordCheck(invalid_names=["admin", "root"]),
        SpecialCharacterCheck()
    ])
    submit = SubmitField('Submit')

class TaskForm(FlaskForm):
    user_input = StringField("Task Name", validators=[
        DataRequired(),
        TaskAvailableNameCheck(),
        Length(max=20),
        RestrictedWordCheck(invalid_names=["admin", "root"]),
        SpecialCharacterCheck()
    ])
    submit = SubmitField('Add')
