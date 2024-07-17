import pytest
from mock import patch

from scan_pdf import Scanner
from . import Options


class TestConverter:

    @pytest.fixture
    def subprocess(self):
        with patch("scan_pdf.scan.subprocess") as subprocess:
            yield subprocess

    def test_convert_default(self, subprocess):
        options = Options()
        options.device = None
        options.color_mode = None
        options.flatbed = None
        options.duplex = None
        options.resolution = 300
        options.threshold = None
        options.paper_format = "A4"
        options.paper_left = None
        options.paper_top = None
        options.paper_width = None
        options.paper_height = None

        scanner = Scanner(options)

        subprocess.call.assert_called_with(
            ['scanimage', '-b', '--format=pnm', '--mode', 'Gray', '--source', 'Automatic Document Feeder', '--adf-mode',
             'Simplex', '--resolution', '300', '-l', '0', '-x', '210', '-t', '0', '-y', '297'])

    def test_convert_flatbed_A5(self, subprocess):
        options = Options()
        options.device = None
        options.color_mode = "color"
        options.flatbed = True
        options.duplex = None
        options.resolution = 150
        options.threshold = None
        options.paper_format = "A5"
        options.paper_left = None
        options.paper_top = None
        options.paper_width = None
        options.paper_height = None

        scanner = Scanner(options)

        subprocess.call.assert_called_with(
            ['scanimage', '-b', '--format=pnm', '--mode', 'Color', '--source', 'Flatbed', '--batch-count', '1',
             '--resolution', '150', '-l', '0', '-x', '149', '-t', '0', '-y', '218'])

    def test_convert_duplex_bw(self, subprocess):
        options = Options()
        options.device = None
        options.color_mode = "bw"
        options.flatbed = None
        options.duplex = True
        options.resolution = 600
        options.threshold = 100
        options.paper_format = None
        options.paper_left = None
        options.paper_top = None
        options.paper_width = None
        options.paper_height = None

        scanner = Scanner(options)

        subprocess.call.assert_called_with(
            ['scanimage', '-b', '--format=pnm', '--mode', 'Lineart', '--source', 'Automatic Document Feeder',
             '--adf-mode', 'Duplex', '--resolution', '600', '--halftoning', 'None', '--threshold', '100', '-l', '0',
             '-x', '210', '-t', '0', '-y', '297'])
