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
    usage: scan-pdf [-h] [--resolution RESOLUTION] [--duplex]
            [--color-mode {bw,gray,color}] [--color-depth COLOR_DEPTH]
            [--paper-format {A4}]
            output_file_name

    Produce PDF from Scanner with document-feeder

    positional arguments:
      output_file_name      name of the produced output file

    optional arguments:
      -h, --help            show this help message and exit
      --resolution RESOLUTION
                scan resolution DPI (default: 300)
      --duplex              scan both sides of document
      --color-mode {bw,gray,color}
                default: gray
      --color-depth COLOR_DEPTH
      --paper-format {A4}   default: A4
