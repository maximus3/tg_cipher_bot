"""Tham module provides encrypting/decrypting according AES(128) standart. 
Based on Rijndael algorithm, AES uses 4 transformation for encrypting: SubSytes(), ShiftRows(),
MixColumns() and AddRoundKey(). For decrypting it uses inverse functions of that fout.
Detales you can read here:
http://csrc.nist.gov/publications/fips/fips197/fips-197.pdf
or here:
http://en.wikipedia.org/wiki/Advanced_Encryption_Standard
or here:
http://www.cs.bc.edu/~straubin/cs381-05/blockciphers/rijndael_ingles2004.swf
or somewhere else.

Comments rather won't help if don't read documentation of the algorithm.

"""

nb = 4  # number of column of State (for AES = 4)
nr = 10  # number of rounds ib cipher cycle (if nb = 4 nr = 10)
nk = 4  # the key length (in 32-bit words)

# This dict will be used in SubBytes().
hex_symbols_to_int = {'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}

sbox = [
    0x63,
    0x7C,
    0x77,
    0x7B,
    0xF2,
    0x6B,
    0x6F,
    0xC5,
    0x30,
    0x01,
    0x67,
    0x2B,
    0xFE,
    0xD7,
    0xAB,
    0x76,
    0xCA,
    0x82,
    0xC9,
    0x7D,
    0xFA,
    0x59,
    0x47,
    0xF0,
    0xAD,
    0xD4,
    0xA2,
    0xAF,
    0x9C,
    0xA4,
    0x72,
    0xC0,
    0xB7,
    0xFD,
    0x93,
    0x26,
    0x36,
    0x3F,
    0xF7,
    0xCC,
    0x34,
    0xA5,
    0xE5,
    0xF1,
    0x71,
    0xD8,
    0x31,
    0x15,
    0x04,
    0xC7,
    0x23,
    0xC3,
    0x18,
    0x96,
    0x05,
    0x9A,
    0x07,
    0x12,
    0x80,
    0xE2,
    0xEB,
    0x27,
    0xB2,
    0x75,
    0x09,
    0x83,
    0x2C,
    0x1A,
    0x1B,
    0x6E,
    0x5A,
    0xA0,
    0x52,
    0x3B,
    0xD6,
    0xB3,
    0x29,
    0xE3,
    0x2F,
    0x84,
    0x53,
    0xD1,
    0x00,
    0xED,
    0x20,
    0xFC,
    0xB1,
    0x5B,
    0x6A,
    0xCB,
    0xBE,
    0x39,
    0x4A,
    0x4C,
    0x58,
    0xCF,
    0xD0,
    0xEF,
    0xAA,
    0xFB,
    0x43,
    0x4D,
    0x33,
    0x85,
    0x45,
    0xF9,
    0x02,
    0x7F,
    0x50,
    0x3C,
    0x9F,
    0xA8,
    0x51,
    0xA3,
    0x40,
    0x8F,
    0x92,
    0x9D,
    0x38,
    0xF5,
    0xBC,
    0xB6,
    0xDA,
    0x21,
    0x10,
    0xFF,
    0xF3,
    0xD2,
    0xCD,
    0x0C,
    0x13,
    0xEC,
    0x5F,
    0x97,
    0x44,
    0x17,
    0xC4,
    0xA7,
    0x7E,
    0x3D,
    0x64,
    0x5D,
    0x19,
    0x73,
    0x60,
    0x81,
    0x4F,
    0xDC,
    0x22,
    0x2A,
    0x90,
    0x88,
    0x46,
    0xEE,
    0xB8,
    0x14,
    0xDE,
    0x5E,
    0x0B,
    0xDB,
    0xE0,
    0x32,
    0x3A,
    0x0A,
    0x49,
    0x06,
    0x24,
    0x5C,
    0xC2,
    0xD3,
    0xAC,
    0x62,
    0x91,
    0x95,
    0xE4,
    0x79,
    0xE7,
    0xC8,
    0x37,
    0x6D,
    0x8D,
    0xD5,
    0x4E,
    0xA9,
    0x6C,
    0x56,
    0xF4,
    0xEA,
    0x65,
    0x7A,
    0xAE,
    0x08,
    0xBA,
    0x78,
    0x25,
    0x2E,
    0x1C,
    0xA6,
    0xB4,
    0xC6,
    0xE8,
    0xDD,
    0x74,
    0x1F,
    0x4B,
    0xBD,
    0x8B,
    0x8A,
    0x70,
    0x3E,
    0xB5,
    0x66,
    0x48,
    0x03,
    0xF6,
    0x0E,
    0x61,
    0x35,
    0x57,
    0xB9,
    0x86,
    0xC1,
    0x1D,
    0x9E,
    0xE1,
    0xF8,
    0x98,
    0x11,
    0x69,
    0xD9,
    0x8E,
    0x94,
    0x9B,
    0x1E,
    0x87,
    0xE9,
    0xCE,
    0x55,
    0x28,
    0xDF,
    0x8C,
    0xA1,
    0x89,
    0x0D,
    0xBF,
    0xE6,
    0x42,
    0x68,
    0x41,
    0x99,
    0x2D,
    0x0F,
    0xB0,
    0x54,
    0xBB,
    0x16,
]

inv_sbox = [
    0x52,
    0x09,
    0x6A,
    0xD5,
    0x30,
    0x36,
    0xA5,
    0x38,
    0xBF,
    0x40,
    0xA3,
    0x9E,
    0x81,
    0xF3,
    0xD7,
    0xFB,
    0x7C,
    0xE3,
    0x39,
    0x82,
    0x9B,
    0x2F,
    0xFF,
    0x87,
    0x34,
    0x8E,
    0x43,
    0x44,
    0xC4,
    0xDE,
    0xE9,
    0xCB,
    0x54,
    0x7B,
    0x94,
    0x32,
    0xA6,
    0xC2,
    0x23,
    0x3D,
    0xEE,
    0x4C,
    0x95,
    0x0B,
    0x42,
    0xFA,
    0xC3,
    0x4E,
    0x08,
    0x2E,
    0xA1,
    0x66,
    0x28,
    0xD9,
    0x24,
    0xB2,
    0x76,
    0x5B,
    0xA2,
    0x49,
    0x6D,
    0x8B,
    0xD1,
    0x25,
    0x72,
    0xF8,
    0xF6,
    0x64,
    0x86,
    0x68,
    0x98,
    0x16,
    0xD4,
    0xA4,
    0x5C,
    0xCC,
    0x5D,
    0x65,
    0xB6,
    0x92,
    0x6C,
    0x70,
    0x48,
    0x50,
    0xFD,
    0xED,
    0xB9,
    0xDA,
    0x5E,
    0x15,
    0x46,
    0x57,
    0xA7,
    0x8D,
    0x9D,
    0x84,
    0x90,
    0xD8,
    0xAB,
    0x00,
    0x8C,
    0xBC,
    0xD3,
    0x0A,
    0xF7,
    0xE4,
    0x58,
    0x05,
    0xB8,
    0xB3,
    0x45,
    0x06,
    0xD0,
    0x2C,
    0x1E,
    0x8F,
    0xCA,
    0x3F,
    0x0F,
    0x02,
    0xC1,
    0xAF,
    0xBD,
    0x03,
    0x01,
    0x13,
    0x8A,
    0x6B,
    0x3A,
    0x91,
    0x11,
    0x41,
    0x4F,
    0x67,
    0xDC,
    0xEA,
    0x97,
    0xF2,
    0xCF,
    0xCE,
    0xF0,
    0xB4,
    0xE6,
    0x73,
    0x96,
    0xAC,
    0x74,
    0x22,
    0xE7,
    0xAD,
    0x35,
    0x85,
    0xE2,
    0xF9,
    0x37,
    0xE8,
    0x1C,
    0x75,
    0xDF,
    0x6E,
    0x47,
    0xF1,
    0x1A,
    0x71,
    0x1D,
    0x29,
    0xC5,
    0x89,
    0x6F,
    0xB7,
    0x62,
    0x0E,
    0xAA,
    0x18,
    0xBE,
    0x1B,
    0xFC,
    0x56,
    0x3E,
    0x4B,
    0xC6,
    0xD2,
    0x79,
    0x20,
    0x9A,
    0xDB,
    0xC0,
    0xFE,
    0x78,
    0xCD,
    0x5A,
    0xF4,
    0x1F,
    0xDD,
    0xA8,
    0x33,
    0x88,
    0x07,
    0xC7,
    0x31,
    0xB1,
    0x12,
    0x10,
    0x59,
    0x27,
    0x80,
    0xEC,
    0x5F,
    0x60,
    0x51,
    0x7F,
    0xA9,
    0x19,
    0xB5,
    0x4A,
    0x0D,
    0x2D,
    0xE5,
    0x7A,
    0x9F,
    0x93,
    0xC9,
    0x9C,
    0xEF,
    0xA0,
    0xE0,
    0x3B,
    0x4D,
    0xAE,
    0x2A,
    0xF5,
    0xB0,
    0xC8,
    0xEB,
    0xBB,
    0x3C,
    0x83,
    0x53,
    0x99,
    0x61,
    0x17,
    0x2B,
    0x04,
    0x7E,
    0xBA,
    0x77,
    0xD6,
    0x26,
    0xE1,
    0x69,
    0x14,
    0x63,
    0x55,
    0x21,
    0x0C,
    0x7D,
]

rcon = [
    [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36],
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
]


def encrypt(input_bytes, key):
    """Function encrypts the input_bytes according to AES(128) algorithm using the key

    Args:
       input_bytes -- list of int less than 255, ie list of bytes. Length of input_bytes is constantly 16
       key -- a strig of plain text. Do not forget it! The same string is used in decryption

    Returns:
        List of int

    """

    # let's prepare our enter data: State array and KeySchedule
    state = [[] for j in range(4)]
    for r in range(4):
        for c in range(nb):
            state[r].append(input_bytes[r + 4 * c])

    key_schedule = key_expansion(key)

    state = add_round_key(state, key_schedule)

    for rnd in range(1, nr):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, key_schedule, rnd)

    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, key_schedule, rnd + 1)

    output = [None for i in range(4 * nb)]
    for r in range(4):
        for c in range(nb):
            output[r + 4 * c] = state[r][c]

    return output


