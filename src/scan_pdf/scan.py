import glob
import logging
import os
import subprocess
from functools import cmp_to_key

logger = logging.getLogger(__name__)


class PaperFormat(object):
    def __init__(self, left, width, top, height):
        self.left = left
        self.width = width
        self.top = top
        self.height = height


class Scanner(object):
    paper_formats = {'A4': PaperFormat(0, 210, 0, 297)}
    page_file_suffix = '.pnm'

    def __init__(self, options):

        args = ['scanimage', '-b']

        color_mode = 'Gray'
        if options.color_mode == 'bw':
            color_mode = 'Lineart'
        elif options.color_mode == 'color':
            color_mode = 'Color'
        args += ['--mode', color_mode]

        if options.flatbed:
            args += ['--source', 'Flatbed', '--batch-count', '1']
        else:
            args += ['--source', 'Automatic Document Feeder']
            args += ['--adf-mode', 'Duplex' if options.duplex else 'Simplex']

        args += ['--resolution', str(options.resolution)]

        if options.threshold:
            args += ['--halftoning', 'None', '--threshold', str(options.threshold)]

        if options.paper_format in self.paper_formats:
            paper_format = self.paper_formats[options.paper_format]

            args += ['-l', str(paper_format.left)]
            args += ['-x', str(paper_format.width)]
            args += ['-t', str(paper_format.top)]
            args += ['-y', str(paper_format.height)]

        logger.debug("call %s", " ".join(args))
        retval = subprocess.call(args)
        logger.debug("call retured %d", retval)

    def get_page_file_basenames(self):
        output_files = glob.glob('out*' + self.page_file_suffix)
        output_files = sorted(output_files, key=cmp_to_key(self.compare_output_names))

        return [os.path.splitext(output_file)[0] for output_file in output_files]

    @staticmethod
    def compare_output_names(name1, name2):
        if len(name1) < len(name2):
            return -1
        elif len(name1) > len(name2):
            return 1
        elif name1 < name2:
            return -1
        elif name1 > name2:
            return 1
        else:
            return 0
