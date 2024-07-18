import os
from argparse import Namespace


class Options(Namespace):
    pass


def touch(file_name: str):
    with open(file_name, "a"):
        os.utime(file_name, None)
