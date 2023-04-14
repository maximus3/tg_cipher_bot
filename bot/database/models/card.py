import sqlalchemy as sa

from .base import BaseModel


class Card(BaseModel):
    __tablename__ = 'card'

    name = sa.Column(
        'name',
        sa.String,
        nullable=False,
        doc='Name of card.',
    )
    num = sa.Column(
        'num',
        sa.String,
        nullable=False,
        doc='Num of card.',
    )
    date = sa.Column(
        'date',
        sa.String,
        nullable=False,
        doc='Date.',
    )
    cvc = sa.Column(
        'cvc',
        sa.String,
        nullable=False,
        doc='Crypt cvc.',
    )
    pin = sa.Column(
        'pin',
        sa.String,
        nullable=False,
        doc='Crypt pin.',
    )

    user_id = sa.Column(
        sa.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
