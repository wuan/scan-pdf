import pytest
from assertpy import assert_that
from mock import patch
from mock.mock import call

from scan_pdf import Combiner
from . import Options


class TestCombine:

    @pytest.fixture(scope="session", autouse=True)
    def pdf_merger(self):
        with patch("pypdf.PdfMerger") as pdf_merger:
            yield pdf_merger()

    def test_combine(self, pdf_merger):
        options = Options()
        options.output_file_name = ['output.pdf']

        combiner = Combiner(options)

        combiner.combine(['foo', 'bar'])

        pdf_merger.append.assert_has_calls([call("foo"), call("bar")])
        pdf_merger.write.assert_called_with("output.pdf")
        pdf_merger.close.assert_called()
