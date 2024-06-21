#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging
import os
import shutil
import stat

from scan_pdf import Scanner, Converter, Combiner, TempDir

def run():
    parser = argparse.ArgumentParser(description='Produce PDF from Scanner with document-feeder')
    parser.add_argument('output_file_name', type=str, nargs=1,
                        help='name of the produced output file')
    parser.add_argument('--device', dest='device', type=str,
                        default=None,
                        help='optional device locator')
    parser.add_argument('--resolution', dest='resolution', type=int,
                        default=300,
                        help='scan resolution DPI (default: 300)')
    parser.add_argument('--flatbed', dest='flatbed', action='store_true',
                        help='scan only one page from flatbed glass')
    parser.add_argument('-d', dest='debug', action='store_true',
                        help='enable debug output')
    parser.add_argument('--duplex', dest='duplex', action='store_true',
                        help='scan both sides of document')
    parser.add_argument('--color-mode', dest='color_mode', action='store',
                        choices=['bw', 'gray', 'color'],
                        default='gray', help='default: gray')
    parser.add_argument('--threshold', dest='threshold', default=None, action='store', help='disabled by default')
    parser.add_argument('--color-depth', dest='color_depth', default=4)
    parser.add_argument('--paper-format', dest='paper_format', action='store',
                        choices=Scanner.paper_formats.keys(),
                        default='A4', help='default: A4')
    parser.add_argument('--paper-left', dest='paper_left', default=0, help="override left offset")
    parser.add_argument('--paper-top', dest='paper_top', default=0, help="override top offset")
    parser.add_argument('--paper-height', dest='paper_height', default=0, help="override paper height")
    parser.add_argument('--paper-width', dest='paper_width', default=0, help="override paper width")

    options = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)
    logger = logging.getLogger(__name__)

    origin_dir = os.getcwd()

    with TempDir() as temp_dir:
        os.chmod(temp_dir, stat.S_IRWXU |stat.S_IRWXG | stat.S_IRWXO)
        os.chdir(temp_dir)

        output_file_name = options.output_file_name[0]

        scanner = Scanner(options)

        output_basenames = scanner.get_page_file_basenames()

        if len(output_basenames) > 0:
            converter = Converter(options)
            for page_number, output_basename in enumerate(output_basenames, start=1):
                converter.convert(output_basename, scanner.page_file_suffix, options.duplex and page_number % 2 == 0)

            combiner = Combiner(options)
            combiner.combine([output_basename + converter.page_file_suffix for output_basename in output_basenames])

            os.chdir(origin_dir)
            shutil.move(os.path.join(temp_dir, os.path.basename(output_file_name)), output_file_name)
        else:
            logger.warn("no pages found")
