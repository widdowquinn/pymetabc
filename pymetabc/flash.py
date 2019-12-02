# -*- coding: utf-8 -*-
"""Functions for handling flash."""

import subprocess

from argparse import Namespace
from pathlib import Path
from typing import Generator

import pandas as pd

from tqdm import tqdm


def generate_flash_commands(dfm: pd.DataFrame, args: Namespace) -> Generator:
    """Generate flash commands.

    :param dfm:  pd.DataFrame containing one row per sample
    :param args:  Namespace of parsed command-line arguments

    Yields command (as List[str]) for each sample, in turn
    """
    cmd_base = ["flash", "-O", "-t", args.threads, "-M", args.merge_maxoverlap]
    for _, row in dfm.iterrows():
        outdir = Path(row["merged_dir"])
        readfiles = sorted(list(Path(row["trimmed_dir"]).glob("*_trimmed.fastq")))
        outputs = ["-d", outdir, "-o", readfiles[0].stem.split("_L001")[0]]
        yield (list(map(str, cmd_base + outputs + [str(_) for _ in readfiles])), outdir)


def run_flash(dfm: pd.DataFrame, args: Namespace) -> pd.DataFrame:
    """Run flash on a dataset.

    :param dfm:  pd.DataFrame containing one row per sample
    :param args:  Namespace of parsed command-line arguments

    Returns modified dataframe with the flash command that was
    applied, and the path to the output directory as new columns
    """
    cmdlist = []
    mergedirs = []
    for cmd, mergedir in tqdm(
        generate_flash_commands(dfm, args), disable=args.disable_tqdm
    ):
        if not args.dryrun:
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=True,
            )
        cmdlist.append(cmd)
        mergedirs.append(str(mergedir))

    dfm["merge_cmd"] = cmdlist
    return dfm
