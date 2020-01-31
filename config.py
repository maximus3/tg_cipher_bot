from telebot import types

TOKEN = 'TOKEN'
host = 'HOST'
port = PORT
directory = ''
DATA_BACKUP_FILE = ''

# Версия телеграм-бота
version = '0.1.0 Beta'

admin_ids = []

DATA_BACKUP_TIME = 60

# Изменения
chng = """

"""

# Описание телеграм-бота
desc = """

"""

TEST_DATA = [{
    'name':'TEST 1234',
    'num':'1234567812345678',
    'date':b'\x8c\x81\x99n#_$Z\xe0x\x82\x19\x02\xd3W\xdc',
    'cvc':b'\xf68|$\xf5g/u\xbf\xde\xa7\x05mN\x85\xd9',
    'pin':b'\x8a\xa6[\\M\xb3"\x04\xe9\xdbVY\xd1\xe2?\xde'
    }]

pin_pad = types.InlineKeyboardMarkup()
pin_btn = []
for i in range(10):
    pin_btn.append(types.InlineKeyboardButton(text=str(i), callback_data='pin_'+str(i)))
res_btn = types.InlineKeyboardButton(text='Сброс', callback_data='pin_res')
acc_btn = types.InlineKeyboardButton(text='ОК', callback_data='pin_acc')
can_btn = types.InlineKeyboardButton(text='Отмена', callback_data='pin_can')
pin_pad.add(pin_btn[1], pin_btn[2], pin_btn[3])
pin_pad.add(pin_btn[4], pin_btn[5], pin_btn[6])
pin_pad.add(pin_btn[7], pin_btn[8], pin_btn[9])
pin_pad.add(res_btn, pin_btn[0], acc_btn)
pin_pad.add(can_btn)

cancpad = types.InlineKeyboardMarkup()
cancbut = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
cancpad.add(cancbut)

markupMain = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
markupMain.row('**Мои карты**')
markupMain.row('**Добавить карту**')
markupMain.row('**Удалить карту**')

MUP = {'main':markupMain}
