import os


class Options(object):
    pass


def touch(file_name: str):
    with open(file_name, 'a'):
        os.utime(file_name, None)
