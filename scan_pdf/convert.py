import logging

import subprocess

logger = logging.getLogger(__name__)

class Converter(object):
    page_file_suffix = '.pdf'

    def __init__(self, options):
        self.options = options

    def convert(self, source_basename, source_suffix):
        logger.info('convert %s', source_basename)
        args = ['convert']

        color_depth = self.options.color_depth if self.options.color_mode != 'bw' else 1
        args += ['-depth', str(color_depth)]
        args += ['-density', str(self.options.resolution)]
        args += ['-compress', 'zip']
        args += [source_basename + source_suffix, source_basename + self.page_file_suffix]

        return subprocess.call(args)
