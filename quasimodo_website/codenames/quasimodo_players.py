import sqlalchemy

from quasimodo_website.codenames.codenames import CodenameColor
from quasimodo_website.codenames.codenames_agents import SpyMaster, Clue
from quasimodo_website.models import Fact


class QuasimodoSpyMaster(SpyMaster):

    def give_clue(self):
        good_words = self.codenames.get_remaining_words_by_color(
            self.color
        )
        if self.color == CodenameColor.RED:
            other_color = CodenameColor.BLUE
        else:
            other_color = CodenameColor.RED
        bad_words = self.codenames.get_remaining_words_by_color(
            other_color
        ) + [self.codenames.get_assassin_card()]
        good_words = [x.lower() for x in good_words]
        bad_words = [x.lower() for x in bad_words]

        # Get Good Facts
        good_facts = []
        for good_word in good_words:
            good_facts += Fact.query \
                .with_entities(Fact.subject, Fact.object, Fact.plausibility)\
                .filter(Fact.subject == good_word) \
                .filter(
                    sqlalchemy.not_(
                        Fact.object.contains(' ')
                    )
                ).filter(
                    Fact.plausibility > 0.5
                ).order_by(Fact.plausibility.desc()).all()
        print("I have good words", len(good_facts))

        # Get Bad Facts
        bad_facts = []
        for bad_word in bad_words:
            bad_facts += Fact.query \
                .with_entities(Fact.subject, Fact.object, Fact.plausibility)\
                .filter(Fact.subject == bad_word) \
                .filter(
                    sqlalchemy.not_(
                        Fact.object.contains(' ')
                    )
                ).order_by(Fact.plausibility.desc()).all()
        print("I have bad words", len(bad_facts))

        # Find first object appearing twice but not in bad_facts
        bad_objects = {x[1] for x in bad_facts}
        seen_object = dict()
        first_correct = None
        for subject, obj, plausibility in good_facts:
            if not self.codenames.is_valid_clue(obj):
                continue
            if (obj in seen_object
                    and obj not in bad_objects
                    and seen_object[obj] != subject):
                print(seen_object[obj], subject, plausibility)
                return Clue(obj, 2)
            if first_correct is None and obj not in bad_objects:
                first_correct = obj
            seen_object[obj] = subject
        if first_correct is None:
            return Clue("guess", 1)
        return Clue(first_correct, 1)
