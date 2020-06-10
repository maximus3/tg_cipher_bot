#!/root/tg_cipher_bot/venv/bin/python
# -*- coding: utf-8 -*-
import telebot

# For Webhook
from aiohttp import web
import ssl

# Мои файлы
from config import *
from webhook import *
from func import *
from m3crypto import *
from markups import *
from utils import *

# Потоки и время для резервного копирования
from threading import Thread
import time

# Логгирование
import logging

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO, filename=directory + 'cipher.log')

# Хранилище данных о сессиях
sessionStorage = {}

# WEBHOOK_BEGIN

app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)

# WEBHOOK_END


def unic_decode(cards):
    for i in range(len(cards)):
        cards[i]['name'] = cards[i]['name'].decode('utf-8')
    return cards


def unic_encode(cards):
    data = []
    for i in range(len(cards)):
        data.append({
            'name': cards[i]['name'].encode('utf-8'),
            'num': cards[i]['num'],
            'date': cards[i]['date'],
            'cvc': cards[i]['cvc'],
            'pin': cards[i]['pin']
        })
    return str(data)


def users_recovery(users_data):
    data = {}
    count = users_data.pop(0)
    for i in range(count):
        user_id = users_data.pop(0)
        cards = eval(users_data.pop(0))
        data[user_id] = {
            'step': 'main',
            'cards': unic_decode(cards),
            'watchcard': -1,
            'code': ''
        }
    global sessionStorage
    sessionStorage = data.copy()


def data_recovery():
    FILE = open(directory + DATA_BACKUP_FILE, "r")
    users_data = eval(FILE.read())
    users_recovery(users_data)


def data_backup():
    data = sessionStorage.copy()

    users_data = [len(data)]
    for user_id in data:
        # users_data += data[user_id].get_backup_data()
        users_data += [user_id, unic_encode(data[user_id]['cards'])]

    FILE = open(directory + DATA_BACKUP_FILE, "w")
    FILE.write(str(users_data))
    FILE.close()
    time.sleep(DATA_BACKUP_TIME)


# Запуск бота
bot = telebot.TeleBot(TOKEN)

try:
    data_recovery()
    logging.info('Data recovery: Success!')
    print('Data recovery:  Success!')
except Exception as e:
    logging.info('Data recovery: Error\n' + str(e))
    print('Data recovery: Error\n' + str(e))

logging.info('Server started')
print('Server started')

try:
    bot.send_message(admin_ids[0], 'Бот запущен')
except Exception:
    pass


@bot.message_handler(commands=['admin'])
def admin(message):
    mid = message.chat.id
    if mid not in admin_ids:
        return

    bot.send_message(mid, """
/getdata - Данные пользователя
/null - обнуление шага
""")


@bot.message_handler(commands=['getdata'])
def getdata(message):
    mid = message.chat.id
    if mid not in admin_ids:
        return

    bot.send_message(mid, str(sessionStorage[mid]))


@bot.message_handler(commands=['null'])
def null(message):
    mid = message.chat.id
    if mid not in admin_ids:
        return

    bot.send_message(mid, 'Ваш шаг был: ' + sessionStorage[mid]['step'])
    sessionStorage[mid]['step'] = 'main'
    bot.send_message(mid, str(sessionStorage[mid]))


