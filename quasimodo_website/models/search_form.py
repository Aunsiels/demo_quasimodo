from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField


class SearchForm(FlaskForm):

    subject = StringField("Subject")
    predicate = StringField("Predicate")
    object = StringField("Object")
    modality = StringField("Modality")
    polarity = SelectField("Polarity",
                           choices=[("Positive and Negative",
                                     "Positive and Negative"),
                                    ("Positive", "Positive"),
                                    ("Negative", "Negative")])
    search = SubmitField("Search")
