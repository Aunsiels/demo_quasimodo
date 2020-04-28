from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class QuestionForm(FlaskForm):

    question = StringField("question")
    answer0 = StringField("answer0")
    answer1 = StringField("answer1")
    answer2 = StringField("answer2")
    answer3 = StringField("answer3")
    ask = SubmitField("Ask")