# Приветствие
# Вход: Сообщение
# Выход: -
@bot.message_handler(commands=['start'])
def start(message):
    mid = message.chat.id

    if sessionStorage.get(mid) == None:
        logging.info('start [%s]: Creating sessionStorage file', str(mid))
        sessionStorage[mid] = {
            'step': 'main',
            'cards': TEST_DATA,
            'watchcard': -1,
            'code': ''
        }

    step = sessionStorage[mid]['step']

    # bot.send_message(mid, '1234567812345678, 12/2025, 361, 9430\n\n' + str(sessionStorage[mid]))

    text = """
Привет, данный бот поможет тебе хранить данные твоих банковских карт абсолютно безопасно!
Для примера мы оставили тут карту "тест 1234" с защитным кодом 1234, попробуй посмотреть ее данные.
Пожалуйста, не забывайте защитный код, потому что он не хранится в системе и восстановить его будет невозможно!
Шифрование реализованно алгоритмом AES-128.
Вот в таком виде хранится информация по катре "тест 1234":
{
    'name':'Тест 1234',
    'num':'1234567812345678',
    'date':b'\x8c\x81\x99n#_$Z\xe0x\x82\x19\x02\xd3W\xdc',
    'cvc':b'\xf68|$\xf5g/u\xbf\xde\xa7\x05mN\x85\xd9',
    'pin':b'\x8a\xa6[\\M\xb3"\x04\xe9\xdbVY\xd1\xe2?\xde'
}
"""

    try:
        bot.send_message(mid, text, reply_markup=MUP[step])
    except Exception:
        bot.send_message(mid, text)


Backup_Thread = Thread()


# Главная функция, обработка всего приходящего текста
# Вход: Сообщение
# Выход: -
@bot.message_handler(content_types=['text'])
def main(message):
    global Backup_Thread
    mid = message.chat.id
    text = message.text.lower()

    if sessionStorage.get(mid) == None:
        sessionStorage[mid] = {
            'step': 'main',
            'cards': TEST_DATA,
            'watchcard': -1,
            'code': '',
            'addcard': None
        }

    if not Backup_Thread.is_alive():
        Backup_Thread = Thread(target=data_backup)
        Backup_Thread.start()

    step = sessionStorage[mid]['step']

    if sessionStorage[mid].get('inline') != None:
        bot.edit_message_text(chat_id=mid,
                              message_id=sessionStorage[mid].get('inline'),
                              text="Данное сообщение уже устарело")
        sessionStorage[mid].pop('inline')
        return

    if step == 'main':

        sessionStorage[mid]['code'] = ''
        sessionStorage[mid]['watchcard'] = -1
        sessionStorage[mid]['addcard'] = None

        if text == '**мои карты**':

            logging.info('main [%s]: Watch Cards', str(mid))
            if len(sessionStorage[mid]['cards']) == 0:
                logging.info('main [%s]: No Cards', str(mid))
                bot.send_message(mid, 'У вас нет карт', reply_markup=MUP[step])
                return
            logging.info('main [%s]: Getting cards', str(mid))
            keybGR = get_cards(mid, 'watchcard')
            keybGR.add(cancbut)
            logging.info('main [%s]: Got', str(mid))

            sent = bot.send_message(mid, 'Выберите карту (всего карт ' + str(len(sessionStorage[mid]['cards'])) + ')',
                                    reply_markup=keybGR)
            sessionStorage[mid]['inline'] = sent.message_id

        elif text == '**добавить карту**':

            logging.info('main [%s]: Add Card', str(mid))
            sessionStorage[mid]['step'] += '_addcard'
            sent = bot.send_message(mid, 'Введите имя карты', reply_markup=cancpad)
            sessionStorage[mid]['inline'] = sent.message_id
            bot.register_next_step_handler(sent, card_add1)

        elif text == '**удалить карту**':

            logging.info('main [%s]: Delete Cards', str(mid))
            if len(sessionStorage[mid]['cards']) == 0:
                logging.info('main [%s]: No Cards', str(mid))
                bot.send_message(mid, 'У вас нет карт', reply_markup=MUP[step])
                return

            logging.info('main [%s]: Getting cards', str(mid))
            keybGR = get_cards(mid, 'delete')
            keybGR.add(cancbut)
            logging.info('main [%s]: Got', str(mid))

            sent = bot.send_message(mid, 'Выберите карту, которую хотите удалить', reply_markup=keybGR)
            sessionStorage[mid]['inline'] = sent.message_id


