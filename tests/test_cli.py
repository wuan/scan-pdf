import pytest
from mock import patch, call, PropertyMock

from scan_pdf.cli import run
from tests import Options


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
