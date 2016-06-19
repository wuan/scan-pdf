import logging
import os

import subprocess

logger = logging.getLogger(__name__)


class Combiner(object):
    def __init__(self, options):
        self.options = options

    def combine(self, page_file_names):
        logger.info("combine %d files into %s", len(page_file_names), self.options.output_file_name)
        combine_args = ['pdftk']
        combine_args += page_file_names
        output_file_name = self.options.output_file_names[0]
        combine_args += ['output', os.path.basename(output_file_name), 'compress']
        return subprocess.call(combine_args)