def get_cards(mid, data=None, tp=0, text=''):
    if tp == 0 or tp == 2:
        keybGR = types.InlineKeyboardMarkup()
    elif tp == 1:
        cards = []

    if mid not in sessionStorage:
        logging.info('main [%s]: No ID', str(mid))
        return []

    for i, elem in enumerate(sessionStorage[mid]['cards']):
        if tp == 0:
            keybGR.add(types.InlineKeyboardButton(text=elem['name'], callback_data=data + '_' + str(i)))
        elif tp == 1:
            cards.append(elem['name'])
        elif tp == 2:
            if text in elem['name']:
                keybGR.add(types.InlineKeyboardButton(text=elem['name'], callback_data=data + '_' + str(i)))

    if tp == 0 or tp == 2:
        return keybGR
    elif tp == 1:
        return cards


def check_num(num):
    sm = 0
    l = int(num[-1])
    for i in range(1, len(num)):
        p = int(num[-i - 1])
        if i % 2 != 0:
            p *= 2
        if p > 9:
            p -= 9
        sm += p
    sm = 10 - (sm % 10)
    sm %= 10
    print(sm, l)
    if l != sm:
        return False
    return True


# Name
def card_add1(message):
    mid = message.chat.id
    text = message.text.lower()
    if sessionStorage[mid]['step'] != 'main_addcard':
        logging.info('card_add1 [%s]: Another step (%s)', str(mid), sessionStorage[mid]['step'])
        return
    sessionStorage[mid]['inline'] = None

    logging.info('card_add1 [%s]: Getting cards', str(mid))
    cards = get_cards(mid, tp=1)
    logging.info('card_add1 [%s]: Got', str(mid))

    if text in cards:
        logging.info('card_add1 [%s]: Name already exists', str(mid))
        sent = bot.send_message(mid, 'Карта с таким именем  уже существует.\nПожалуйста, введите другое имя',
                                reply_markup=cancpad)
        sessionStorage[mid]['inline'] = sent.message_id
        bot.register_next_step_handler(sent, card_add1)
        return

    if len(text) > 32:
        logging.info('card_add1 [%s]: Name is too long', str(mid))
        sent = bot.send_message(mid, 'Слишком длинное название (не более 32 символов)\nПожалуйста, введите другое имя',
                                reply_markup=cancpad)
        sessionStorage[mid]['inline'] = sent.message_id
        bot.register_next_step_handler(sent, card_add1)
        return

    if check_text(text, 'ruseng1'):
        logging.info('card_add1 [%s]: Wrong format', str(mid))
        sent = bot.send_message(mid, 'Используйте русские, английские буквы и цифры\nПожалуйста, введите другое имя',
                                reply_markup=cancpad)
        sessionStorage[mid]['inline'] = sent.message_id
        bot.register_next_step_handler(sent, card_add1)
        return

    logging.info('card_add1 [%s]: Creating addcard', str(mid))
    sessionStorage[mid]['addcard'] = {
        'name': text,
        'num': '',
        'date': '',
        'cvc': '',
        'pin': ''
    }

    sessionStorage[mid]['step'] += '_code'
    sent = bot.send_message(mid, '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nПридумайте защитный код (до 16 символов)\n----',
                            reply_markup=pin_pad)
    sessionStorage[mid]['inline'] = sent.message_id


