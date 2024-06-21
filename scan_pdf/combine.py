import logging

import pypdf

logger = logging.getLogger(__name__)


class Combiner(object):
    def __init__(self, options):
        self.options = options

    def combine(self, page_file_names):
        output_file_name = self.options.output_file_name[0]
        logger.info("combine %d pages into %s", len(page_file_names), output_file_name)

        merger = pypdf.PdfMerger()

        for pdf in page_file_names:
            merger.append(pdf)

        merger.write(output_file_name)
        merger.close()

        return 0
