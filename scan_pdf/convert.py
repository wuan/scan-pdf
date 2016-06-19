import os

import subprocess

from scan_pdf import logger


class Converter(object):
    page_file_suffix = '.pdf'

    def __init__(self, options):
        self.options = options

    def convert(self, source_basename, source_suffix):
        logger.info('convert %s', source_basename)
        args = ['convert']

        args += ['-depth', str(self.options.color_depth)]
        args += ['-density', str(self.options.resolution)]
        args += ['-compress', 'zip']
        args += [source_basename + source_suffix, source_basename + self.page_file_suffix]

        return subprocess.call(args)
