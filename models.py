import peewee

from config import DATA_BACKUP_FILE

database = peewee.SqliteDatabase(DATA_BACKUP_FILE)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    chat_id = peewee.IntegerField(unique=True, verbose_name='Teleram chat id')


class Card(BaseModel):
    user = peewee.ForeignKeyField(User, backref='cards', on_delete='CASCADE')
    name = peewee.CharField(max_length=32)
    num = peewee.CharField(max_length=16)
    date = peewee.CharField()
    cvc = peewee.CharField()
    pin = peewee.CharField()