# Num
def card_add2(message):
    mid = message.chat.id
    text = message.text.lower()
    if sessionStorage[mid]['step'] != 'main_addcard_num':
        logging.info('card_add2 [%s]: Another step (%s)', str(mid), sessionStorage[mid]['step'])
        return
    sessionStorage[mid]['inline'] = None

    if not text.isdigit():
        logging.info('card_add2 [%s]: Not digits', str(mid))
        sent = bot.send_message(mid, 'Пожалуйста, используйте только цифры\nПожалуйста, введите номер карты заново',
                                reply_markup=cancpad)
        sessionStorage[mid]['inline'] = sent.message_id
        bot.register_next_step_handler(sent, card_add2)
        return

    if len(text) != 16:
        logging.info('card_add2 [%s]: Not enough simbols', str(mid))
        sent = bot.send_message(mid, 'Длина номера должна быть 16 символов\nПожалуйста, введите номер карты заново',
                                reply_markup=cancpad)
        sessionStorage[mid]['inline'] = sent.message_id
        bot.register_next_step_handler(sent, card_add2)
        return

    if not check_num(text):
        logging.info('card_add2 [%s]: Not num', str(mid))
        sent = bot.send_message(mid, 'Номер неверен.\nПожалуйста, введите номер карты заново', reply_markup=cancpad)
        sessionStorage[mid]['inline'] = sent.message_id
        bot.register_next_step_handler(sent, card_add2)
        return

    sessionStorage[mid]['addcard']['num'] = text

    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
    sessionStorage[mid]['step'] += '_date'
    step = sessionStorage[mid]['step']
    sent = bot.send_message(mid, '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите дату окончания срока действия карты\n--/----',
                            reply_markup=pin_pad)
    sessionStorage[mid]['inline'] = sent.message_id


def watch_card(call):
    mid = call.message.chat.id
    step = sessionStorage[mid]['step']

    i = sessionStorage[mid]['watchcard']
    code = sessionStorage[mid]['code']
    name = sessionStorage[mid]['cards'][i]['name']

    num = sessionStorage[mid]['cards'][i]['num']
    date = sessionStorage[mid]['cards'][i]['date']
    cvc = sessionStorage[mid]['cards'][i]['cvc']
    pin = sessionStorage[mid]['cards'][i]['pin']

    try:
        # num = decrypt(code, num)
        date = decrypt(code, date)
        cvc = decrypt(code, cvc)
        pin = decrypt(code, pin)
    except Exception:
        logging.info('pin_acc  [%s]: Decrypt error', str(mid))
        sessionStorage[mid]['code'] = ''
        sessionStorage[mid]['watchcard'] = -1
        sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
        step = sessionStorage[mid]['step']
        bot.edit_message_text(chat_id=mid,
                              message_id=call.message.message_id,
                              text='Произошла ошибка при декодировании.\nВозможно, защитный код введен неправильно. Попробуйте еще раз',
                              parse_mode='Markdown')
        return
    logging.info('pin_acc  [%s]: Decrypted', str(mid))

    if (not num.isdigit()) or (not date.isdigit()) or (not cvc.isdigit()) or (not pin.isdigit()):
        logging.info('pin_acc  [%s]: Not digit', str(mid))
        sessionStorage[mid]['code'] = ''
        sessionStorage[mid]['watchcard'] = -1
        sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
        step = sessionStorage[mid]['step']
        bot.edit_message_text(chat_id=mid,
                              message_id=call.message.message_id,
                              text='Произошла ошибка.\nВозможно, защитный код введен неправильно. Попробуйте еще раз',
                              parse_mode='Markdown')
        return

    sessionStorage[mid]['code'] = ''
    sessionStorage[mid]['watchcard'] = -1
    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
    step = sessionStorage[mid]['step']
    keybGR = types.InlineKeyboardMarkup()

    bot.edit_message_text(chat_id=mid,
                          message_id=call.message.message_id,
                          text='''
Защитный код принят. Данное сообщение исчезнет через 5 секунд.
Карта: *''' + name + '''*
Номер карты: `''' + num + '''`
Дата: ''' + date[:2] + '/' + date[2:] + '''
CVC-код: ''' + cvc + '''
PIN-код: _''' + pin + '_',
                          parse_mode='Markdown',
                          reply_markup=keybGR)

    logging.info('pin_acc  [%s]: Waiting 10 sec...', str(mid))
    time.sleep(5)
    logging.info('pin_acc  [%s]: Done', str(mid))

    bot.edit_message_text(chat_id=mid,
                          message_id=call.message.message_id,
                          text='''
Сообщение устарело.
Карта: *''' + name + '''*
Номер карты: `''' + num + '`',
                          parse_mode='Markdown')


