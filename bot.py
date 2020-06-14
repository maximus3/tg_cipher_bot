#!/root/tg_cipher_bot/venv/bin/python
# -*- coding: utf-8 -*-
import telebot
from functools import wraps

# For Webhook
from aiohttp import web
import ssl

# My files
import config
import webhook
import func
import markups
import utils
import static_data
import views

# For data backup
from threading import Thread
import time

# For logs
import logging

logging.basicConfig(format=u'%(filename)s %(funcName)s [LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(name)s: %('
                           u'message)s',
                    level=logging.INFO, filename=config.DIRECTORY + 'cipher.log')

# Data
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


def data_backup():
    logger = logging.getLogger()
    try:
        views.save_data(sessionStorage)
        logger.info('Success!')
        if len(config.admin_ids) > 0:
            bot.send_message(config.admin_ids[0], 'Saving data: Success!')
            data = open(config.DIRECTORY + config.DATA_BACKUP_FILE, 'rb')
            bot.send_document(config.admin_ids[0], data)
    except Exception as e:
        logger.error(f'ERROR:\n{str(e)}')
        if len(config.admin_ids) > 0:
            bot.send_message(config.admin_ids[0], 'Saving data: ERROR:\n' + str(e))


# Запуск бота
bot = telebot.TeleBot(config.TOKEN)

try:
    sessionStorage = views.get_data()
    logging.info('Data recovery: Success!')
    print('Data recovery: Success!')
except Exception as e:
    logging.info('Data recovery: Error\n' + str(e))
    print('Data recovery: Error\n' + str(e))

logging.info('Server started')
print('Server started')

if len(config.admin_ids) > 0:
    bot.send_message(config.admin_ids[0], 'Server started')

Backup_Thread = Thread()


# DATA_BACKUP_END


# sessionStorage decorator
def ss_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message):
        chat_id = message.chat.id
        if chat_id not in sessionStorage:
            sessionStorage[chat_id] = utils.UserData()
        elif sessionStorage[chat_id].getInline() is not None:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=sessionStorage[chat_id].getInline(),
                                  text="Данное сообщение уже устарело")
            sessionStorage[chat_id].resetAll()
        return function_to_decorate(message)

    return wrapped


def isAdmin_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message):
        chat_id = message.chat.id
        if not sessionStorage[chat_id].isAdmin():
            return
        return function_to_decorate(message)

    return wrapped


@ss_dec
def backup_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message):
        global Backup_Thread
        if not Backup_Thread.is_alive():
            Backup_Thread = Thread(target=data_backup())
            Backup_Thread.start()
        return function_to_decorate(message)

    return wrapped


@backup_dec
def checkCards_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message):
        chat_id = message.chat.id
        user = sessionStorage[chat_id]
        step = user.getStep()
        if len(user.cards) == 0:
            bot.send_message(chat_id, 'У вас нет карт', reply_markup=markups.MUP[step])
            return
        return function_to_decorate(message)

    return wrapped


def noInline_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(message):
        chat_id = message.chat.id
        sessionStorage[chat_id].resetInline()
        return function_to_decorate(message)

    return wrapped


def checkInline_dec(function_to_decorate):
    @wraps(function_to_decorate)
    def wrapped(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user = sessionStorage[chat_id]
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text='Загрузка...\n' + call.message.text,
                              parse_mode='Markdown')
        if user.getInline() is None or user.getInline() != message_id:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Данное сообщение уже устарело")
            return
        user.resetInline()
        return function_to_decorate(call)

    return wrapped


@backup_dec
def check_step(message, step, text=None):
    chat_id = message.chat.id
    cur_step = sessionStorage[chat_id].getStep()
    if text is None:
        return cur_step == step
    return cur_step == step and message.text.lower() == text.lower()


def check_call_step(call, data, step=None):
    if not call.message:
        return False
    cur_data = call.data
    if step is None:
        return cur_data.startswith(data)
    chat_id = call.message.chat.id
    cur_step = sessionStorage[chat_id].getStep()
    return cur_step.startswith(step) and cur_data.startswith(data)


@bot.message_handler(commands=['admin'])
@ss_dec
@isAdmin_dec
def handle_admin(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, func.get_commands(static_data.ADMIN_COMMANDS))


@bot.message_handler(commands=['getdata'])
@ss_dec
@isAdmin_dec
def getdata(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, str(sessionStorage[chat_id]))


@bot.message_handler(commands=['getbackup'])
@ss_dec
@isAdmin_dec
def getbackup(message):
    chat_id = message.chat.id
    data = open(config.DIRECTORY + config.DATA_BACKUP_FILE, 'rb')
    bot.send_document(chat_id, data)


