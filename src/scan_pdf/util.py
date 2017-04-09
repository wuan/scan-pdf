import tempfile
import shutil


class TempDir(object):
    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='scanpdf_')
        return self.temp_dir

    # noinspection PyUnusedLocal
    def __exit__(self, type_value, value, traceback):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