# Инлайн-режим с непустым запросом
@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(query):
    try:

        uid = query.from_user.id
        text = query.query

        cards = get_cards(uid, tp=1)
        if not cards or len(cards) == 0:
            return

        results = []

        # Клавиатура
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="test"))

        for i, elem in enumerate(cards):
            if text in elem:
                single_msg = types.InlineQueryResultArticle(
                    id=str(i), title=elem,
                    input_message_content=types.InputTextMessageContent(
                        message_text='Карта *' + elem + '*\nНомер: `' + str(
                            sessionStorage[uid]['cards'][i]['num']) + '`', parse_mode='Markdown'),
                    reply_markup=None
                )
                results.append(single_msg)

        bot.answer_inline_query(query.id, results)

    except Exception as e:
        print(str(e))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        mid = call.message.chat.id
        step = sessionStorage[mid]['step']

        bot.edit_message_text(chat_id=mid,
                              message_id=call.message.message_id,
                              text='Загрузка...\n' + call.message.text,
                              parse_mode='Markdown',
                              reply_markup=types.InlineKeyboardMarkup())

        if sessionStorage[mid].get('inline') == None or sessionStorage[mid]['inline'] != call.message.message_id:
            bot.edit_message_text(chat_id=mid, message_id=call.message.message_id, text="Данное сообщение уже устарело")
            return

        sessionStorage[mid].pop('inline')

        if call.data == 'cancel':
            logging.info('cancel [%s]: Cancel', str(mid))
            sessionStorage[mid]['step'] = 'main'
            sessionStorage[mid]['code'] = ''
            sessionStorage[mid]['watchcard'] = -1
            sessionStorage[mid]['addcard'] = None
            bot.edit_message_text(chat_id=mid,
                                  message_id=call.message.message_id,
                                  text='_Действие отменено_\n' + call.message.text,
                                  parse_mode='Markdown')

        elif call.data == 'deletecard_yes':
            logging.info('deletecard_yes [%s]: Deleting card', str(mid))
            name = sessionStorage[mid]['cards'][sessionStorage[mid]['watchcard']]['name']
            logging.info('deletecard_yes  [%s]: Got name', str(mid))
            num = sessionStorage[mid]['watchcard']
            logging.info('deletecard_yes  [%s]: Got num', str(mid))
            sessionStorage[mid]['cards'].pop(num)
            logging.info('deletecard_yes  [%s]: Deleted', str(mid))
            sessionStorage[mid]['watchcard'] = -1
            sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
            step = sessionStorage[mid]['step']
            bot.edit_message_text(chat_id=mid,
                                  message_id=call.message.message_id,
                                  text='Выбрана карта *' + name + '*\nКарта удалена',
                                  parse_mode='Markdown')

        elif call.data == 'deletecard_no':
            name = sessionStorage[mid]['cards'][sessionStorage[mid]['watchcard']]['name']
            logging.info('deletecard_no  [%s]: Got name', str(mid))
            sessionStorage[mid]['watchcard'] = -1
            sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
            step = sessionStorage[mid]['step']
            bot.edit_message_text(chat_id=mid,
                                  message_id=call.message.message_id,
                                  text='Выбрана карта *' + name + '*\nУдаление отменено',
                                  parse_mode='Markdown')

        elif 'delete_' in call.data:
            sessionStorage[mid]['step'] += '_delete'
            num = int(((call.data).split('_')).pop())
            logging.info('delete_  [%s]: Got num', str(mid))
            sessionStorage[mid]['watchcard'] = num
            name = sessionStorage[mid]['cards'][sessionStorage[mid]['watchcard']]['name']
            logging.info('delete_  [%s]: Got name', str(mid))
            keybGR = types.InlineKeyboardMarkup()
            cbtn1 = types.InlineKeyboardButton(text='Удалить', callback_data='deletecard_yes')
            cbtn2 = types.InlineKeyboardButton(text='Отмена', callback_data='deletecard_no')
            keybGR.add(cbtn1, cbtn2)
            bot.edit_message_text(chat_id=mid,
                                  message_id=call.message.message_id,
                                  text='Выбрана карта *' + name + '*\nВы уверены, что хотите удалить ее из базы? Отмена невозможна!',
                                  parse_mode='Markdown',
                                  reply_markup=keybGR)
            sessionStorage[mid]['inline'] = call.message.message_id

        elif 'watchcard_' in call.data:
            sessionStorage[mid]['step'] += '_watchcard'
            logging.info('watchcard_  [%s]: Watching card', str(mid))
            num = int(((call.data).split('_')).pop())
            sessionStorage[mid]['watchcard'] = num
            logging.info('watchcard_  [%s]: Got num', str(mid))
            name = sessionStorage[mid]['cards'][sessionStorage[mid]['watchcard']]['name']
            logging.info('watchcard_  [%s]: Got name', str(mid))

            sessionStorage[mid]['code'] = ''

            bot.edit_message_text(chat_id=mid,
                                  message_id=call.message.message_id,
                                  text='$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВыбрана карта *' + name + '*\nВведите защитный код:\n----',
                                  parse_mode='Markdown',
                                  reply_markup=pin_pad)
            sessionStorage[mid]['inline'] = call.message.message_id

        elif call.data == 'pin_can':
            logging.info('pin_can  [%s]: Cancelling', str(mid))
            sessionStorage[mid]['code'] = ''
            sessionStorage[mid]['watchcard'] = -1
            sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
            if step != 'main_watchcard':
                sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
            step = sessionStorage[mid]['step']
            bot.edit_message_text(chat_id=mid,
                                  message_id=call.message.message_id,
                                  text='_Действие отменено_\n' + call.message.text,
                                  parse_mode='Markdown')

        elif call.data == 'pin_res':
            logging.info('pin_res  [%s]: Resetting pin', str(mid))

            if step == 'main_watchcard' or step == 'main_addcard_code':
                sessionStorage[mid]['code'] = ''
            elif step == 'main_addcard_pin':
                sessionStorage[mid]['addcard']['pin'] = ''
            elif step == 'main_addcard_cvc':
                sessionStorage[mid]['addcard']['cvc'] = ''
            elif step == 'main_addcard_date':
                sessionStorage[mid]['addcard']['date'] = ''

            ltext = call.message.text

            if step == 'main_watchcard' or step == 'main_addcard_code' or step == 'main_addcard_pin' or step == 'main_addcard_cvc':
                ltext = ltext.replace('-', '#')
                ltext = ltext.replace('#', '')
                if step == 'main_addcard_cvc':
                    ltext += '---'
                else:
                    ltext += '----'
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text=ltext,
                                      parse_mode='Markdown',
                                      reply_markup=pin_pad)
            elif step == 'main_addcard_date':
                ltext = ltext.split('\n')
                ltext[-1] = '--/----'
                ltext = '\n'.join(ltext)
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text=ltext,
                                      parse_mode='Markdown',
                                      reply_markup=pin_pad)

            sessionStorage[mid]['inline'] = call.message.message_id



        elif call.data == 'pin_acc':
            logging.info('pin_acc  [%s]: Accepting pin', str(mid))
            code = sessionStorage[mid]['code']
            if step == 'main_watchcard':
                watch_card(call)

            elif step == 'main_addcard_code':
                logging.info('pin_acc  [%s]: Checking code', str(mid))
                if len(code) < 4 or len(code) > 16:
                    logging.info('pin_acc  [%s]: Wrong format of code', str(mid))
                    sessionStorage[mid]['code'] = ''
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='Защитный код должен содержать от 4 до 16 символов. Попробуйте еще раз.\n' + '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nПридумайте защитный код (до 16 символов)\n----',
                                          parse_mode='Markdown',
                                          reply_markup=pin_pad)
                    sessionStorage[mid]['inline'] = call.message.message_id
                    return
                logging.info('pin_acc  [%s]: Checked', str(mid))

                sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                sessionStorage[mid]['step'] += '_num'
                step = sessionStorage[mid]['step']
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text='Введите номер карты',
                                      reply_markup=cancpad)
                sessionStorage[mid]['inline'] = call.message.message_id
                bot.register_next_step_handler(call.message, card_add2)

            elif step == 'main_addcard_date':
                if len(sessionStorage[mid]['addcard']['date']) != 6:
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='Вы ввели недостаточное количество символов, введите еще.\n' + call.message.text,
                                          parse_mode='Markdown',
                                          reply_markup=pin_pad)
                    sessionStorage[mid]['inline'] = call.message.message_id
                    return

                m = sessionStorage[mid]['addcard']['date'][:2]
                y = sessionStorage[mid]['addcard']['date'][2:]
                m = int(m)
                y = int(y)
                if m < 1 or m > 12 or y < 2018:
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    step = sessionStorage[mid]['step']
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='Введенная дата некорректна')
                    return

                try:
                    sessionStorage[mid]['addcard']['date'] = encrypt(code, sessionStorage[mid]['addcard']['date'])
                except Exception:
                    logging.info('pin_acc  [%s]: Decrypt error', str(mid))
                    sessionStorage[mid]['code'] = ''
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    step = sessionStorage[mid]['step']
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='Произошла ошибка при кодировании')
                    return

                sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                sessionStorage[mid]['step'] += '_cvc'
                step = sessionStorage[mid]['step']
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text='$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите CVC код\n---',
                                      reply_markup=pin_pad)
                sessionStorage[mid]['inline'] = call.message.message_id

            elif step == 'main_addcard_cvc':
                if len(sessionStorage[mid]['addcard']['cvc']) < 3 or len(sessionStorage[mid]['addcard']['cvc']) > 4:
                    sessionStorage[mid]['addcard']['cvc'] = ''
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='CVC код должен содержать от 3 до 4 символов. Попробуйте еще раз\n' + '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите CVC код\n---',
                                          parse_mode='Markdown',
                                          reply_markup=pin_pad)
                    sessionStorage[mid]['inline'] = call.message.message_id
                    return

                try:
                    sessionStorage[mid]['addcard']['cvc'] = encrypt(code, sessionStorage[mid]['addcard']['cvc'])
                except Exception:
                    logging.info('pin_acc  [%s]: Decrypt error', str(mid))
                    sessionStorage[mid]['code'] = ''
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    step = sessionStorage[mid]['step']
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='Произошла ошибка при кодировании')
                    return

                sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                sessionStorage[mid]['step'] += '_pin'
                step = sessionStorage[mid]['step']
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text='$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите PIN код\n----',
                                      reply_markup=pin_pad)
                sessionStorage[mid]['inline'] = call.message.message_id

            elif step == 'main_addcard_pin':
                logging.info('pin_acc  [%s]: Checking pin', str(mid))
                if len(sessionStorage[mid]['addcard']['pin']) < 4 or len(sessionStorage[mid]['addcard']['pin']) > 8:
                    logging.info('pin_acc  [%s]: Not enough simbols', str(mid))
                    sessionStorage[mid]['addcard']['pin'] = ''
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='PIN код должен состоять из 4 символов. Попробуйте еще раз\n' + '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите PIN код\n----',
                                          parse_mode='Markdown',
                                          reply_markup=pin_pad)
                    sessionStorage[mid]['inline'] = call.message.message_id
                    return

                logging.info('pin_acc  [%s]: Checked', str(mid))

                try:
                    logging.info('pin_acc  [%s]: Trying to encrypt', str(mid))
                    sessionStorage[mid]['addcard']['pin'] = encrypt(code, sessionStorage[mid]['addcard']['pin'])
                    logging.info('pin_acc  [%s]: Encrypted', str(mid))
                except Exception:
                    logging.info('pin_acc  [%s]: Encrypt error', str(mid))
                    sessionStorage[mid]['code'] = ''
                    sessionStorage[mid]['addcard'] = None
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                    step = sessionStorage[mid]['step']
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text='Произошла ошибка при кодировании')
                    return

                logging.info('pin_acc  [%s]: Adding card', str(mid))
                sessionStorage[mid]['cards'].append(sessionStorage[mid]['addcard'])
                logging.info('pin_acc  [%s]: Added', str(mid))
                name = sessionStorage[mid]['addcard']['name']
                sessionStorage[mid]['addcard'] = None
                sessionStorage[mid]['code'] = ''

                sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                sessionStorage[mid]['step'] = prev_step(sessionStorage[mid]['step'])
                step = sessionStorage[mid]['step']
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text='Карта *' + name + '* успешно добавлена!',
                                      parse_mode='Markdown')

        elif 'pin_' in call.data:
            logging.info('pin_  [%s]: Entering pin', str(mid))
            num = ((call.data).split('_')).pop()

            if step == 'main_watchcard' or step == 'main_addcard_code':
                sessionStorage[mid]['code'] += num
                ln = len(sessionStorage[mid]['code'])
            elif step == 'main_addcard_pin':
                sessionStorage[mid]['addcard']['pin'] += num
                ln = len(sessionStorage[mid]['addcard']['pin'])
            elif step == 'main_addcard_cvc':
                sessionStorage[mid]['addcard']['cvc'] += num
                ln = len(sessionStorage[mid]['addcard']['cvc'])
            elif step == 'main_addcard_date':
                sessionStorage[mid]['addcard']['date'] += num
                ln = len(sessionStorage[mid]['addcard']['date'])
                if ln > 6:
                    sessionStorage[mid]['addcard']['date'] = sessionStorage[mid]['addcard']['date'][:6]
                    num = ''

            ltext = call.message.text

            if step == 'main_watchcard' or step == 'main_addcard_code' or step == 'main_addcard_pin' or step == 'main_addcard_cvc':
                ltext = ltext.replace('-', '#')
                ltext = ltext.replace('#', '')
                k = 4
                if step == 'main_addcard_cvc':
                    k = 3
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text=ltext + '#' * (ln - 1) + num + '-' * (max(k - ln, 0)),
                                      parse_mode='Markdown',
                                      reply_markup=pin_pad)
                time.sleep(0.01)
                bot.edit_message_text(chat_id=mid,
                                      message_id=call.message.message_id,
                                      text=ltext + '#' * ln + '-' * (max(k - ln, 0)),
                                      parse_mode='Markdown',
                                      reply_markup=pin_pad)
            elif step == 'main_addcard_date':
                ltext = ltext.replace('-', '')
                if ln < 3:
                    ltext = ltext.replace('/', '')
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text=ltext + num + '-' * (max(2 - ln, 0)) + '/----',
                                          parse_mode='Markdown',
                                          reply_markup=pin_pad)
                else:
                    bot.edit_message_text(chat_id=mid,
                                          message_id=call.message.message_id,
                                          text=ltext + num + '-' * (max(6 - ln, 0)),
                                          parse_mode='Markdown',
                                          reply_markup=pin_pad)

            sessionStorage[mid]['inline'] = call.message.message_id

    # Если сообщение из инлайн-режима
    elif call.inline_message_id:

        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")


# WEBHOOK_START

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)

# WEBHOOK_FINISH
