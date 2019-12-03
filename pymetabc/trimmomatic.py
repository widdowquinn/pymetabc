# -*- coding: utf-8 -*-
"""Functions for handling trimmomatic."""
import os

import subprocess

from argparse import Namespace
from pathlib import Path
from typing import Generator

import pandas as pd

from tqdm import tqdm


def collect_trimmomatic_summaries(dfm: pd.DataFrame) -> pd.DataFrame:
    """Return pd.DataFrame summarising trimmomatic output for each run.

    :param dfm:  pd.DataFrame containing one row per sample

    Generates nine new series (columns) for each row in the input
    dataframe corresponding to the trimmomatic summary output for each file
    """
    # Generate series of trimmomatic summary paths and process
    dfm["trim_summary"] = dfm["trimmed_dir"].apply(os.path.join, args=("summary.txt",))
    # Parse summary files into dataframe
    dfm = dfm.apply(parse_trimmomatic_summary, axis=1)
    return dfm


def generate_trimmomatic_commands(dfm: pd.DataFrame, args: Namespace) -> Generator:
    """Return generator of trimmomatic commands.

    :param dfm:  pd.DataFrame containing one row per sample
    :param args:  Namespace of parsed command-line arguments

    Yields command (as List[str]) for each sample, in turn
    """
    cmd_base = ["trimmomatic", "PE", "-threads", args.threads, f"-{args.trim_fastq}"]
    for _, row in dfm.iterrows():
        outdir = Path(row["trimmed_dir"])
        fpath, rpath = Path(row["fwd_read_path"]), Path(row["rev_read_path"])
        paths = [
            fpath,
            rpath,
            outdir / f"{fpath.name}_trimmed.fastq",
            outdir / f"{fpath.name}_untrimmed.fastq",
            outdir / f"{rpath.name}_trimmed.fastq",
            outdir / f"{rpath.name}_untrimmed.fastq",
        ]
        logs = ["-trimlog", outdir / "trimlog.log", "-summary", outdir / "summary.txt"]
        trimmer = [
            f"ILLUMINACLIP:{args.trim_adapters}:2:30:10",
            "SLIDINGWINDOW:5:20",
            "LEADING:5",
            "TRAILING:5",
            "MINLEN:50",
        ]
        yield (
            list(map(str, cmd_base + logs + paths + trimmer)),  # type: ignore
            outdir,
        )


def parse_trimmomatic_summary(dfm: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame modified to include trimmomatic summary output.

    :param dfm:  pd.DataFrame containing one row per sample
    """
    fpath = Path(dfm["trim_summary"])
    with fpath.open("r") as ifh:
        for line in [_.strip() for _ in ifh if _.strip()]:
            key, val = line.split(": ")
            if "." in val:
                dfm[key] = float(val)
            else:
                dfm[key] = int(val)
    return dfm


def run_trimmomatic(dfm: pd.DataFrame, args: Namespace) -> pd.DataFrame:
    """Run trimmomatic on a dataset.

    :param dfm:  pd.DataFrame containing one row per sample
    :param args:  Namespace, parsed command-line arguments

    Returns modified dataframe with the trimmomatic command that was
    applied, and the path to the output directory as new columns
    """
    cmdlist = []
    trimdirs = []
    for cmd, trimdir in tqdm(
        generate_trimmomatic_commands(dfm, args), disable=args.disable_tqdm
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
        trimdirs.append(str(trimdir))

    dfm["trim_cmd"] = cmdlist
    dfm["trim_output"] = trimdirs
    return dfm
