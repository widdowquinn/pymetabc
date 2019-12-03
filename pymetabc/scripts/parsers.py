# -*- coding: utf-8 -*-
"""Module providing pymetabc command-line parser."""

import sys

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Optional

from pymetabc import ADAPTER_PATH


def parse_cmdline(argv: Optional[List] = None) -> Namespace:
    """Return Namespace parsed from commmand-line options.

    :param argv:  List of command-line options
                  (used for testing)

    This function expects the argv argument to be empty, when run from the
    command-line.
    """
    # Process supplied arguments
    if argv is None:  # Use command-line
        argv = sys.argv[1:]
    parser = build_parser()
    return parser.parse_args([str(_) for _ in argv])


def build_parser() -> ArgumentParser:
    """Return ArgumentParser for pymetabc."""
    # Parent parser
    parser_main = ArgumentParser(
        prog="pymetabc", formatter_class=ArgumentDefaultsHelpFormatter
    )

    # Common arguments
    parser_main.add_argument(
        "-l",
        "--logfile",
        dest="logfile",
        action="store",
        default=None,
        type=Path,
        help="path to logfile output",
    )
    parser_main.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Report verbose output to log",
    )
    parser_main.add_argument(
        "-t",
        "--threads",
        action="store",
        dest="threads",
        default=cpu_count(),
        type=int,
        help="number of threads to use",
    )
    parser_main.add_argument(
        "--dryrun",
        dest="dryrun",
        action="store_true",
        default=False,
        help="do not run third-party tools (for testing)",
    )
    parser_main.add_argument(
        "--disable_tqdm",
        dest="disable_tqdm",
        action="store_true",
        default=False,
        help="disable tqdm progress bar",
    )

    # Data input/output
    parser_main.add_argument(
        action="store",
        dest="indir",
        default=None,
        type=Path,
        help="input directory of FASTQ files",
    )
    parser_main.add_argument(
        action="store",
        dest="outdir",
        default=None,
        type=Path,
        help="output directory for results",
    )
    parser_main.add_argument(
        "-s",
        "--sample_sep",
        action="store",
        dest="sample_sep",
        default="_L001",
        type=str,
        help="separator for sample ID in sample filenames",
    )

    # Trimming
    parser_main.add_argument(
        "--trim_exe",
        action="store",
        dest="trim_exe",
        default="trimmomatic",
        type=Path,
        help="path to trimmomatic executable",
    )
    parser_main.add_argument(
        "--trim_dir",
        action="store",
        dest="trim_dir",
        default="02_trimmed",
        type=str,
        help="directory name for trimmomatic output",
    )
    parser_main.add_argument(
        "--trim_fastq",
        action="store",
        dest="trim_fastq",
        default="phred33",
        type=str,
        help="FASTQ format for trimmomatic",
    )
    parser_main.add_argument(
        "--trim_adapters",
        action="store",
        dest="trim_adapters",
        default=Path(ADAPTER_PATH),
        type=Path,
        help="path to ILLUMINACLIP adapter file",
    )

    # Merging
    parser_main.add_argument(
        "--merge_exe",
        action="store",
        dest="merge_exe",
        default="flash",
        type=Path,
        help="path to flash executable",
    )
    parser_main.add_argument(
        "--merge_dir",
        action="store",
        dest="merge_dir",
        default="03_merged",
        type=str,
        help="directory name for flash output",
    )
    parser_main.add_argument(
        "--merge_maxoverlap",
        action="store",
        dest="merge_maxoverlap",
        default=300,
        type=int,
        help="maximum overlap for flash merge (-M in flash)",
    )

    # Hashing
    parser_main.add_argument(
        "--hash_dir",
        action="store",
        dest="hash_dir",
        default="04_hashed",
        type=str,
        help="directory name for merged read hashing output",
    )

    # Thresholding
    parser_main.add_argument(
        "--thresh_dir",
        action="store",
        dest="thresh_dir",
        default="05_thresholded",
        type=str,
        help="directory name for thresholded read output",
    )
    parser_main.add_argument(
        "--thresh_mode",
        action="store",
        dest="thresh_mode",
        default="cutoff",
        type=str,
        help="mode for thresholding merged reads",
    )
    parser_main.add_argument(
        "--thresh_cutoff",
        action="store",
        dest="thresh_cutoff",
        default=1000,
        type=int,
        help="threshold minimum abundance in a run",
    )
    # To be recovered when a control abundance threshold method is
    # implemented
    # parser_main.add_argument(
    #     "--thresh_controls",
    #     action="store",
    #     dest="thresh_controls",
    #     default="",
    #     type=str,
    #     help="list of control sample names",
    # )
    # parser_main.add_argument(
    #     "--thresh_percentile",
    #     action="store",
    #     dest="thresh_percentile",
    #     default=0.95,
    #     type=float,
    #     help="threshold control percentile",
    # )

    return parser_main
