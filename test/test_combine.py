import unittest

import mock
import sys

from assertpy import assert_that


class Options(object):
    pass

class CombineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules['subprocess'] = mock.Mock()

    def test_combine(self):
        from scan_pdf import Combiner
        options = Options()
        options.output_file_name = ['output.pdf']

        combiner = Combiner(options)

        result = combiner.combine(['foo', 'bar'])

        import subprocess
        subprocess.call.assert_called_with(['pdftk', 'foo', 'bar', 'output', 'output.pdf', 'compress'])
        assert_that(result).is_equal_to(subprocess.call.return_value)
