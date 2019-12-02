# -*- coding: utf-8 -*-
"""Functions for handling trimmomatic."""
import os

from pathlib import Path

import pandas as pd


def collect_trimmomatic_summaries(dfm: pd.DataFrame) -> pd.DataFrame:
    """Return pd.DataFrame summarising trimmomatic output for each run.

    Generates nine new series (columns) for each row in the input
    dataframe corresponding to the trimmomatic summary output for each file
    """
    # Generate series of trimmomatic summary paths and process
    dfm["trim_summary"] = dfm["trimmed_dir"].apply(os.path.join, args=("summary.txt",))
    # Parse summary files into dataframe
    dfm = dfm.apply(parse_trimmomatic_summary, axis=1)
    return dfm


def parse_trimmomatic_summary(dfm: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame modified to include trimmomatic summary output."""
    fpath = Path(dfm["trim_summary"])
    with fpath.open("r") as ifh:
        for line in [_.strip() for _ in ifh if _.strip()]:
            key, val = line.split(": ")
            if "." in val:
                dfm[key] = float(val)
            else:
                dfm[key] = int(val)
    return dfm
