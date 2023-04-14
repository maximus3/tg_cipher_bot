TEST_DATA = [
    {
        'name': 'TEST 1234',
        'num': '1234567812345678',
        'date': b'\x8c\x81\x99n#_$Z\xe0x\x82\x19\x02\xd3W\xdc',
        'cvc': b'\xf68|$\xf5g/u\xbf\xde\xa7\x05mN\x85\xd9',
        'pin': b'\x8a\xa6[\\M\xb3"\x04\xe9\xdbVY\xd1\xe2?\xde',
    }
]

START_TEXT = """
Привет, данный бот поможет тебе хранить данные твоих банковских карт абсолютно безопасно!
Для примера мы оставили тут карту "тест 1234" с защитным кодом 1234, попробуй посмотреть ее данные.
Пожалуйста, не забывайте защитный код, потому что он не хранится в системе и восстановить его будет невозможно!
Шифрование реализованно алгоритмом AES-128.
Вот в таком виде хранится информация по катре "тест 1234":
""" + str(
    TEST_DATA[0]
)

ADMIN_COMMANDS = [
    {'command': '/null', 'description': 'Обнуление шага'},
    {'command': '/getdata', 'description': 'Получение своих данных'},
    {'command': '/getbackup', 'description': 'Бэкап файла'},
]


class StaticMessage:
    def __init__(self, forUser=None, forLog=None):
        self.forUser = forUser
        self.forLog = forLog

    def __str__(self):
        return self.forUser


TEMPLATES = {'date': '--/----', 'cvc': '---', 'pin': '----', 'code': '----'}

MESSAGES = {  # step - short name
    'any': {
        'old_message': StaticMessage('Данное сообщение уже устарело'),
        'start': StaticMessage(START_TEXT),
        'loading': StaticMessage('Загрузка...'),
        'no_cards': StaticMessage('У вас нет карт'),
        'cancel': StaticMessage('_Действие отменено_'),
    },
    'from_user': {
        'my_cards': StaticMessage('**Мои карты**'),
        'add_card': StaticMessage('**Добавить карту**'),
        'delete_card': StaticMessage('**Удалить карту**'),
    },
    'main': {
        'watch_card': StaticMessage('Выберите карту. Всего карт: {}'),
        'add_card': StaticMessage('Введите имя карты'),
        'delete_card': StaticMessage('Выберите карту, которую хотите удалить'),
    },
    'main_addcard_name': {
        'nameExists': StaticMessage(
            'Карта с таким именем  уже существует', 'Name already exists'
        ),
        'length': StaticMessage(
            'Слишком длинное название (не более 32 символов)',
            'Name is too long',
        ),
        'format': StaticMessage(
            'Используйте русские, английские буквы и цифры',
            'Wrong format of name',
        ),
        'ok': StaticMessage(
            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nПридумайте защитный код (до 16 символов)\n'
            + TEMPLATES['code'],
            'Name format is OK',
        ),
    },
    'main_addcard_num': {
        'digits': StaticMessage(
            'Номер карты должен состоять только из цифр', 'Not digits'
        ),
        'length': StaticMessage(
            'Номер карты должен состоять из 16 символов', 'Not enough symbols'
        ),
        'num': StaticMessage('Номер набран неправильно', 'Not correct num'),
        'ok': StaticMessage(
            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите дату окончания срока действия карты\n'
            + TEMPLATES['date'],
            'Num format is OK',
        ),
    },
    'main_addcard_code': {
        'length': StaticMessage(
            'Защитный код должен содержать от 4 до 16 символов', 'Length error'
        ),
        'ok': StaticMessage('Введите номер карты', 'Code is OK'),
    },
    'main_addcard_date': {
        'length': StaticMessage(
            'Пожалуйста, введите 4 или 6 цифр даты (ммгггг или ммгг)',
            'Length error',
        ),
        'incorrect': StaticMessage(
            'Введена некорректная дата', 'Format error'
        ),
        'encode': StaticMessage(
            'Произошла ошибка при кодировании', 'Encode error'
        ),
        'ok': StaticMessage(
            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите CVC код\n'
            + TEMPLATES['cvc'],
            'Date is OK',
        ),
    },
    'main_addcard_cvc': {
        'length': StaticMessage(
            'CVC код должен содержать от 3 до 4 символов', 'Length error'
        ),
        'encode': StaticMessage(
            'Произошла ошибка при кодировании', 'Encode error'
        ),
        'ok': StaticMessage(
            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите PIN код\n'
            + TEMPLATES['pin'],
            'CVC is OK',
        ),
    },
    'main_addcard_pin': {
        'length': StaticMessage(
            'PIN код должен содержать 4 символа', 'Length error'
        ),
        'encode': StaticMessage(
            'Произошла ошибка при кодировании', 'Encode error'
        ),
        'ok': StaticMessage('Карта *{}* успешно добавлена!', 'PIN is OK'),
    },
    'main_delete': {
        'confirm_delete': StaticMessage(
            'Выбрана карта *{}*\nВы уверены, что хотите удалить ее из базы? Отмена '
            'невозможна!'
        ),
        'yes': StaticMessage('Выбрана карта *{}*\nКарта удалена'),
        'no': StaticMessage('Выбрана карта *{}*\nУдаление отменено'),
    },
    'main_watchcard': {
        'decode': StaticMessage(
            'Произошла ошибка при декодировании.\nВозможно, защитный код введен неправильно. '
            'Попробуйте еще раз',
            'Decode error',
        ),
        'digit': StaticMessage(
            'Произошла ошибка.\nВозможно, защитный код введен неправильно. Попробуйте еще раз',
            'Not digit in result error',
        ),
        'ok': StaticMessage(
            'Защитный код принят. Данное сообщение исчезнет через 5 секунд.\n{}\n{}',
            'Decode is OK',
        ),
        'enter_code': StaticMessage(
            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВыбрана карта *{}*\nВведите защитный код:\n'
            + TEMPLATES['code']
        ),
        'basic': StaticMessage('Карта: *{}*\n' + 'Номер карты: `{}`'),
    },
}
MESSAGES['main']['start'] = MESSAGES['any']['start']
MESSAGES['main_addcard_name']['start'] = MESSAGES['main']['add_card']
MESSAGES['main_addcard_code']['start'] = MESSAGES['main_addcard_name']['ok']
MESSAGES['main_addcard_num']['start'] = MESSAGES['main_addcard_code']['ok']
MESSAGES['main_addcard_date']['start'] = MESSAGES['main_addcard_num']['ok']
MESSAGES['main_addcard_cvc']['start'] = MESSAGES['main_addcard_date']['ok']
MESSAGES['main_addcard_pin']['start'] = MESSAGES['main_addcard_cvc']['ok']
MESSAGES['main_watchcard']['start'] = MESSAGES['main_watchcard']['enter_code']
