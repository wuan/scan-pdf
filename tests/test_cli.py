import logging
import os
from unittest.mock import PropertyMock, call, patch

import pytest

from scan_pdf.cli import parse_args, run
from tests import Options


class TestParseArgs:
    def test_defaults(self):
        with patch("sys.argv", ["scan-pdf", "output.pdf"]):
            options = parse_args()

        assert options.output_file_name == ["output.pdf"]
        assert options.device is None
        assert options.resolution == 300
        assert options.flatbed is False
        assert options.debug is False
        assert options.duplex is False
        assert options.color_mode == "gray"
        assert options.threshold is None
        assert options.color_depth == 4
        assert options.paper_format == "A4"
        assert options.paper_left == 0
        assert options.paper_top == 0
        assert options.paper_height == 0
        assert options.paper_width == 0

    def test_all_options(self):
        with patch(
            "sys.argv",
            [
                "scan-pdf",
                "output.pdf",
                "--device",
                "dev0",
                "--resolution",
                "600",
                "--flatbed",
                "-d",
                "--duplex",
                "--color-mode",
                "color",
                "--threshold",
                "128",
                "--color-depth",
                "8",
                "--paper-format",
                "A5",
                "--paper-left",
                "10",
                "--paper-top",
                "20",
                "--paper-height",
                "300",
                "--paper-width",
                "200",
            ],
        ):
            options = parse_args()

        assert options.output_file_name == ["output.pdf"]
        assert options.device == "dev0"
        assert options.resolution == 600
        assert options.flatbed is True
        assert options.debug is True
        assert options.duplex is True
        assert options.color_mode == "color"
        assert options.threshold == "128"
        assert options.color_depth == "8"
        assert options.paper_format == "A5"
        assert options.paper_left == "10"
        assert options.paper_top == "20"
        assert options.paper_height == "300"
        assert options.paper_width == "200"


class TestCli:
    @pytest.fixture
    def parse_args(self):
        with patch("scan_pdf.cli.parse_args") as parse_args:
            yield parse_args

    @pytest.fixture
    def scanner(self):
        with patch("scan_pdf.cli.Scanner") as scanner:
            yield scanner

    @pytest.fixture
    def converter(self):
        with patch("scan_pdf.cli.Converter") as converter:
            yield converter

    @pytest.fixture
    def combiner(self):
        with patch("scan_pdf.cli.Combiner") as combiner:
            yield combiner

    @pytest.fixture
    def shutil_move(self):
        with patch("shutil.move") as move:
            yield move

    def test_defaults(self, parse_args, scanner, converter, combiner, shutil_move):
        options = Options()
        options.output_file_name = ["output1.pdf"]
        options.debug = False
        options.duplex = False
        type(converter.return_value).page_file_suffix = PropertyMock(
            return_value=".pnm"
        )

        parse_args.return_value = options

        scanner.return_value.get_page_file_basenames.return_value = ["page1", "page2"]

        run()

        assert scanner.call_args_list == [call(options)]
        assert converter.call_args_list == [call(options)]
        assert converter.return_value.convert.call_args_list == [
            call("page1", scanner.return_value.page_file_suffix, False),
            call("page2", scanner.return_value.page_file_suffix, False),
        ]
        assert combiner.call_args_list == [call(options)]
        assert combiner.return_value.combine.call_args_list == [
            call(["page1.pnm", "page2.pnm"])
        ]

        move_calls = shutil_move.call_args_list
        assert len(move_calls) == 1
        move_call = move_calls[0]
        assert move_call[0][0].endswith("/output1.pdf")
        assert move_call[0][1] == "output1.pdf"

    def test_no_pages_found(
        self, parse_args, scanner, converter, combiner, shutil_move, caplog
    ):
        options = Options()
        options.output_file_name = ["output1.pdf"]
        options.debug = False
        options.duplex = False

        parse_args.return_value = options
        scanner.return_value.get_page_file_basenames.return_value = []

        cwd = os.getcwd()
        try:
            with caplog.at_level(logging.WARNING, logger="scan_pdf.cli"):
                run()
        finally:
            os.chdir(cwd)

        assert "no pages found" in caplog.text
        converter.assert_not_called()
        combiner.assert_not_called()
        shutil_move.assert_not_called()

    def test_duplex(self, parse_args, scanner, converter, combiner, shutil_move):
        options = Options()
        options.output_file_name = ["output1.pdf"]
        options.debug = False
        options.duplex = True
        type(converter.return_value).page_file_suffix = PropertyMock(
            return_value=".pnm"
        )

        parse_args.return_value = options
        scanner.return_value.get_page_file_basenames.return_value = [
            "page1",
            "page2",
            "page3",
        ]

        run()

        assert converter.return_value.convert.call_args_list == [
            call("page1", scanner.return_value.page_file_suffix, False),
            call("page2", scanner.return_value.page_file_suffix, True),
            call("page3", scanner.return_value.page_file_suffix, False),
        ]

    def test_debug(self, parse_args, scanner, converter, combiner, shutil_move):
        options = Options()
        options.output_file_name = ["output1.pdf"]
        options.debug = True
        options.duplex = False
        type(converter.return_value).page_file_suffix = PropertyMock(
            return_value=".pnm"
        )

        parse_args.return_value = options
        scanner.return_value.get_page_file_basenames.return_value = ["page1"]

        with patch("scan_pdf.cli.logging.basicConfig") as basic_config:
            run()

        basic_config.assert_called_once_with(level=logging.DEBUG)
