from . import aes128


def check_key(key):
    if len(key) > 16:
        return False

    for symbol in key:
        if ord(symbol) > 0xFF:
            # That key won\'t work. Try another using only latin alphabet and numbers
            return False

    return True


def encrypt(key, data='', filename=None):

    if not check_key(key):
        return None

    if filename:
        # Input data
        with open(filename, 'rb') as f:
            data = f.read()
    else:
        try:
            data = data.encode('utf-8')
        except AttributeError:
            pass

    crypted_data = []
    temp = []
    for byte in data:
        temp.append(byte)
        if len(temp) == 16:
            crypted_part = aes128.encrypt(temp, key)
            crypted_data.extend(crypted_part)
            del temp[:]
    else:
        # padding v1
        # writing in the end

        # crypted_data.extend(temp)

        # padding v2
        # writing ...00001 in the end
        if 0 < len(temp) < 16:
            empty_spaces = 16 - len(temp)
            for i in range(empty_spaces - 1):
                temp.append(0)
            temp.append(1)
            crypted_part = aes128.encrypt(temp, key)
            crypted_data.extend(crypted_part)

    if filename:
        out_path = os.path.join(
            os.path.dirname(filename), 'crypted_' + os.path.basename(filename)
        )

        with open(out_path, 'xb') as ff:
            ff.write(bytes(crypted_data))
        return out_path
    else:
        return bytes(crypted_data)


def decrypt(key, data='', filename=None):

    if not check_key(key):
        return None

    if filename:
        # Input data
        with open(filename, 'rb') as f:
            data = f.read()
    else:
        try:
            data = data.encode('utf-8')
        except AttributeError:
            pass

    decrypted_data = []
    temp = []
    for byte in data:
        temp.append(byte)
        if len(temp) == 16:
            decrypted_part = aes128.decrypt(temp, key)
            decrypted_data.extend(decrypted_part)
            del temp[:]
    else:
        # padding v1
        # decrypted_data.extend(temp)

        # padding v2
        if 0 < len(temp) < 16:
            empty_spaces = 16 - len(temp)
            for i in range(empty_spaces - 1):
                temp.append(0)
            temp.append(1)
            decrypted_part = aes128.encrypt(temp, key)
            decrypted_data.extend(crypted_part)

        # Delete ...000001 path
        if decrypted_data[-1] == 1:
            decrypted_data.pop()
            while len(decrypted_data) > 0 and decrypted_data[-1] == 0:
                decrypted_data.pop()

    if filename:
        out_path = os.path.join(
            os.path.dirname(input_path),
            'decrypted_' + os.path.basename(input_path),
        )

        # Ounput data
        with open(out_path, 'xb') as ff:
            ff.write(bytes(decrypted_data))
        return out_path
    else:
        return bytes(decrypted_data).decode('utf-8')
