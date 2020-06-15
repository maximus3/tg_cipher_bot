from config import admin_ids
from static_data import TEST_DATA
from markups import canc_but
from m3crypto import decrypt, encrypt

from telebot import types


# Проверка текста, True если есть ошибка
# Вход: строка; ключ для проверки
# Выход: True если есть строка не соответствует нужному формату, False иначе
def wrong_format_text(text, tp):
    if tp == 'rus':
        for i in text:
            if (not ('а' <= i <= 'я')) and i != ' ' and i != 'ё':
                return True
        return False
    elif tp == 'rus1':
        for i in text:
            if (not ('а' <= i <= 'я')) and i != ' ' and (not ('0' <= i <= '9')) and i != 'ё':
                return True
        return False
    elif tp == 'eng1':
        for i in text:
            if (not ('A' <= i <= 'Z')) and i != ' ' and (not ('0' <= i <= '9')) and (
                    not ('a' <= i <= 'z')):
                return True
        return False
    elif tp == 'login':
        if len(text) > 32:
            return True
        for i in text:
            if (not ('0' <= i <= '9')) and (not ('a' <= i <= 'z')):
                return True
        return False
    elif tp == 'pass':
        if len(text) > 32:
            return True
        for i in text:
            if (not ('A' <= i <= 'Z')) and (not ('0' <= i <= '9')) and (not ('a' <= i <= 'z')):
                return True
        return False
    elif tp == 'ruseng1':
        for i in text:
            if (not ('A' <= i <= 'Z')) and i != 'ё' and i != ' ' and (not ('0' <= i <= '9')) and (
                    not ('a' <= i <= 'z')) and (not ('а' <= i <= 'я')) and (not ('А' <= i <= 'Я')):
                return True
        return False


class CardData:
    order = {
        'name': 'code',
        'code': 'num',
        'num': 'date',
        'date': 'cvc',
        'cvc': 'pin'
    }

    def __init__(self, data=None):
        self.name = ''
        self.num = ''
        self.date = ''
        self.cvc = ''
        self.pin = ''
        if data is not None:
            self.name = data['name']
            self.num = data['num']
            self.date = data['date']
            self.cvc = data['cvc']
            self.pin = data['pin']

    def setName(self, name):
        if len(name) > 32:
            return 'length', False

        if wrong_format_text(name, 'ruseng1'):
            return 'format', False

        self.name = name
        return 'ok', True

    def setNum(self, num):
        if not num.isdigit():
            return 'digits', False
        if len(num) != 16:
            return 'length', False
        sm = 0
        last = int(num[-1])
        for i in range(1, len(num)):
            prev = int(num[-i - 1])
            if i % 2 != 0:
                prev *= 2
            if prev > 9:
                prev -= 9
            sm += prev
        sm = 10 - (sm % 10)
        sm %= 10
        if last != sm:
            return 'num', False
        self.num = num
        return 'ok', True

    def setDate(self, code):
        from datetime import date
        if len(self.date) != 4 and len(self.date) != 6:
            return 'length', False
        month = int(self.date[:2])
        year = int(self.date[2:])
        if year < 100:
            year += 2000

        today = date.today()
        if not (0 < month < 13) or date(year, month, today.day) < today:
            return 'incorrect', False
        try:
            self.date = encrypt(code, self.date)
        except Exception:
            return 'encode', False
        return 'ok', True

    def setCvc(self, code):
        if not (2 < len(self.cvc) < 5):
            return 'length', False
        try:
            self.cvc = encrypt(code, self.cvc)
        except Exception:
            return 'encode', False
        return 'ok', True

    def setPin(self, code):
        if not (3 < len(self.pin) < 9):
            return 'length', False
        try:
            self.pin = encrypt(code, self.pin)
        except Exception:
            return 'encode', False
        return 'ok', True

    def resetPin(self):
        self.pin = ''

    def resetCvc(self):
        self.cvc = ''

    def resetDate(self):
        self.date = ''

    def addNumDate(self, num):
        self.date += num
        if len(self.date) > 6:
            self.date = self.date[:6]
            num = ''
        return len(self.date), num, 6

    def addNumCvc(self, num):
        self.cvc += num
        return len(self.cvc), num, 3

    def addNumPin(self, num):
        self.pin += num
        return len(self.pin), num, 4

    subjFunc = {
        'set': {
            'date': setDate,
            'cvc': setCvc,
            'pin': setPin,
            'num': setNum,
            'name': setName
        },
        'reset': {
            'date': resetDate,
            'cvc': resetCvc,
            'pin': resetPin
        },
        'addNum': {
            'date': addNumDate,
            'cvc': addNumCvc,
            'pin': addNumPin
        }
    }


