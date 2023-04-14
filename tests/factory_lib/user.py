# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, fuzzy

from bot.database.models import User


class UserFactory(Factory):
    class Meta:
        model = User

    chat_id = fuzzy.FuzzyText()
