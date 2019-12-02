#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) University of Strathclyde 2019
# Author: Leighton Pritchard
#
# Contact:
# leighton.pritchard@strath.ac.uk
#
# Leighton Pritchard,
# Strathclyde Institute for Pharmacy and Biomedical Sciences,
# Cathedral Street,
# Glasgow,
# G1 1XQ
# Scotland,
# UK
#
# The MIT License
#
# Copyright (c) 2019 University of Strathclyde
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Distribution setup."""

import sys
import re
import setuptools

try:
    import distribute_setup

    distribute_setup.use_setuptools()
except ImportError:
    pass

# Get long description from README.md
with open("README.md", "r") as dfh:
    long_description = dfh.read()  # pylint: disable=C0103

# parse version from package/module without importing or
# evaluating the code
with open("pymetabc/__init__.py") as fh:
    for line in fh:
        # The escaping/use of quotes in the re.search() below can be treacherous
        m = re.search(r'^__version__ = "(?P<version>[^"]+)"$', line)
        print(m)
        if m:
            version = m.group("version")
            break

if sys.version_info <= (3, 0):
    sys.stderr.write("ERROR: pymetabc requires Python 3 " + "or above...exiting.\n")
    sys.exit(1)

setuptools.setup(
    name="pymetabc",
    version=version,
    author="Leighton Pritchard",
    author_email="leighton.pritchard@strath.ac.uk",
    description="".join(
        [
            (
                "pymetabc provides a lightweight metabarcoding trim, merge, "
                "threshold and visualisation tool"
            )
        ]
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="genome bioinformatics sequence metabarcoding metagenomics",
    platforms="Posix; MacOS X",
    url="http://widdowquinn.github.io/pymetabc/",  # project home page
    download_url="https://github.com/widdowquinn/pymetabc/releases",
    scripts=[],
    entry_points={"console_scripts": ["pymetabc = pymetabc.scripts.pymetabc:run_main"]},
    packages=setuptools.find_packages(),
    package_data={"pymetabc": ["pymetabc/data/TruSeq3-PE.fa"]},
    include_package_date=True,
    install_requires=["biopython", "bokeh", "pandas", "tqdm"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
