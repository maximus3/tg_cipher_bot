# Description

Данный бот поможет вам не запоминать номера карт, CVC и PIN коды. Все будет храниться в зашифрованном виде в телеграм боте.

Проверить работу можно по ссылке:
https://teleg.run/cipher_m3bot

# INSTRUCTIONS
Taked from https://mastergroosha.github.io/telegram-tutorial/docs/pyTelegramBotAPI/

## Install to your server

Rename `TEMPLATE_config.py` to `config.py` and fill in all the fields.

Then see `Webhook`, `VENV` and `AUTOSTART` to configure and start bot.

## WEBHOOK

Для начала, установим пакет openssl (для Linux):

`sudo apt-get install openssl`

Затем сгенерируем приватный ключ:

`openssl genrsa -out webhook_pkey.pem 2048`

Теперь, внимание, генерируем самоподписанный сертификат вот этой вот длинной командой:

`openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem`

Нам предложат ввести некоторую информацию о себе: двухбуквенный код страны, имя организации и т.д. Если не хотите ничего вводить, ставьте точку. НО! ВАЖНО! Когда дойдете до предложения ввести Common Name, следует написать IP адрес сервера, на котором будет запущен бот.

В результате получим файлы webhook_cert.pem и webhook_pkey.pem, положим их в какой-нибудь пустой каталог, в котором потом будем создавать бота.

Обратите внимание, что Telegram поддерживает всего 4 различных порта при работе с самоподписанными сертификатами. Теоретически, это означает, что на одной машине может быть запущено не больше 4 ботов на вебхуках.

## VENV

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`deactivate`

## AUTOSTART

Чтобы сделать жизнь ещё приятнее, давайте настроим автозагрузку бота, чтобы при возникновении ошибок или при перезапуске сервера он вновь запускался, избавляя нас от необходимости постоянно проверять всё вручную. Для этого мы воспользуемся подсистемой инициализации systemd, которая всё больше распространена в современных Linux-дистрибутивах. Прежде, чем описать службу systemd, откройте главный файл с ботом, в котором прописан его запуск и добавьте в качестве первой строки следующий код: `#!venv/bin/python`

Сохраните файл, закройте его и выполните команду `chmod +x имяфайласботом.py`, чтобы сделать его исполняемым. Теперь создайте файл `mybot.service`, и скопируйте туда следующий текст:

```
[Unit]
Description=MY BOT
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/user/mybot
ExecStart=/home/user/mybot/bot.py
KillMode=process
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Отредактируйте поля `Description`, `WorkingDirectory` и `ExecStart`, сохраните и закройте файл. Далее скопируйте его в каталог `/etc/systemd/system/`, введя свой пароль при необходимости (если сидите не из-под рута, что правильно, то ваш юзер должен иметь возможность выполнять команды от имени sudo). Затем выполните следующие команды для включения автозагрузки и запуска бота (опять-таки, требуются права суперпользователя):

```
systemctl enable mybot.service
systemctl restart mybot
```

Наконец, проверьте состояние вашего бота командой `systemctl status mybot`. Его статус должен быть `Active (running)` зелёного цвета (если поддерживается разноцветный режим).

## Problems

### /usr/bin/python^M: bad interpreter: No such file or directory
The issue is not EOF but EOL. The shell sees a ^M as well as the end of line and thus tries to find `/usr/bin/python^M`.

The usual way of getting into this state is to edit the python file with a MSDOS/Windows editor and then run on Unix. The simplest fix is to run dos2unix on the file or edit the file in an editor that explicitly allows saving with Unix end of lines.

vi/vim: `:set fileformat=unix` and then save the file `:wq`
