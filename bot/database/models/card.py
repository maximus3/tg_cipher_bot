import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel
from .user import User


class Card(BaseModel):
    __tablename__ = 'card'

    name: orm.Mapped[str] = sa.Column(
        'name',
        sa.String,
        nullable=False,
        doc='Name of card.',
    )
    num: orm.Mapped[str] = sa.Column(
        'num',
        sa.String,
        nullable=False,
        doc='Num of card.',
    )
    date: orm.Mapped[str] = sa.Column(
        'date',
        sa.String,
        nullable=False,
        doc='Date.',
    )
    cvc: orm.Mapped[str] = sa.Column(
        'cvc',
        sa.String,
        nullable=False,
        doc='Crypt cvc.',
    )
    pin: orm.Mapped[str] = sa.Column(
        'pin',
        sa.String,
        nullable=False,
        doc='Crypt pin.',
    )

    user_id: orm.Mapped[uuid.UUID | str] = sa.Column(  # type: ignore
        sa.ForeignKey(User.id, ondelete='CASCADE'),
        nullable=False,
        unique=False,
        index=True,
        doc='User id',
    )
    user: orm.Mapped[User] = orm.relationship(  # type: ignore
        User,
        foreign_keys=[user_id],
        doc='User',
    )
