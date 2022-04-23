import hashlib


def spw(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()