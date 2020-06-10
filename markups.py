from telebot import types

pin_pad = types.InlineKeyboardMarkup()
pin_btn = [types.InlineKeyboardButton(text=str(i), callback_data='pin_' + str(i)) for i in range(10)]
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

markupMain = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupMain.row('**Мои карты**')
markupMain.row('**Добавить карту**')
markupMain.row('**Удалить карту**')

MUP = {'main': markupMain}
