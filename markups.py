from telebot import types
from static_data import MESSAGES

pin_pad = types.InlineKeyboardMarkup(row_width=3)
pin_btn = [types.InlineKeyboardButton(text=str(i), callback_data='pin_' + str(i)) for i in range(10)]
res_btn = types.InlineKeyboardButton(text='Сброс', callback_data='pin_res')
acc_btn = types.InlineKeyboardButton(text='ОК', callback_data='pin_acc')
can_btn = types.InlineKeyboardButton(text='Отмена', callback_data='pin_can')
pin_pad.add(pin_btn[1], pin_btn[2], pin_btn[3])
pin_pad.add(pin_btn[4], pin_btn[5], pin_btn[6])
pin_pad.add(pin_btn[7], pin_btn[8], pin_btn[9])
pin_pad.add(res_btn, pin_btn[0], acc_btn)
pin_pad.add(can_btn)

canc_pad = types.InlineKeyboardMarkup()
canc_but = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
canc_pad.add(canc_but)

markupMain = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupMain.row(MESSAGES['from_user']['my_cards'].forUser)
markupMain.row(MESSAGES['from_user']['add_card'].forUser)
markupMain.row(MESSAGES['from_user']['delete_card'].forUser)

inlineMarkupDelete = types.InlineKeyboardMarkup()
delete_yes_btn = types.InlineKeyboardButton(text='Удалить', callback_data='deletecard_yes')
delete_no_btn = types.InlineKeyboardButton(text='Отмена', callback_data='deletecard_no')
inlineMarkupDelete.add(delete_yes_btn, delete_no_btn)

MUP = {'main': markupMain, 'main_delete': inlineMarkupDelete}  # Markups for steps
