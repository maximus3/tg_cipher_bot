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
            if (
                (not ('а' <= i <= 'я'))
                and i != ' '
                and (not ('0' <= i <= '9'))
                and i != 'ё'
            ):
                return True
        return False
    elif tp == 'eng1':
        for i in text:
            if (
                (not ('A' <= i <= 'Z'))
                and i != ' '
                and (not ('0' <= i <= '9'))
                and (not ('a' <= i <= 'z'))
            ):
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
            if (
                (not ('A' <= i <= 'Z'))
                and (not ('0' <= i <= '9'))
                and (not ('a' <= i <= 'z'))
            ):
                return True
        return False
    elif tp == 'ruseng1':
        for i in text:
            if (
                (not ('A' <= i <= 'Z'))
                and i != 'ё'
                and i != ' '
                and (not ('0' <= i <= '9'))
                and (not ('a' <= i <= 'z'))
                and (not ('а' <= i <= 'я'))
                and (not ('А' <= i <= 'Я'))
            ):
                return True
        return False
