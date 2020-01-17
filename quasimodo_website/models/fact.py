import json

from quasimodo_website import DB

LONG_ELEMENTS_SIZE = 8192

ELEMENTS_SIZE = 256


class Fact(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    subject = DB.Column(DB.String(ELEMENTS_SIZE), index=True)
    predicate = DB.Column(DB.String(ELEMENTS_SIZE), index=True)
    object = DB.Column(DB.String(ELEMENTS_SIZE), index=True)
    __modality = []
    __modality_json = DB.Column(DB.String(LONG_ELEMENTS_SIZE), index=True)
    is_negative = DB.Column(DB.Boolean)
    plausibility = DB.Column(DB.Float)
    typicality = DB.Column(DB.Float)
    saliency = DB.Column(DB.Float)
    __examples = []
    __examples_json = DB.Column(DB.String(LONG_ELEMENTS_SIZE))

    @property
    def examples(self):
        if self.__examples:
            return self.__examples
        else:
            self.__examples = json.loads(self.__examples_json)
            return self.__examples

    @examples.setter
    def examples(self, examples):
        self.__examples = examples
        self.__examples_json = json.dumps(examples)

    @property
    def examples_json(self):
        return self.__examples_json

    @examples_json.setter
    def examples_json(self, examples_json):
        self.__examples = json.loads(examples_json)
        self.__examples_json = examples_json

    @property
    def modality(self):
        if self.__modality:
            return self.__modality
        else:
            self.__modality = json.loads(self.__modality_json)
            return self.__modality

    @modality.setter
    def modality(self, modality):
        self.__modality = modality
        self.__modality_json = json.dumps(modality)

    @property
    def modality_sentences(self):
        return ", ".join([x[0] for x in self.modality])

    @property
    def modality_json(self):
        return self.__modality_json

    @modality_json.setter
    def modality_json(self, modality_json):
        self.__modality = json.loads(modality_json)
        self.__modality_json = modality_json

    @classmethod
    def from_line(cls, line):
        line = line.strip().split("\t")
        # There is a small problem in formatting
        modifier = 0 if len(line) == 9 else 1
        examples = cls.get_examples_from_line(line)
        modalities = cls.get_modalities_from_line(line)
        return Fact(subject=line[0],
                    predicate=line[1],
                    object=line[2],
                    modality=modalities,
                    is_negative=line[4] == "1",
                    plausibility=float(line[5]),
                    typicality=float(line[7 - modifier]),
                    saliency=float(line[8 - modifier]),
                    examples=examples)

    @classmethod
    def get_examples_from_line(cls, line):
        if len(line) != 9:
            return []
        examples = cls.get_multiple_sentence_column(line, 6)
        return examples

    @classmethod
    def get_modalities_from_line(cls, line):
        examples = cls.get_multiple_sentence_column(line, 3)
        return examples

    @classmethod
    def get_multiple_sentence_column(cls, line, column_number):
        if not line[column_number].strip():
            return []
        raw_examples_tuples = [example.split(" x#x")
                               for example in
                               line[column_number].split(" // ")]
        examples = [(example[0], int(example[1]))
                    for example in raw_examples_tuples]
        return examples

    @classmethod
    def modality_like(cls, search):
        return Fact.__modality_json.like(search)


def read_facts(filename):
    with open(filename) as f:
        facts = read_facts_from_file(f)
    return facts


def read_facts_from_file(f):
    facts = []
    first = True
    for line in f:
        if not isinstance(line, str):
            line = line.decode("utf-8")
        if first and line.startswith("subject\t"):
            first = False
        else:
            first = False
            facts.append(Fact.from_line(line))
    return facts


def add_all_facts_to_db(facts, db):
    db.session.add_all(facts)
    db.session.commit()
