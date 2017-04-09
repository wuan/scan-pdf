import unittest

import mock
import sys

from assertpy import assert_that


class Options(object):
    pass


class CombineTest(unittest.TestCase):
    @classmethod
    def setUp(self):
        super(CombineTest, self).setUpClass()

        sys.modules['subprocess'] = mock.Mock()

    def test_foo(self):
        from scan_pdf import Combiner
        import subprocess
        options = Options()
        options.output_file_name = ['output.pdf']
        combiner = Combiner(options)

        result = combiner.combine(['foo', 'bar'])

        subprocess.call.assert_called_with(['pdftk', 'foo', 'bar', 'output', 'output.pdf', 'compress'])
        assert_that(result).is_equal_to(subprocess.call.return_value)
