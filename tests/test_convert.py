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
        os_path_exists.assert_called_once_with("base.pdf")

    @pytest.mark.parametrize("color_mode", ["gray", "color"])
    def test_convert_uses_color_depth(self, subprocess, os_path_exists, color_mode):
        options = Options()
        options.color_mode = color_mode
        options.color_depth = 4
        options.resolution = 300
        subprocess.call.return_value = 0

        converter = Converter(options)

        converter.convert("base", ".suffix")

        args = subprocess.call.call_args[0][0]
        assert args[1:3] == ["-depth", "4"]

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

        caplog.set_level(logging.DEBUG, logger="scan_pdf.convert")

        result = converter.convert("base", ".suffix")

        assert_that(result).is_equal_to(1)
        command = "convert -depth 4 -density 300 -compress zip base.suffix base.pdf"
        assert caplog.record_tuples == [
            ("scan_pdf.convert", logging.INFO, "convert base"),
            ("scan_pdf.convert", logging.DEBUG, f"call: {command}"),
            ("scan_pdf.convert", logging.ERROR, f"convert failed: {command}"),
        ]

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

        assert caplog.record_tuples == [
            ("scan_pdf.convert", logging.ERROR, "target file 'base.pdf' does not exist")
        ]
