import unittest

import mock
import sys

from assertpy import assert_that


class Options(object):
    pass


class ConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules['subprocess'] = mock.Mock()

    def test_convert(self):
        from scan_pdf import Converter
        options = Options()
        options.color_mode = 'bw'
        options.resolution = 300

        converter = Converter(options)

        result = converter.convert('base', '.suffix')

        import subprocess
        subprocess.call.assert_called_with(['convert', '-depth', '1', '-density', '300', '-compress', 'zip', 'base.suffix', 'base.pdf'])
        assert_that(result).is_equal_to(subprocess.call.return_value)
