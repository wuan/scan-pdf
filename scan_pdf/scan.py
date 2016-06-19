import glob
import logging
import os
import subprocess

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

        args += ['--source', 'Automatic Document Feeder']

        adf_mode = 'Simplex'
        if options.duplex:
            adf_mode = 'Duplex'
        args += ['--adf-mode', adf_mode]

        args += ['--resolution', str(options.resolution)]

        if options.paper_format in self.paper_formats:
            paper_format = self.paper_formats[options.paper_format]

            args += ['-l', str(paper_format.left)]
            args += ['-x', str(paper_format.width)]
            args += ['-t', str(paper_format.top)]
            args += ['-y', str(paper_format.height)]

        logger.info("call %s", " ".join(args))
        retval = subprocess.call(args)
        logger.info("call retured %d", retval)

    def get_page_file_basenames(self):
        output_files = glob.glob('out*' + self.page_file_suffix)
        output_files = sorted(output_files, cmp=self.compare_output_names)

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