@bot.message_handler(commands=['null'])
@ss_dec
@isAdmin_dec
def null(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Ваш шаг был: ' + sessionStorage[chat_id].getStep())
    sessionStorage[chat_id].resetAll()


@bot.message_handler(commands=['start'])
@backup_dec
@noInline_dec
def handle_start(message):
    chat_id = message.chat.id
    step = sessionStorage[chat_id].getStep()
    if step in markups.MUP:
        bot.send_message(chat_id, static_data.START_TEXT, reply_markup=markups.MUP[step])
    else:
        bot.send_message(chat_id, static_data.START_TEXT)


@bot.message_handler(func=lambda message: check_step(message, 'main', '**мои карты**'), content_types=['text'])
@backup_dec
@noInline_dec
@checkCards_dec
def handle_step_main_watch(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')

    keybGR = user.get_cards_keyboard(chat_id, data='watchcard')
    sent = bot.send_message(chat_id, 'Выберите карту (всего карт ' + str(len(user.cards)) + ')',
                            reply_markup=keybGR)
    user.setInline(sent.message_id)

    logger.info(f'{chat_id}: OK')


@bot.message_handler(func=lambda message: check_step(message, 'main', '**добавить карту**'), content_types=['text'])
@backup_dec
@noInline_dec
def handle_step_main_add(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')

    user.nextStep('addcard_name')
    sent = bot.send_message(chat_id, 'Введите имя карты', reply_markup=markups.canc_pad)
    sessionStorage[chat_id].setInline(sent.message_id)

    logger.info(f'{chat_id}: OK')


@bot.message_handler(func=lambda message: check_step(message, 'main', '**удалить карту**'), content_types=['text'])
@backup_dec
@noInline_dec
@checkCards_dec
def handle_step_main_del(message):
    chat_id = message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')

    keybGR = user.get_cards_keyboard(chat_id, data='delete')

    sent = bot.send_message(chat_id, 'Выберите карту, которую хотите удалить', reply_markup=keybGR)
    sessionStorage[chat_id].setInline(sent.message_id)

    logger.info(f'{chat_id}: OK')


@bot.message_handler(func=lambda message: check_step(message, 'main_addcard_'), content_types=['text'])
@backup_dec
@noInline_dec
def handle_step_main_addcard(message):
    chat_id = message.chat.id
    text = message.text.lower()
    user = sessionStorage[chat_id]
    step = user.getStep()
    subj = step.split('_')[-1]
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')

    if subj == 'name':
        user.addCard = utils.CardData()

    info, added = user.setSubj(subj, text)
    log_info = static_data.MESSAGES[step][info]['forLog']
    user_info = static_data.MESSAGES[step][info]['forUser']

    logger.info(f'{chat_id}: {log_info}')

    if not added:
        sent = bot.send_message(chat_id, user_info, reply_markup=markups.canc_pad)
        user.setInline(sent.message_id)
        return

    user.prevStep()
    user.nextStep(user.addCard.order[subj])
    sent = bot.send_message(chat_id, user_info, reply_markup=markups.pin_pad)
    user.setInline(sent.message_id)


@bot.inline_handler(lambda query: len(query.query) >= 0)
@backup_dec
def query_text(query):
    chat_id = query.from_user.id
    name = query.query
    user = sessionStorage[chat_id]

    if len(user.cards) == 0:
        return

    results = user.getQueryKeyboard(name)
    bot.answer_inline_query(query.id, results)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'cancel'))
@checkInline_dec
def handle_inline_cancel(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')
    user.resetAll()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text='_Действие отменено_\n' + call.message.text,
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'deletecard_'))
@checkInline_dec
def handle_inline_deletecard(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    name = user.getWatchCardName()
    text = 'Выбрана карта *' + name + '*\n'
    if call.data.endwith('yes'):
        user.deleteWatchCard()
        text += 'Карта удалена'
    else:
        text += 'Удаление отменено'

    user.resetAll()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'delete_'))
@checkInline_dec
def handle_inline_delete(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('delete')

    num = int((call.data.split('_')).pop())
    name = user.setWatchCard(num)

    user_info = static_data.MESSAGES[step]['confirmDelete']['forUser'](name)

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=user_info,
                          parse_mode='Markdown',
                          reply_markup=markups.MUP[step])
    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'watchcard_'))
@checkInline_dec
def handle_inline_watchcard(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.nextStep('watchcard')

    num = int((call.data.split('_')).pop())
    name = user.setWatchCard(num)
    user.resetCode()

    user_info = static_data.MESSAGES[step]['confirmDelete']['forUser'](name)

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=user_info,
                          parse_mode='Markdown',
                          reply_markup=markups.pin_pad)
    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'pin_can'))
