import os

import pytest
from mock import patch

from scan_pdf import Scanner
from . import Options, touch


class TestConverter:
    @pytest.fixture
    def subprocess(self):
        with patch("scan_pdf.scan.subprocess") as subprocess:
            yield subprocess

    @pytest.fixture
    def options(self):
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
        return options

    def test_convert_default(self, subprocess, options):
        Scanner(options)

        subprocess.call.assert_called_with(
            [
                "scanimage",
                "-b",
                "--format=pnm",
                "--mode",
                "Gray",
                "--source",
                "Automatic Document Feeder",
                "--adf-mode",
                "Simplex",
                "--resolution",
                "300",
                "-l",
                "0",
                "-x",
                "210",
                "-t",
                "0",
                "-y",
                "297",
            ]
        )

    def test_convert_flatbed_A5_device(self, subprocess, options):
        options.device = "foo"
        options.color_mode = "color"
        options.flatbed = True
        options.resolution = 150
        options.paper_format = "A5"

        Scanner(options)

        subprocess.call.assert_called_with(
            [
                "scanimage",
                "-b",
                "--format=pnm",
                "-d",
                "foo",
                "--mode",
                "Color",
                "--source",
                "Flatbed",
                "--batch-count",
                "1",
                "--resolution",
                "150",
                "-l",
                "0",
                "-x",
                "148",
                "-t",
                "0",
                "-y",
                "210",
            ]
        )

    def test_convert_duplex_bw(self, subprocess, options):
        options.color_mode = "bw"
        options.duplex = True
        options.resolution = 600
        options.threshold = 100

        Scanner(options)

        subprocess.call.assert_called_with(
            [
                "scanimage",
                "-b",
                "--format=pnm",
                "--mode",
                "Lineart",
                "--source",
                "Automatic Document Feeder",
                "--adf-mode",
                "Duplex",
                "--resolution",
                "600",
                "--halftoning",
                "None",
                "--threshold",
                "100",
                "-l",
                "0",
                "-x",
                "210",
                "-t",
                "0",
                "-y",
                "297",
            ]
        )

    def test_base_folder(self, tmp_path, subprocess, options):
        os.chdir(tmp_path)
        scanner = Scanner(options)
        touch("notpage.pnm")
        touch("outpage.not")
        touch("outpage.pnm")
        touch("outpage1.pnm")
        touch("outpage2.pnm")
        touch("outpage13.pnm")
        touch("outpage17.pnm")
        touch("outpage127.pnm")

        names = scanner.get_page_file_basenames()

        assert names == [
            "outpage",
            "outpage1",
            "outpage2",
            "outpage13",
            "outpage17",
            "outpage127",
        ]
