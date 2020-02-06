from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SubjectForm(FlaskForm):

    subject = StringField("Subject")
    search = SubmitField("Get")