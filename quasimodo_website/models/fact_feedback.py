from quasimodo_website import DB


class FactFeedback(DB.Model):

    id = DB.Column(DB.Integer, primary_key=True)
    fact_id = DB.Column(DB.Integer, DB.ForeignKey('fact.id'))
    source = DB.Column(DB.String)
    feedback = DB.Column(DB.String, index=True)
