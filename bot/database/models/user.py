import sqlalchemy as sa

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    chat_id = sa.Column(
        'chat_id',
        sa.String,
        nullable=False,
        unique=True,
        index=True,
        doc='Telegram chat id.',
    )

    def __repr__(self):  # type: ignore
        return f'<User {self.chat_id}>'
