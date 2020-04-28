import json
import os
import pickle
import re
from sys import argv

from flask import current_app
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegressionCV

from .models import MultipleChoiceQuestion, MultipleChoiceAnswer, \
    ChoiceConfidence


from .spacy_accessor import SpacyAccessor


FILE_DIR = os.path.abspath(os.path.dirname(__file__))


class MachineLearningSolver:

    def __init__(self, knowledge_base_location=None, training_location=None):
        self.knowledge_base_location = knowledge_base_location
        self.training_location = training_location
        self.question_answer_label = []
        self.preprocessed_question_answer_label = []
        self.kb = None  # A pandas dataframe
        self.kb_grouped_s = None
        self.kb_grouped_p = None
        self.kb_grouped_o = None
        self.spacy_accessor = SpacyAccessor()
        self.clf = None

    def preprocess(self):
        self.load_kb()
        self.train()
        self.save_model()

    def load_kb(self):
        kb_raw = []
        raw_triples = []
        with open(self.knowledge_base_location) as f:
            for line in f:
                line = line.strip().split("\t")
                if line[5] == "score":
                    continue
                kb_raw.append(line[:6])
                raw_triples.append("\t".join(line[0:3]))
        raw_lemmatized_triples = self.spacy_accessor.lemmatize_multiple(
            raw_triples)
        kb = []
        for line in raw_lemmatized_triples:
            line = " ".join(line)
            line = line.strip().split("\t")
            subj = line[0].strip()
            pred = line[1].strip()
            if len(line) > 2:
                obj = line[2].strip()
            else:
                obj = ""
            kb.append([subj, pred, obj])
        self.kb = pd.DataFrame(kb_raw,
                               columns=["subject", "predicate", "object",
                                        "modality", "is_negative",
                                        "score"])
        df_spo_lemma = pd.DataFrame(kb, columns=["subject", "predicate",
                                                 "object"])
        self.kb["subject"] = df_spo_lemma["subject"]
        self.kb["predicate"] = df_spo_lemma["predicate"]
        self.kb["object"] = df_spo_lemma["object"]
        self.kb["score"] = pd.to_numeric(self.kb["score"])
        self.kb["predicate"] = [transform_predicate(x) for x in
                                self.kb["predicate"]]

    def load_training_data_questions(self):
        questions = []
        with open(self.training_location) as f:
            for line in f:
                questions.append(json.loads(line.strip()))
        self.question_answer_label = []
        for question in questions:
            for choice in question["question"]["choices"]:
                self.question_answer_label.append(
                    (question["question"]["stem"],
                     choice["text"],
                     int(choice["label"] == question["answerKey"])))

    def preprocess_question_answer_label(self):
        questions = [" ".join(remove_stop_words(x[0].lower())) for x in
                     self.question_answer_label]
        answers = [" ".join(remove_stop_words(x[1].lower())) for x in
                   self.question_answer_label]
        questions_lemmatized = self.spacy_accessor.lemmatize_multiple(
            questions)
        answers_lemmatized = self.spacy_accessor.lemmatize_multiple(answers)
        self.preprocessed_question_answer_label = []
        for i in range(len(self.question_answer_label)):
            self.preprocessed_question_answer_label.append(
                (questions_lemmatized[i],
                 answers_lemmatized[i],
                 self.question_answer_label[i][2]))
        return self.preprocessed_question_answer_label

    def group_kb(self):
        self.kb_grouped_s = self.kb.groupby(by="subject")
        self.kb_grouped_p = self.kb.groupby(by="predicate")
        self.kb_grouped_o = self.kb.groupby(by="object")

    def get_features_lemmatized(self, question, answer):
        p_and_o_with_s = 0
        p_with_s = 0
        o_with_s = 0
        double_link_s_to_o = 0

        if answer in self.kb_grouped_s.groups:
            for _, row in self.kb_grouped_s.get_group(answer).iterrows():
                if check_in(row["predicate"], question):
                    if check_in(row["object"], question):
                        p_and_o_with_s += row["score"]
                    else:
                        p_with_s += row["score"]
                elif check_in(row["object"], question):
                    o_with_s += row["score"]

        s_and_o_with_p = 0
        s_with_p = 0
        o_with_p = 0

        if answer in self.kb_grouped_p.groups:
            for _, row in self.kb_grouped_p.get_group(answer).iterrows():
                if check_in(row["subject"], question):
                    if check_in(row["object"], question):
                        s_and_o_with_p += row["score"]
                    else:
                        s_with_p += row["score"]
                elif check_in(row["object"], question):
                    o_with_p += row["score"]

        s_and_p_with_o = 0
        s_with_o = 0
        p_with_o = 0
        double_link_o_to_s = 0

        if answer in self.kb_grouped_o.groups:
            for _, row in self.kb_grouped_o.get_group(answer).iterrows():
                if check_in(row["subject"], question):
                    if check_in(row["predicate"], question):
                        s_and_p_with_o += row["score"]
                    else:
                        s_with_o += row["score"]
                elif check_in(row["predicate"], question):
                    p_with_o += row["score"]

        return np.array([p_and_o_with_s,
                         s_and_o_with_p,
                         s_and_p_with_o,
                         p_with_s,
                         o_with_s,
                         s_with_p,
                         o_with_p,
                         s_with_o,
                         p_with_o,
                         double_link_s_to_o,
                         double_link_o_to_s])

    def get_features_grouped_preprocessed(self, question, answer):
        question_lemmatized = " ".join(question)
        answer_lemmatized_split = answer
        result = None
        max_size = min(len(answer_lemmatized_split), 3)
        for size in range(max_size, 0, -1):
            for i in range(len(answer_lemmatized_split)):
                j = i + size
                to_add = self.get_features_lemmatized(question_lemmatized,
                                                      " ".join(
                                                          answer_lemmatized_split[
                                                          i:j])).astype(
                    np.float64)
                to_add[np.isnan(to_add)] = 0.0
                if result is None:
                    result = to_add
                else:
                    result += to_add
            if result is not None:
                break
        if result is None:
            return [0.0] * 11
        return list(result)

    def get_features_from_preprocessed_qal(self, qal):
        return self.get_features_grouped_preprocessed(qal[0], qal[1])

    def get_all_features(self):
        all_features = []
        for i, qal in enumerate(self.preprocessed_question_answer_label):
            all_features.append(self.get_features_from_preprocessed_qal(qal))
        return all_features

    def get_labels(self):
        y = []
        for qal in self.question_answer_label:
            y.append(qal[2])
        return y

    def train(self):
        self.load_training_data_questions()
        self.preprocess_question_answer_label()
        if self.kb_grouped_s is None:
            self.group_kb()
        X = np.array(self.get_all_features())
        y = np.array(self.get_labels())
        self.clf = LogisticRegressionCV(class_weight="balanced", cv=5)
        self.clf.fit(X, y)

    def save_model(self, filename=FILE_DIR + "classifier_lr.pck"):
        with open(filename, "wb") as f:
            pickle.dump((self.kb_grouped_s,
                         self.kb_grouped_p,
                         self.kb_grouped_o,
                         self.clf), f)

    def load_model(self, filename=FILE_DIR + "/classifier_lr.pck"):
        with open(filename, "rb") as f:
            self.kb_grouped_s, self.kb_grouped_p, self.kb_grouped_o, self.clf = pickle.load(f)

    def answer_question(self,
                        question: MultipleChoiceQuestion) -> MultipleChoiceAnswer:
        # pylint: disable=unused-variable
        if self.clf is None:
            self.load_model()
        if self.kb_grouped_s is None:
            self.group_kb()

        question_text = question.stem.lower()
        current_app.logger.info("Question: " + question_text)
        choices = question.choices
        choice_texts = [x.text for x in choices]
        current_app.logger.info("Choices: " + ";".join(choice_texts))

        question_preprocessed = self.spacy_accessor.lemmatize(
            " ".join(remove_stop_words(question_text)))
        choices_preprocessed = [self.spacy_accessor.lemmatize(
            " ".join(remove_stop_words(choice.lower())))
                                for choice in choice_texts]

        confidences = self.predict_proba_positive(question_preprocessed,
                                                  choices_preprocessed)

        return MultipleChoiceAnswer(
            [ChoiceConfidence(choice, confidence)
             for choice, confidence in zip(choices, confidences)]
        )

    def predict_proba_positive(self, question_text, choice_texts):
        features = [
            self.get_features_from_preprocessed_qal((question_text, choice))
            for choice in choice_texts]
        X = np.array(features)
        y_prediction = self.clf.predict_proba(X)[:, 1]
        return y_prediction


stop_words = set(stopwords.words('english'))


def remove_stop_words(sentence):
    word_tokens = word_tokenize(sentence)
    return [w for w in word_tokens if w not in stop_words]


def check_in(word, sentence):
    regex = re.compile(r"(^|\s)" + re.escape(word) + r"($|\s)")
    return regex.search(sentence) is not None


def transform_predicate(predicate):
    if predicate == "has_body_part":
        return "have"
    if "has_" in predicate:
        return "be"
    return predicate


if __name__ == "__main__":
    if len(argv) != 3:
        print("python3 preprocessing.py <kb_location> <training_set>")
    solver = MachineLearningSolver(argv[1], argv[2])
    solver.preprocess()
