#!/usr/bin/env python


import argparse
import logging
import os
import shutil
import stat

from scan_pdf import Combiner, Converter, Scanner, TempDir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Produce PDF from Scanner with document-feeder"
    )
    _ = parser.add_argument(
        "output_file_name", nargs=1, help="name of the produced output file"
    )
    _ = parser.add_argument("--device", help="optional device locator")
    _ = parser.add_argument(
        "--resolution",
        type=int,
        default=300,
        help="scan resolution DPI (default: 300)",
    )
    _ = parser.add_argument(
        "--flatbed",
        action="store_true",
        help="scan only one page from flatbed glass",
    )
    _ = parser.add_argument(
        "-d", dest="debug", action="store_true", help="enable debug output"
    )
    _ = parser.add_argument(
        "--duplex", action="store_true", help="scan both sides of document"
    )
    _ = parser.add_argument(
        "--color-mode",
        choices=["bw", "gray", "color"],
        default="gray",
        help="default: gray",
    )
    _ = parser.add_argument("--threshold", help="disabled by default")
    _ = parser.add_argument("--color-depth", default=4)
    _ = parser.add_argument(
        "--paper-format",
        choices=Scanner.paper_formats.keys(),
        default="A4",
        help="default: A4",
    )
    _ = parser.add_argument("--paper-left", default=0, help="override left offset")
    _ = parser.add_argument("--paper-top", default=0, help="override top offset")
    _ = parser.add_argument("--paper-height", default=0, help="override paper height")
    _ = parser.add_argument("--paper-width", default=0, help="override paper width")
    return parser


def parse_args() -> argparse.Namespace:
    return build_parser().parse_args()


def run() -> None:
    options = parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)
    logger = logging.getLogger(__name__)

    origin_dir = os.getcwd()

    with TempDir() as temp_dir:
        os.chmod(temp_dir, stat.S_IRWXU)
        os.chdir(temp_dir)

        output_file_name = options.output_file_name[0]

        scanner = Scanner(options)

        output_basenames = scanner.get_page_file_basenames()

        if len(output_basenames) > 0:
            converter = Converter(options)
            for page_number, output_basename in enumerate(output_basenames, start=1):
                _ = converter.convert(
                    output_basename,
                    scanner.page_file_suffix,
                    options.duplex and page_number % 2 == 0,
                )

            combiner = Combiner(options)
            combiner.combine(
                [
                    output_basename + converter.page_file_suffix
                    for output_basename in output_basenames
                ]
            )

            os.chdir(origin_dir)
            _ = shutil.move(
                os.path.join(temp_dir, os.path.basename(output_file_name)),
                output_file_name,
            )
        else:
            logger.warning("no pages found")
