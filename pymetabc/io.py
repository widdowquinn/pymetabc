# -*- coding: utf-8 -*-
"""Module to handle dataframes and data IO."""

from argparse import Namespace
from pathlib import Path
from typing import Generator, Optional

import pandas as pd


def add_sample_subdirs(
    dfm: pd.DataFrame, root_dir: Optional[Path] = Path(".")
) -> Generator:
    """Generate one output directory per sample under the root directory.

    :param dfm:  pd.DataFrame containing one row per sample
    :param root_dir:  Path to root directory for new output

    Yields path (as str) to the directory
    """
    for idx, _ in dfm.iterrows():  # one subdirectory per sample
        sample_dir = root_dir / idx
        sample_dir.mkdir(exist_ok=True)
        yield str(sample_dir)


def create_dataframe(args: Namespace) -> pd.DataFrame:
    """Return new dataframe describing paths to sample files in root directory.

    :param args:  Namespace of command line arguments

    The returned dataframe is indexed by the column "sample_name" (this is
    determined by using args.sample_sep to split the sample directory name),
    and contains columns for "sample_dir" (path to input files), "fwd_read_path"
    (path to forward reads for the sample), and "rev_read_path" (path to reverse
    reads for the sample).
    """
    data = pd.DataFrame(sampledirs_to_paths(args))
    data.set_index("sample_name", inplace=True)
    return data


def sampledirs_to_paths(args: Namespace) -> Generator:
    """Generate dictionaries of sample data paths.

    :param args:  Namespace of command line arguments

    Yields a dictionary corresponding to rows of a dataframe for each
    sample, in turn.
    """
    for sample_dir in [
        _ for _ in args.indir.iterdir() if _.is_dir()
    ]:  # One folder per sample
        sample_name = sample_dir.name.split(args.sample_sep)[0]
        # sort to ensure fwd, rev order
        freads, rreads = sorted(tuple(sample_dir.iterdir()))
        # Stringify paths so that BeakerX/pandas can handle them
        yield dict(
            [
                ("sample_name", sample_name),
                ("sample_dir", str(sample_dir)),
                ("fwd_read_path", str(freads)),
                ("rev_read_path", str(rreads)),
            ]
        )