def decrypt(cipher, key):
    """Function decrypts the cipher according to AES(128) algorithm using the key

    Args:
       cipher -- list of int less than 255, ie list of bytes
       key -- a strig of plain text. Do not forget it! The same string is used in decryption

    Returns:
        List of int

    """

    # let's prepare our algorithm enter data: State array and KeySchedule
    state = [[] for i in range(nb)]
    for r in range(4):
        for c in range(nb):
            state[r].append(cipher[r + 4 * c])

    key_schedule = key_expansion(key)

    state = add_round_key(state, key_schedule, nr)

    rnd = nr - 1
    while rnd >= 1:
        state = shift_rows(state, inv=True)
        state = sub_bytes(state, inv=True)
        state = add_round_key(state, key_schedule, rnd)
        state = mix_columns(state, inv=True)

        rnd -= 1

    state = shift_rows(state, inv=True)
    state = sub_bytes(state, inv=True)
    state = add_round_key(state, key_schedule, rnd)

    output = [None for i in range(4 * nb)]
    for r in range(4):
        for c in range(nb):
            output[r + 4 * c] = state[r][c]

    return output


def sub_bytes(state, inv=False):
    """That transformation replace every element from State on element from Sbox
    according the algorithm: in hexadecimal notation an element from State
    consist of two values: 0x<val1><val2>. We take elem from crossing
    val1-row and val2-column in Sbox and put it instead of the element in State.
    If decryption-transformation is on (inv == True) it uses InvSbox instead Sbox.

    Args:
        inv -- If value == False means function is encryption-transformation.
               True - decryption-transformation

    """

    if inv == False:  # encrypt
        box = sbox
    else:  # decrypt
        box = inv_sbox

    for i in range(len(state)):
        for j in range(len(state[i])):
            row = state[i][j] // 0x10
            col = state[i][j] % 0x10

            # Our Sbox is a flat array, not a bable. So, we use this trich to find elem:
            # And DO NOT change list sbox! if you want it to work
            box_elem = box[16 * row + col]
            state[i][j] = box_elem

    return state