class UserData:

    _defaultValues = {
        'admin': False,
        'step': 'main',
        'watchCardNum': -1,
        'code': '',
        'inline': None,
    }

    def __init__(self, chat_id, data=TEST_DATA):
        if len(data) == 0:
            data = TEST_DATA

        self._admin = (chat_id in admin_ids)
        self.chat_id = chat_id
        self._step = self._defaultValues['step']
        self._watchCardNum = self._defaultValues['watchCardNum']
        self._code = self._defaultValues['code']
        self._inline = self._defaultValues['inline']
        self.cards = [CardData(card) for card in data]
        self.addCard = CardData()

    def __str__(self):
        return str({
            'admin': self._admin,
            'step': self._step,
            'watchcard': self._watchCardNum,
            'code': self._code,
            'inline': self._inline,
            'cards': self.cards
        })

    def isAdmin(self):
        return self._admin

    def prevStep(self):
        step = self._step.split('_')
        step.pop()
        self._step = '_'.join(step)
        if len(self._step) == 0:
            self._step = self._defaultValues['step']
        return self._step

    def getStep(self):
        return self._step

    def nextStep(self, step):
        self._step += '_' + step
        return self._step

    def setInline(self, inline):
        self._inline = inline

    def resetInline(self):
        self._inline = self._defaultValues['inline']

    def getInline(self):
        return self._inline

    def resetAll(self):
        self._inline = self._defaultValues['inline']
        self._code = self._defaultValues['code']
        self._watchCardNum = self._defaultValues['watchCardNum']
        self._step = self._defaultValues['step']
        self.addCard = CardData()

    def setAddCardName(self, name):
        for card in self.cards:
            if name == card.name:
                return 'nameExists', False
        return self.addCard.setName(name)

    def get_cards_keyboard(self, data):
        keybGR = types.InlineKeyboardMarkup(row_width=1)

        for i, card in enumerate(self.cards):
            keybGR.add(types.InlineKeyboardButton(text=card.name, callback_data=data + '_' + str(i)))

        keybGR.add(canc_but)
        return keybGR

    def getQueryKeyboard(self, name):
        cards = []
        for i, card in enumerate(self.cards):
            if name in card.name:
                single_msg = types.InlineQueryResultArticle(
                    id=str(i), title=card.name,
                    input_message_content=types.InputTextMessageContent(
                        message_text='Карта *' + card.name + '*\nНомер: `' + str(card.num) + '`',
                        parse_mode='Markdown'),
                    reply_markup=None
                )
                cards.append(single_msg)
        return cards

    def setWatchCard(self, num):
        self._watchCardNum = num
        return self.cards[self._watchCardNum].name

    def getWatchCardName(self):
        return self.cards[self._watchCardNum].name

    def getWatchCardNum(self):
        return self.cards[self._watchCardNum].num

    def deleteWatchCard(self):
        self.cards.pop(self._watchCardNum)
        self._watchCardNum = -1

    def resetCode(self):
        self._code = self._defaultValues['code']

    def decodeWatchCard(self):
        card = self.cards[self._watchCardNum]
        try:
            date = decrypt(self._code, card.date)
            cvc = decrypt(self._code, card.cvc)
            pin = decrypt(self._code, card.pin)
        except Exception:
            return 'decode', False, ''
        if not (date.isdigit() and cvc.isdigit() and pin.isdigit()):
            return 'digit', False, ''

        text = 'Дата: ' + date[:2] + '/' + date[2:] + '\nCVC-код: ' + cvc + '\nPIN-код: _' + pin + '_'
        return 'ok', True, text

    def setCode(self):
        code = self._code
        if not 3 < len(code) < 17:
            return 'length', False

        '''
        for symbol in key:
            if ord(symbol) > 0xff:
                # That key won\'t work. Try another using only latin alphabet and numbers
                return False
        '''

        return 'ok', True

    def setSubj(self, subj, text=None):
        if subj == 'code':
            return self.setCode()
        card = self.addCard
        if text is not None:
            return self.addCard.subjFunc['set'][subj](card, text)
        return self.addCard.subjFunc['set'][subj](card, self._code)

    def resetSubj(self, subj):
        if subj == 'code':
            return self.resetCode()
        card = self.addCard
        return self.addCard.subjFunc['reset'][subj](card)

    def addNumSubj(self, subj, num):
        if subj == 'code':
            self._code += num
            return len(self._code), num, 4
        card = self.addCard
        return self.addCard.subjFunc['addNum'][subj](card, num)
