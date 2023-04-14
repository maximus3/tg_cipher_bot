# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from bot.database.models import Card


class CardFactory(Factory):
    class Meta:
        model = Card

    name = fuzzy.FuzzyText()
    num = fuzzy.FuzzyText()
    date = fuzzy.FuzzyText()
    cvc = fuzzy.FuzzyText()
    pin = fuzzy.FuzzyText()
    user_id = Faker('uuid4')
