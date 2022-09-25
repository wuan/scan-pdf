import pytest
from assertpy import assert_that
from mock import patch
from mock.mock import call

from scan_pdf import Combiner


class Options(object):
    pass


class TestCombine:

    @pytest.fixture(scope="session", autouse=True)
    def pdf_merger(self):
        with patch("PyPDF2.PdfMerger") as pdf_merger:
            yield pdf_merger()

    def test_combine(self, pdf_merger):
        options = Options()
        options.output_file_name = ['output.pdf']

        combiner = Combiner(options)

        result = combiner.combine(['foo', 'bar'])

        pdf_merger.append.assert_has_calls([call("foo"), call("bar")])
        pdf_merger.write.assert_called_with("output.pdf")
        pdf_merger.close.assert_called()
        assert_that(result).is_equal_to(0)
