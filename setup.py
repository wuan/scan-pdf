# coding=utf-8
import glob

from setuptools import setup, find_packages

setup(
    name='scan-pdf',
    version='0.1.8',
    packages=find_packages(),
    scripts=glob.glob('scripts/*'),
    description='Tools for using scanners with document feeder',
    author='Andreas Würl',
    author_email='andreas@wuerl.net',
    url='https://github.com/wuan/scan-pdf',
    license='Apache-2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[],
    tests_require=['pytest-cov', 'mock', 'assertpy'],
)