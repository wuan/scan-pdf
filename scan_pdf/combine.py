import argparse
import logging
from typing import List

import pypdf

logger = logging.getLogger(__name__)


class Combiner:
    def __init__(self, options: argparse.Namespace):
        self.options = options

    def combine(self, page_file_names: List[str]) -> None:
        output_file_name = self.options.output_file_name[0]
        logger.info("combine %d pages into %s", len(page_file_names), output_file_name)

        merger = pypdf.PdfMerger()

        for pdf in page_file_names:
            merger.append(pdf)

        merger.write(output_file_name)
        merger.close()
