from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


def pad(m):
    return m + chr(16 - len(m) % 16) * (16 - len(m) % 16)


def un_pad(ct):
    return ct[:-ord(ct[-1])]


def aes_encrypt(key: str, word: str):
    key = b2a_hex(key.encode('utf-8'))
    word = b2a_hex(word.encode('utf-8')).decode()
    cipher = AES.new(key, AES.MODE_ECB)
    cipher_text = cipher.encrypt(pad(word).encode())
    return cipher_text


def aes_decrypt(key: str, word: str):
    pass

if __name__ == '__main__':
    aes_encrypt('VWTcDPMml39qpTY8VmTofQ==', '13110790527')
    # VWTcDPMml39qpTY8VmTofQ==