def shift_rows(state, inv=False):
    """That transformation shifts rows of State: the second rotate over 1 bytes,
    the third rotate over 2 bytes, the fourtg rotate over 3 bytes. The transformation doesn't
    touch the first row. When encrypting transformation uses left shift, in decription - right shift

    Args:
        inv: If value == False means function is encryption mode. True - decryption mode

    """

    count = 1

    if inv == False:  # encrypting
        for i in range(1, nb):
            state[i] = left_shift(state[i], count)
            count += 1
    else:  # decryptionting
        for i in range(1, nb):
            state[i] = right_shift(state[i], count)
            count += 1

    return state


def mix_columns(state, inv=False):
    """When encrypting transformation multiplyes every column of State with
    a fixed polinomial a(x) = {03}x**3 + {01}x**2 + {01}x + {02} in Galua field.
    When decrypting multiplies with a'(x) = {0b}x**3 + {0d}x**2 + {09}x + {0e}
    Detailed information in AES standart.

    Args:
        inv: If value == False means function is encryption mode. True - decryption mode

    """

    for i in range(nb):

        if inv == False:  # encryption
            s0 = (
                mul_by_02(state[0][i])
                ^ mul_by_03(state[1][i])
                ^ state[2][i]
                ^ state[3][i]
            )
            s1 = (
                state[0][i]
                ^ mul_by_02(state[1][i])
                ^ mul_by_03(state[2][i])
                ^ state[3][i]
            )
            s2 = (
                state[0][i]
                ^ state[1][i]
                ^ mul_by_02(state[2][i])
                ^ mul_by_03(state[3][i])
            )
            s3 = (
                mul_by_03(state[0][i])
                ^ state[1][i]
                ^ state[2][i]
                ^ mul_by_02(state[3][i])
            )
        else:  # decryption
            s0 = (
                mul_by_0e(state[0][i])
                ^ mul_by_0b(state[1][i])
                ^ mul_by_0d(state[2][i])
                ^ mul_by_09(state[3][i])
            )
            s1 = (
                mul_by_09(state[0][i])
                ^ mul_by_0e(state[1][i])
                ^ mul_by_0b(state[2][i])
                ^ mul_by_0d(state[3][i])
            )
            s2 = (
                mul_by_0d(state[0][i])
                ^ mul_by_09(state[1][i])
                ^ mul_by_0e(state[2][i])
                ^ mul_by_0b(state[3][i])
            )
            s3 = (
                mul_by_0b(state[0][i])
                ^ mul_by_0d(state[1][i])
                ^ mul_by_09(state[2][i])
                ^ mul_by_0e(state[3][i])
            )

        state[0][i] = s0
        state[1][i] = s1
        state[2][i] = s2
        state[3][i] = s3

    return state


