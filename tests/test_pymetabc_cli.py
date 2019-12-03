# -*- coding: utf-8 -*-
"""Test complete run of pymetabc.

Intended to be run from repository root with pytest -v
"""

import logging
import shutil
import unittest

from argparse import Namespace
from multiprocessing import cpu_count
from pathlib import Path
from typing import NamedTuple

from pymetabc import ADAPTER_PATH
from pymetabc.scripts.pymetabc import run_main, run_pipeline


class DirPaths(NamedTuple):

    """Paths to input, output, and target data directories."""

    indir: Path
    outdir: Path
    tgtdir: Path


class ThirdPartyExes(NamedTuple):

    """Paths to third party executables."""

    trimmomatic: str
    flash: str


class TestPymetabcCLI(unittest.TestCase):

    """Class defining complete run through of pymetabc on test data."""

    def setUp(self) -> None:
        """Configure parameters for tests."""
        # Set up paths to input, output, target data
        testdir = Path("tests")  # intended relative to repository root
        self.dirpaths = DirPaths(
            testdir / "test_input", testdir / "test_output", testdir / "test_targets"
        )
        shutil.rmtree(self.dirpaths.outdir, ignore_errors=True)
        self.dirpaths.outdir.mkdir(exist_ok=True)

        # Null logger instance
        self.logger = logging.getLogger("TestIndexSubcommand logger")
        self.logger.addHandler(logging.NullHandler())

        # Set up paths to third party executables
        self.exes = ThirdPartyExes("trimmomatic", "flash")

        # Set namespace arguments
        self.args = Namespace(
            logfile=None,
            verbose=False,
            threads=cpu_count(),
            dryrun=False,
            disable_tqdm=True,
            indir=self.dirpaths.indir,
            outdir=self.dirpaths.outdir,
            sample_sep="_L001",
            trim_exe=self.exes.trimmomatic,
            trim_dir="02_trimmed",
            trim_fastq="phred33",
            trim_adapters=Path(ADAPTER_PATH),
            merge_exe=self.exes.flash,
            merge_dir="03_merged",
            merge_maxoverlap=300,
            hash_dir="04_hashed",
            thresh_dir="05_thresholded",
            thresh_mode="cutoff",
            thresh_cutoff=1000,
        )

        # Set command-line arguments
        self.argv = ["-t", cpu_count(), self.dirpaths.indir, self.dirpaths.outdir]

    def test_script(self) -> None:
        """Test script run of pymetabc."""
        run_pipeline(self.args, self.logger)

    def test_cli(self) -> None:
        """Test CLI parsing run of pymetabc."""
        run_main(self.argv, self.logger)
