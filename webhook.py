from config import TOKEN, directory, port, host


WEBHOOK_HOST = host  # ip/host where the bot is running
WEBHOOK_PORT = port  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = directory + 'webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = directory + 'webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(TOKEN)
