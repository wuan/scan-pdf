`scan-pdf <https://github.com/wuan/scan-pdf>`_
==============================================

.. image:: https://badge.fury.io/py/scan-pdf.png
    :alt: PyPi-Package
    :target: https://badge.fury.io/py/scan-pdf
.. image:: https://sonar.tryb.de/api/project_badges/measure?project=scan-pdf&metric=alert_status&token=sqb_53c510ab94d29224e4930fe5e9babdfb9cc8e3e6
    :alt: Build Status
.. image:: https://sonar.tryb.de/api/project_badges/measure?project=scan-pdf&metric=coverage&token=sqb_53c510ab94d29224e4930fe5e9babdfb9cc8e3e6
    :alt: Coverage

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

