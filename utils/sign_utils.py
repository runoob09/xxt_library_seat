"""
加密相关的工具类
"""
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad


def encryptByAES(s):
    """
    加密函数
    :param s: 传入的字符串
    :return: 加密后的结果
    """
    key = "u2oh6Vu^HWe4_AES"
    iv = key.encode('utf-8')
    aeskey = key.encode('utf-8')
    secretData = s.encode('utf-8')
    cipher = AES.new(aeskey, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(secretData, AES.block_size))
    ciphertext = base64.b64encode(encrypted).decode('utf-8')
    return ciphertext
