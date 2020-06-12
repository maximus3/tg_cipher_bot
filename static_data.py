DATA_BACKUP_TIME = 60

TEST_DATA = [{
    'name': 'TEST 1234',
    'num': '1234567812345678',
    'date': b'\x8c\x81\x99n#_$Z\xe0x\x82\x19\x02\xd3W\xdc',
    'cvc': b'\xf68|$\xf5g/u\xbf\xde\xa7\x05mN\x85\xd9',
    'pin': b'\x8a\xa6[\\M\xb3"\x04\xe9\xdbVY\xd1\xe2?\xde'
}]

START_TEXT = """
Привет, данный бот поможет тебе хранить данные твоих банковских карт абсолютно безопасно!
Для примера мы оставили тут карту "тест 1234" с защитным кодом 1234, попробуй посмотреть ее данные.
Пожалуйста, не забывайте защитный код, потому что он не хранится в системе и восстановить его будет невозможно!
Шифрование реализованно алгоритмом AES-128.
Вот в таком виде хранится информация по катре "тест 1234":
""" + str(TEST_DATA[0])

ADMIN_COMMANDS = [
    {'command': '/null', 'description': 'Обнуление шага'},
    {'command': '/getdata', 'description': 'Получение своих данных'},
    {'command': '/getbackup', 'description': 'Бэкап файла'}
]

MESSAGES = {
    'main_addcard_name': {
        'nameExists': {
            'forUser': 'Карта с таким именем  уже существует.\nПожалуйста, введите другое имя',
            'forLog': 'Name already exists'
        },
        'length': {
            'forUser': 'Слишком длинное название (не более 32 символов)\nПожалуйста, введите другое имя',
            'forLog': 'Name is too long'
        },
        'format': {
            'forUser': 'Используйте русские, английские буквы и цифры\nПожалуйста, введите другое имя',
            'forLog': 'Wrong format of name'
        },
        'ok': {
            'forUser': '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nПридумайте защитный код (до 16 символов)\n----',
            'forLog': 'Name format is OK'
        }
    },
    'main_addcard_num': {
        'digits': {
            'forUser': 'Пожалуйста, используйте только цифры\nПожалуйста, введите номер карты заново',
            'forLog': 'Not digits'
        },
        'length': {
            'forUser': 'Длина номера должна быть 16 символов\nПожалуйста, введите номер карты заново',
            'forLog': 'Not enough symbols'
        },
        'num': {
            'forUser': 'Номер неверен.\nПожалуйста, введите номер карты заново',
            'forLog': 'Not correct num'
        },
        'ok': {
            'forUser': '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите дату окончания срока действия карты\n--/----',
            'forLog': 'Num format is OK'
        }
    },
    'main_watchcard': {
        'decode': {
            'forUser': 'Произошла ошибка при декодировании.\nВозможно, защитный код введен неправильно. Попробуйте '
                       'еще раз',
            'forLog': 'Decode error'
        },
        'digit': {
            'forUser': 'Произошла ошибка.\nВозможно, защитный код введен неправильно. Попробуйте еще раз',
            'forLog': 'Not digit in result error'
        },
        'ok': {
            'forUser': None,
            'forLog': 'Decode is OK'
        }
    },
    'main_addcard_code': {
        'length': {
            'forUser': 'Защитный код должен содержать от 4 до 16 символов. Попробуйте еще раз.\n',
            'forLog': 'Length error'
        },
        'ok': {
            'forUser': 'Введите номер карты',
            'forLog': 'Code is OK'
        }
    },
    'main_addcard_date': {
        'length': {
            'forUser': 'Пожалуйста, введите 4 или 6 цифр даты (ммгггг или ммгг)\n',
            'forLog': 'Length error'
        },
        'incorrect': {
            'forUser': 'Введена некорректная дата\n',
            'forLog': 'Format error'
        },
        'encode': {
            'forUser': 'Произошла ошибка при кодировании',
            'forLog': 'Encode error'
        },
        'ok': {
            'forUser': '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите CVC код\n---',
            'forLog': 'Date is OK'
        }
    },
    'main_addcard_cvc': {
        'length': {
            'forUser': 'CVC код должен содержать от 3 до 4 символов. Попробуйте еще раз\n',
            'forLog': 'Length error'
        },
        'encode': {
            'forUser': 'Произошла ошибка при кодировании',
            'forLog': 'Encode error'
        },
        'ok': {
            'forUser': '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите PIN код\n----',
            'forLog': 'CVC is OK'
        }
    },
    'main_addcard_pin': {
        'length': {
            'forUser': 'PIN код должен состоять из 4 символов. Попробуйте еще раз\n',
            'forLog': 'Length error'
        },
        'encode': {
            'forUser': 'Произошла ошибка при кодировании',
            'forLog': 'Encode error'
        },
        'ok': {
            'forUser': '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВведите PIN код\n----',
            'forLog': 'PIN is OK'
        }
    },
    '_delete': {
        'confirmDelete': {
            'forUser': lambda name: 'Выбрана карта *' + name + '*\nВы уверены, что хотите удалить ее из базы? Отмена '
                                                               'невозможна! '
        }
    },
    '_watchcard': {
        'enterCode': {
            'forUser': lambda name: '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nВыбрана карта *' + name + '*\nВведите защитный '
                                                                                               'код:\n---- '
        }
    }
}
