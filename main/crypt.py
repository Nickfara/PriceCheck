from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode
import os
from constants import KEY, SECRET_FORMAT_NUMBER_T2

def crypting(text, password, way:str = 'encrypt'):
    """

    :param text: Данные для шифрования.
    :param password: Ключ шифрования.
    :param way: Способ работы: encrypt - шифрование, decrypt - расшифровка.
    :return:
    """
    # Добавляем "соль".
    salt = os.urandom(16)

    # Создаем ключ, используя PBKDF2HMAC.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    # Генерируем urlsafe base64 ключ.
    key = urlsafe_b64encode(kdf.derive(password))

    # Создаем шифровальщик с использованием Fernet.
    cipher_suite = Fernet(key)

    # Шифруем сообщение.
    message = text

    if way == 'encrypt':
        msg = cipher_suite.encrypt(message)
        msg = cipher_suite.decrypt(msg)
    elif way == 'decrypt':
        msg = cipher_suite.decrypt(message)
    else:
        raise Exception("Неверный способ!")

    return msg


testi = crypting(SECRET_FORMAT_NUMBER_T2, KEY)
print(testi)

testis = crypting(testi, KEY, 'decrypt')
print(testis)

