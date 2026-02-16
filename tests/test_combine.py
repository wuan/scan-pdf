import pytest
from mock import patch
from mock.mock import call

from scan_pdf import Combiner
from . import Options


class TestCombine:
    @pytest.fixture(scope="session", autouse=True)
    def pdf_writer(self):
        with patch("pypdf.PdfWriter") as pdf_writer:
            yield pdf_writer()

    def test_combine(self, pdf_writer):
        options = Options()
        options.output_file_name = ["output.pdf"]

        combiner = Combiner(options)

        combiner.combine(["foo", "bar"])

        pdf_writer.append.assert_has_calls([call("foo"), call("bar")])
        pdf_writer.write.assert_called_once()
        pdf_writer.close.assert_called()
