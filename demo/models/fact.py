import json

from demo import db


class Fact(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(64), index=True)
    predicate = db.Column(db.String(64), index=True)
    object = db.Column(db.String(64), index=True)
    modality = db.Column(db.String(64), index=True)
    is_negative = db.Column(db.Boolean)
    plausibility = db.Column(db.Float)
    typicality = db.Column(db.Float)
    saliency = db.Column(db.Float)
    __examples_json = db.Column(db.String(1024))
    __examples = []

    @property
    def examples(self):
        return self.__examples

    @examples.setter
    def examples(self, examples):
        self.__examples = examples
        self.__examples_json = json.dumps(examples)

    @property
    def examples_json(self):
        return self.__examples

    @examples_json.setter
    def examples_json(self, examples_json):
        self.__examples = json.loads(examples_json)
        self.__examples_json = examples_json

    @classmethod
    def from_line(cls, line):
        line = line.strip().split("\t")
        examples = cls.get_examples_from_line(line)
        return Fact(subject=line[0],
                    predicate=line[1],
                    object=line[2],
                    modality=line[3].strip(),
                    is_negative=line[4] == "1",
                    plausibility=float(line[5]),
                    typicality=float(line[7]),
                    saliency=float(line[8]),
                    examples=examples)

    @classmethod
    def get_examples_from_line(cls, line):
        raw_examples_tuples = [example.split(" x#x") for example in line[6].split(" // ")]
        examples = [(example[0], int(example[1])) for example in raw_examples_tuples]
        return examples


def read_facts(filename):
    facts = []
    with open(filename) as f:
        for line in f:
            facts.append(Fact.from_line(line))
    return facts


def add_all_facts_to_db(facts, db):
    db.session.add_all(facts)
    db.session.commit()
