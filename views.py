from models import User, Card, database
from config import DIRECTORY, DATA_BACKUP_FILE
from utils import UserData
from static_data import DATA_BACKUP_TIME
import os
import time


def create_tables():
    if os.path.exists(DIRECTORY + DATA_BACKUP_FILE):
        return False
    with database:
        database.create_tables([User, Card])
    return True


def get_data():
    if create_tables():
        return {}
    sessionStorage = {}
    for user in User.select():
        chat_id = user.chat_id
        data = []
        for card in user.cards:
            data.append({
                'name': card.name,
                'num': card.num,
                'date': bytes.fromhex(card.date),
                'cvc': bytes.fromhex(card.cvc),
                'pin': bytes.fromhex(card.pin)
            })
        sessionStorage[chat_id] = UserData(chat_id=chat_id, data=data)
    return sessionStorage


def save_data(sessionStorage):
    prev_name = DIRECTORY + 'prev_' + DATA_BACKUP_FILE
    name = DIRECTORY + DATA_BACKUP_FILE
    if os.path.exists(prev_name):
        os.remove(prev_name)

    os.rename(name, prev_name)

    create_tables()

    for chat_id in sessionStorage:
        user = sessionStorage[chat_id]
        user_db = User.create(chat_id=chat_id)
        for card in user.cards:
            Card.create(user=user_db, name=card.name, num=card.num, date=card.date.hex(), cvc=card.cvc.hex(),
                        pin=card.pin.hex())
    time.sleep(DATA_BACKUP_TIME)
    return True