def key_expansion(key):
    """It makes list of RoundKeys for function AddRoundKey. All details
    about algorithm is is in AES standart

    """

    key_symbols = [ord(symbol) for symbol in key]

    # ChipherKey shoul contain 16 symbols to fill 4*4 table. If it's less
    # complement the key with "0x01"
    if len(key_symbols) < 4 * nk:
        for i in range(4 * nk - len(key_symbols)):
            key_symbols.append(0x01)

    # make ChipherKey(which is base of KeySchedule)
    key_schedule = [[] for i in range(4)]
    for r in range(4):
        for c in range(nk):
            key_schedule[r].append(key_symbols[r + 4 * c])

    # Comtinue to fill KeySchedule
    for col in range(nk, nb * (nr + 1)):  # col - column number
        if col % nk == 0:
            # take shifted (col - 1)th column...
            tmp = [key_schedule[row][col - 1] for row in range(1, 4)]
            tmp.append(key_schedule[0][col - 1])

            # change its elements using Sbox-table like in SubBytes...
            for j in range(len(tmp)):
                sbox_row = tmp[j] // 0x10
                sbox_col = tmp[j] % 0x10
                sbox_elem = sbox[16 * sbox_row + sbox_col]
                tmp[j] = sbox_elem

            # and finally make XOR of 3 columns
            for row in range(4):
                s = (
                    (key_schedule[row][col - 4])
                    ^ (tmp[row])
                    ^ (rcon[row][int(col / nk - 1)])
                )
                key_schedule[row].append(s)

        else:
            # just make XOR of 2 columns
            for row in range(4):
                s = key_schedule[row][col - 4] ^ key_schedule[row][col - 1]
                key_schedule[row].append(s)

    return key_schedule