@checkInline_dec
def handle_inline_pin_can(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')
    user.resetAll()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text='_Действие отменено_\n' + call.message.text,
                          parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'pin_res'))
@checkInline_dec
def handle_inline_pin_res(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')
    text = call.message.text

    if step == 'main_addcard_date':
        user.addCard.resetDate()
        text = text.split('\n')
        text[-1] = '--/----'
        text = '\n'.join(text)
    else:
        text = text.replace('-', '#')
        text = text.replace('#', '')
        text += '----'
        if step == 'main_watchcard' or step == 'main_addcard_code':
            user.resetCode()
        elif step == 'main_addcard_pin':
            user.addCard.resetPin()
        elif step == 'main_addcard_cvc':
            user.addCard.resetCvc()
            text.pop()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='Markdown',
                          reply_markup=markups.pin_pad)
    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'pin_acc', 'main_watchcard'))
@checkInline_dec
def handle_inline_pin_acc_watchcard(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')

    name = user.getWatchCardName()
    num = user.getWatchCardNum()
    card_text = 'Карта: *' + name + '*\n' + 'Номер карты: `' + num + '`\n'

    info, decoded, text = user.decodeWatchCard()
    log_info = static_data.MESSAGES[step][info]['forLog']
    logger.info(f'{chat_id}: {log_info}')
    user.resetAll()

    if decoded:
        text = 'Защитный код принят. Данное сообщение исчезнет через 5 секунд.\n' + card_text + text
    else:
        text = static_data.MESSAGES[step][info]['forUser']

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='Markdown')

    if not decoded:
        return

    time.sleep(5)

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text='Сообщение устарело.' + card_text,
                          parse_mode='Markdown')

    logger.info(f'{chat_id}: OK')


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'pin_acc', 'main_addcard_'))
@checkInline_dec
def handle_inline_pin_acc_addcard(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    subj = step.split('_')[-1]
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Checking {subj}')

    info, added = user.setSubj(subj)
    log_info = static_data.MESSAGES[step][info]['forLog']
    user_info = static_data.MESSAGES[step][info]['forUser']
    logger.info(f'{chat_id}: {log_info}')

    if info == 'encode':
        user.resetAll()
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text=user_info,
                              parse_mode='Markdown')
        return

    if not added:
        user.resetSubj()
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text=user_info + call.message.text,
                              parse_mode='Markdown',
                              reply_markup=markups.pin_pad)
        user.setInline(call.message.message_id)
        return

    if subj == 'pin':
        user.cards.append(user.addCard)
        name = user.getWatchCardName()
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text='Карта *' + name + '* успешно добавлена!',
                              parse_mode='Markdown')
        return

    replyMarkup = markups.pin_pad
    if subj == 'code':
        replyMarkup = markups.canc_pad

    user.prevStep()
    user.nextStep(user.addCard.order[subj])
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=user_info,
                          reply_markup=replyMarkup)
    user.setInline(call.message.message_id)


@bot.callback_query_handler(func=lambda call: check_call_step(call, 'pin_', 'main_'))
@checkInline_dec
def handle_inline_pin_acc_addcard(call):
    chat_id = call.message.chat.id
    user = sessionStorage[chat_id]
    step = user.getStep()
    subj = step.split('_')[-1]
    logger = logging.getLogger(step)
    logger.info(f'{chat_id}: Started')

    if step == 'main_watchcard':
        subj = 'code'

    num = (call.data.split('_')).pop()

    length, num, digitCount = user.addNumSubj(subj, num)

    text = call.message.text

    text_for_send = []

    if subj != 'date':
        text = text.replace('-', '#')
        text = text.replace('#', '')

        text_for_send.append(text + '#' * (length - 1) + num + '-' * max(digitCount - length, 0))
        text_for_send.append(text + '#' * length + '-' * max(digitCount - length, 0))
    else:
        text = text.replace('-', '')
        if length < 3:
            text = text.replace('/', '')
            text_for_send.append(text + num + '-' * (max(digitCount - 4 - length, 0)) + '/----')
        else:
            text_for_send.append(text + num + '-' * (max(digitCount - length, 0)))

    for send_text in text_for_send:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=call.message.message_id,
                              text=send_text,
                              parse_mode='Markdown',
                              reply_markup=markups.pin_pad)
        if send_text != text_for_send[-1]:
            time.sleep(0.01)
    user.setInline(call.message.message_id)


# WEBHOOK_START

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=webhook.WEBHOOK_URL_BASE + webhook.WEBHOOK_URL_PATH,
                certificate=open(webhook.WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(webhook.WEBHOOK_SSL_CERT, webhook.WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=webhook.WEBHOOK_LISTEN,
    port=webhook.WEBHOOK_PORT,
    ssl_context=context,
)

# WEBHOOK_FINISH
