import pytest
from assertpy import assert_that
from mock import patch

from scan_pdf import Converter


class Options(object):
    pass


class TestConverter:

    @pytest.fixture
    def subprocess(self):
        with patch("scan_pdf.convert.subprocess") as subprocess:
            yield subprocess

    def test_convert(self, subprocess):
        options = Options()
        options.color_mode = 'bw'
        options.resolution = 300
        subprocess.call.return_value = 0

        converter = Converter(options)

        result = converter.convert('base', '.suffix')

        subprocess.call.assert_called_with(
            ['convert', '-depth', '1', '-density', '300', '-compress', 'zip', 'base.suffix', 'base.pdf'])
        assert_that(result).is_equal_to(subprocess.call.return_value)