def add_round_key(state, key_schedule, round=0):
    """That transformation combines State and KeySchedule together. Xor
    of State and RoundSchedule(part of KeySchedule).

    """

    for col in range(nk):
        # nb*round is a shift which indicates start of a part of the KeySchedule
        s0 = state[0][col] ^ key_schedule[0][nb * round + col]
        s1 = state[1][col] ^ key_schedule[1][nb * round + col]
        s2 = state[2][col] ^ key_schedule[2][nb * round + col]
        s3 = state[3][col] ^ key_schedule[3][nb * round + col]

        state[0][col] = s0
        state[1][col] = s1
        state[2][col] = s2
        state[3][col] = s3

    return state


# Small helpful functions block


def left_shift(array, count):
    """Rotate the array over count times"""

    res = array[:]
    for i in range(count):
        temp = res[1:]
        temp.append(res[0])
        res[:] = temp[:]

    return res


def right_shift(array, count):
    """Rotate the array over count times"""

    res = array[:]
    for i in range(count):
        tmp = res[:-1]
        tmp.insert(0, res[-1])
        res[:] = tmp[:]

    return res


def mul_by_02(num):
    """The function multiplies by 2 in Galua space"""

    if num < 0x80:
        res = num << 1
    else:
        res = (num << 1) ^ 0x1B

    return res % 0x100


def mul_by_03(num):
    """The function multiplies by 3 in Galua space
    example: 0x03*num = (0x02 + 0x01)num = num*0x02 + num
    Addition in Galua field is oparetion XOR

    """
    return mul_by_02(num) ^ num


def mul_by_09(num):
    # return mul_by_03(num)^mul_by_03(num)^mul_by_03(num) - works wrong, I don't know why
    return mul_by_02(mul_by_02(mul_by_02(num))) ^ num


def mul_by_0b(num):
    # return mul_by_09(num)^mul_by_02(num)
    return mul_by_02(mul_by_02(mul_by_02(num))) ^ mul_by_02(num) ^ num


def mul_by_0d(num):
    # return mul_by_0b(num)^mul_by_02(num)
    return (
        mul_by_02(mul_by_02(mul_by_02(num))) ^ mul_by_02(mul_by_02(num)) ^ num
    )


def mul_by_0e(num):
    # return mul_by_0d(num)^num
    return (
        mul_by_02(mul_by_02(mul_by_02(num)))
        ^ mul_by_02(mul_by_02(num))
        ^ mul_by_02(num)
    )


# End of small helpful functions block
