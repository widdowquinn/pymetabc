# -*- coding: utf-8 -*-
"""Implements pymetabc script for processing metabarcoding sequence data."""

import sys
import time

from argparse import Namespace
from logging import Logger
from typing import List, Optional

from pymetabc import flash, hashing, io, trimmomatic

from .logger import build_logger
from .parsers import parse_cmdline
from .. import __version__


#  Main function: run as the pymetabc script
def run_main(argv: Optional[List] = None, logger: Optional[Logger] = None) -> int:
    """Run pymetabc as a script.

    :param argv:  List of arguments as if from command-line,
                  (used for testing)
    :param logger:  Logger object
                  (used for testing)

    Process input FASTQ sequence files from a single input directory in the pymetabc
    pipeline:

    - trim reads with trimmomatic
    - merge reads with flash
    - hash reads and count abundance
    - generate output tables and figures
    """
    # If testing, a List was passed, and is processed. Otherwise we collect sys.argv
    if argv is None:
        args = parse_cmdline()
    else:
        args = parse_cmdline(argv)

    # Catch execution with no arguments, report version and return zero
    if len(sys.argv) == 1:
        sys.stderr.write(f"pymetabc version: {__version__}")
        return 0

    # Set up logging (if necessary; when testing a logger is passed)
    time0 = time.time()
    if logger is None:
        logger = build_logger(f"pymetabc {__version__}", args)

    # Run the pipeline
    returnval = run_pipeline(args, logger)

    # Report how it ended
    logger.info("Completed. time taken: %.3f", (time.time() - time0))
    return returnval


# Run the pipeline with passed arguments
def run_pipeline(args: Namespace, logger: Logger) -> int:
    """Run the stages of the pymetabc pipeline.

    :param args:  Namespace of command-line arguments
    :param logger:  Logger for output
    """
    # Report calling arguments
    logger.info("pymetabc called with arguments:")
    for key, val in vars(args).items():
        logger.info("\t%s:\t%s", key, val)

    # Create output directories
    logger.info("Creating output directories:")
    logger.info("\tOutput root: %s", args.outdir)
    args.outdir.mkdir(exist_ok=True)
    args.trimdir = args.outdir / args.trim_dir
    logger.info("\tTrimming output: %s", args.trimdir)
    args.trimdir.mkdir(exist_ok=True)
    args.mergedir = args.outdir / args.merge_dir
    logger.info("\tMerge output: %s", args.mergedir)
    args.mergedir.mkdir(exist_ok=True)
    args.hashdir = args.outdir / args.hash_dir
    logger.info("\tHashing output: %s", args.hashdir)
    args.hashdir.mkdir(exist_ok=True)

    # Process input data
    logger.info("Stage 1: Process input data")
    dfm = io.create_dataframe(args)
    logger.info("\tFound %d samples:", len(dfm))
    logger.info("\t\t%s, ...", ", ".join(sorted(list(dfm.index))[:5]))

    # Write table of input file paths to disk
    ofname = args.outdir / "01_input_files.tab"
    logger.info("Writing input file paths to %s", ofname)
    dfm.to_csv(ofname, sep="\t", encoding="utf-8")

    # Trim reads
    logger.info("Stage 2: Trim input reads")
    dfm["trimmed_dir"] = list(io.add_sample_subdirs(dfm, args.trimdir))
    trimmomatic.run_trimmomatic(dfm, args)

    # Parse read summaries into dataframe
    logger.info("\tParsing trimmomatic output")
    dfm = trimmomatic.collect_trimmomatic_summaries(dfm)

    # Write table of trimmed read data to disk
    ofname = args.outdir / "02_trimmed.tab"
    logger.info("Writing trimmed data table to %s", ofname)
    dfm.to_csv(ofname, sep="\t", encoding="utf-8")

    # Write bokeh plot of trimmomatic summary data to disk
    ofname = args.outdir / "02_summaries.html"
    logger.info("Writing trimmomatic summaries plot to %s", ofname)
    trimmomatic.plot_trimmomatic_summary(dfm, ofname)

    # Merge trimmed reads
    logger.info("Stage 3: Merge trimmed reads")
    dfm["merged_dir"] = list(io.add_sample_subdirs(dfm, args.mergedir))
    logger.info("\tMerging reads with flash")
    dfm = flash.run_flash(dfm, args)

    # Write table of merged read data to disk
    ofname = args.outdir / "03_merged.tab"
    logger.info("Writing merged data table to %s", ofname)
    dfm.to_csv(ofname, sep="\t", encoding="utf-8")

    # Hash merged reads
    logger.info("Stage 4: Hash merged reads")
    logger.info("\tHashing merged reads")
    dfm["hashed_reads"] = list(hashing.add_hashed_reads(dfm, args))

    # Write table of merged read data to disk
    ofname = args.outdir / "04_hashed.tab"
    logger.info("Writing hashed data table to %s", ofname)
    dfm.to_csv(ofname, sep="\t", encoding="utf-8")

    # How many unique hashes are there?
    uhashes = hashing.count_unique_hashes(args.hashdir)
    logger.info("\tThere are %d unique merged reads (abundance > 1)", len(uhashes))
    ofname = args.outdir / "04_hashed_abundance_distribution.html"
    logger.info("Writing read abundance distribution plot to %s", ofname)
    hashing.plot_hashed_abundance_distribution(uhashes, ofname)

    # Write bokeh plot of hashed read abundances to disk
    ofname = args.outdir / "04_hashed_abundances.html"
    logger.info("Writing hashed read abundance plot to %s", ofname)
    # trimmomatic.plot_read_hash_abundances(dfm, ofname)

    return 0
