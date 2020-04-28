from flask import render_template

from quasimodo_website.models.question_form import QuestionForm
from quasimodo_website.question_answering.models import MultipleChoiceQuestion, \
    Choice
from quasimodo_website.question_answering.preprocessing import \
    MachineLearningSolver
from quasimodo_website.question_answering.blueprint import BP

solver = MachineLearningSolver()
solver.load_model()


@BP.route("/", methods=["GET", "POST"])
def question_page():
    form = QuestionForm()
    if form.validate_on_submit():
        question = MultipleChoiceQuestion(
            stem=form.question.data,
            choices=[
                Choice("A", form.answer0.data),
                Choice("B", form.answer1.data),
                Choice("C", form.answer2.data),
                Choice("D", form.answer3.data)
            ]
        )
        solution = solver.answer_question(question)
        best_confidence = 0
        best_text = ""
        for choice in solution.choiceConfidences:
            if best_confidence < choice.confidence:
                best_confidence = choice.confidence
                best_text = choice.choice.text
        return render_template("question_answer.html",
                               question=form.question.data,
                               answer0=form.answer0.data,
                               answer1=form.answer1.data,
                               answer2=form.answer2.data,
                               answer3=form.answer3.data,
                               solution=best_text)
    return render_template("question_page.html", form=form)