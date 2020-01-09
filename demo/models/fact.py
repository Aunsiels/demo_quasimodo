import json

from demo import db

LONG_ELEMENTS_SIZE = 8192

ELEMENTS_SIZE = 256


class Fact(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(ELEMENTS_SIZE), index=True)
    predicate = db.Column(db.String(ELEMENTS_SIZE), index=True)
    object = db.Column(db.String(ELEMENTS_SIZE), index=True)
    modality = db.Column(db.String(LONG_ELEMENTS_SIZE), index=True)
    is_negative = db.Column(db.Boolean)
    plausibility = db.Column(db.Float)
    typicality = db.Column(db.Float)
    saliency = db.Column(db.Float)
    __examples_json = db.Column(db.String(LONG_ELEMENTS_SIZE))
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
        # There is a small problem in formatting
        modificator = 0 if len(line) == 9 else 1
        examples = cls.get_examples_from_line(line)
        return Fact(subject=line[0],
                    predicate=line[1],
                    object=line[2],
                    modality=line[3].strip(),
                    is_negative=line[4] == "1",
                    plausibility=float(line[5]),
                    typicality=float(line[7 - modificator]),
                    saliency=float(line[8 - modificator]),
                    examples=examples)

    @classmethod
    def get_examples_from_line(cls, line):
        if len(line) != 9:
            return []
        raw_examples_tuples = [example.split(" x#x") for example in line[6].split(" // ")]
        examples = [(example[0], int(example[1])) for example in raw_examples_tuples]
        return examples


def read_facts(filename):
    with open(filename) as f:
        facts = read_facts_from_file(f)
    return facts


def read_facts_from_file(f):
    facts = []
    for line in f:
        facts.append(Fact.from_line(line.decode("utf-8")))
    return facts


def add_all_facts_to_db(facts, db):
    db.session.add_all(facts)
    db.session.commit()
