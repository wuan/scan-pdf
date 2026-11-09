import logging
from unittest.mock import patch

import pytest
from assertpy import assert_that

from scan_pdf import Converter

from . import Options


class TestConverter:
    @pytest.fixture
    def subprocess(self):
        with patch("scan_pdf.convert.subprocess") as subprocess:
            yield subprocess

    @pytest.fixture
    def os_path_exists(self):
        with patch("scan_pdf.convert.os.path.exists", return_value=True) as exists:
            yield exists

    def test_convert(self, subprocess, os_path_exists):
        options = Options()
        options.color_mode = "bw"
        options.resolution = 300
        subprocess.call.return_value = 0

        converter = Converter(options)

        result = converter.convert("base", ".suffix")

        subprocess.call.assert_called_with(
            [
                "convert",
                "-depth",
                "1",
                "-density",
                "300",
                "-compress",
                "zip",
                "base.suffix",
                "base.pdf",
            ]
        )
        assert_that(result).is_equal_to(subprocess.call.return_value)

    def test_convert_flip(self, subprocess, os_path_exists):
        options = Options()
        options.color_mode = "bw"
        options.resolution = 300
        subprocess.call.return_value = 0

        converter = Converter(options)

        converter.convert("base", ".suffix", flip=True)

        args = subprocess.call.call_args[0][0]
        assert "-rotate" in args
        assert "180" in args
        assert args.index("-rotate") == args.index("-compress") + 2

    def test_convert_nonzero_returncode(self, subprocess, os_path_exists, caplog):
        options = Options()
        options.color_mode = "gray"
        options.color_depth = 4
        options.resolution = 300
        subprocess.call.return_value = 1

        converter = Converter(options)

        with caplog.at_level(logging.ERROR, logger="scan_pdf.convert"):
            result = converter.convert("base", ".suffix")

        assert_that(result).is_equal_to(1)
        assert "convert failed" in caplog.text

    def test_convert_missing_target_file(self, subprocess, caplog):
        options = Options()
        options.color_mode = "gray"
        options.color_depth = 4
        options.resolution = 300
        subprocess.call.return_value = 0

        converter = Converter(options)

        with patch("scan_pdf.convert.os.path.exists", return_value=False):
            with caplog.at_level(logging.ERROR, logger="scan_pdf.convert"):
                converter.convert("base", ".suffix")

        assert "does not exist" in caplog.text
