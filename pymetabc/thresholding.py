# -*- coding: utf-8 -*-
"""Module to threshold merged, hashed reads."""

from argparse import Namespace
from pathlib import Path
from typing import Generator

import pandas as pd

from Bio import SeqIO
from tqdm import tqdm


def add_thresholded_reads(dfm: pd.DataFrame, args: Namespace) -> Generator:
    """Generate one output directory per sample under the root directory.

    :param dfm:  pd.DataFrame containing one row per sample
    :param args:  Namespace of parsed command-line options

    Yields path (as str) to the directory
    """
    for _, row in tqdm(
        dfm.iterrows(), disable=args.disable_tqdm
    ):  # one subdirectory per sample
        readfile = Path(row["hashed_reads"])
        ofname = args.threshdir / readfile.name
        if not args.dryrun:
            thresholded_reads = thresh_cutoff(readfile, args)
            SeqIO.write(thresholded_reads, ofname, "fasta")
        yield str(ofname)


def thresh_cutoff(readfile: Path, args: Namespace) -> Generator:
    """Generate sequences from readfile with abundance above hard threshold.

    :param readfile:  Path to input FASTA file
    :param args:  Namespace of parsed command line arguments

    This method uses a hard threshold specified in args.thresh_cutoff.
    """
    with readfile.open("r") as ifh:
        for record in SeqIO.parse(ifh, "fasta"):
            _, abd = record.id.split("_")
            if int(abd) > args.thresh_cutoff:
                yield record
