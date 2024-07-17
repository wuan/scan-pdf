import pytest
from mock import patch

from . import Options


class TestConverter:

    @pytest.fixture
    def subprocess(self):
        with patch("scan_pdf.convert.subprocess") as subprocess:
            yield subprocess

    def test_convert(self, subprocess):
        options = Options()


