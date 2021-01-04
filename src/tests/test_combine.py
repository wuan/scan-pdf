import pytest
from assertpy import assert_that
from mock import patch

from scan_pdf import Combiner


class Options(object):
    pass


class TestCombine:

    @pytest.fixture
    def subprocess(self):
        with patch("scan_pdf.combine.subprocess") as subprocess:
            yield subprocess

    def test_combine(self, subprocess):
        options = Options()
        options.output_file_name = ['output.pdf']

        combiner = Combiner(options)

        result = combiner.combine(['foo', 'bar'])

        subprocess.call.assert_called_with(['pdfunite', 'foo', 'bar', 'output.pdf'])
        assert_that(result).is_equal_to(subprocess.call.return_value)
