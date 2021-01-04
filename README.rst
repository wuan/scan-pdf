`scan-pdf <https://github.com/wuan/scan-pdf>`_
==============================================

.. image:: https://badge.fury.io/py/scan-pdf.png
    :alt: PyPi-Package
    :target: https://badge.fury.io/py/scan-pdf
.. image:: https://travis-ci.org/wuan/scan-pdf.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/wuan/scan-pdf
.. image:: https://coveralls.io/repos/wuan/scan-pdf/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/wuan/scan-pdf?branch=master

simple script to create pdf files from a scanner with document feeder

Examples
========

scan double sided pages to pdf
------------------------------

Example::

    scan-pdf --resolution 100 --duplex test.pdf

supported options
-----------------

.. code-block::

    > scan-pdf -h
    usage: scan-pdf [-h] [--resolution RESOLUTION] [--flatbed] [-d] [--duplex] [--color-mode {bw,gray,color}] [--threshold THRESHOLD] [--color-depth COLOR_DEPTH] [--paper-format {A4,A5}] [--paper-left PAPER_LEFT] [--paper-top PAPER_TOP]
                    [--paper-height PAPER_HEIGHT] [--paper-width PAPER_WIDTH]
                    output_file_name

    Produce PDF from Scanner with document-feeder

    positional arguments:
      output_file_name      name of the produced output file

    optional arguments:
      -h, --help            show this help message and exit
      --resolution RESOLUTION
                            scan resolution DPI (default: 300)
      --flatbed             scan only one page from flatbed glass
      -d                    enable debug output
      --duplex              scan both sides of document
      --color-mode {bw,gray,color}
                            default: gray
      --threshold THRESHOLD
                            disabled by default
      --color-depth COLOR_DEPTH
      --paper-format {A4,A5}
                            default: A4
      --paper-left PAPER_LEFT
                            override left offset
      --paper-top PAPER_TOP
                            override top offset
      --paper-height PAPER_HEIGHT
                            override paper height
      --paper-width PAPER_WIDTH
                            override paper width

