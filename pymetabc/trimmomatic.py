# -*- coding: utf-8 -*-
"""Functions for handling trimmomatic."""
import os

import subprocess

from argparse import Namespace
from pathlib import Path
from typing import Generator, List

import pandas as pd

from bokeh.palettes import Category20  # pylint: disable=no-name-in-module
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, save
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


def plot_trimmomatic_summary(
    data: pd.DataFrame, ofname: Path, plot_width: int = 1800, plot_height: int = 280
) -> None:
    """Return bokeh plot of trimmomatic summary data.

    :param dfm:  pd.DataFrame containing one row per sample
    :param ofname;  Path to write HTML bokeh output
    :param plot_width:  int, pixel width of plot
    :param plot_height:  int, pixel height of each plot in the grid

    This returns a gridplot of scatterplots. Each scatterplot represents a
    single measure returned by trimmomatic, for all samples in the dataframe.

    The plots are stacked vertically in column order.

    Plot zooms are linked.
    """
    # Plot summary data
    source = ColumnDataSource(data.sort_values(["sample_name"]))
    figures = []  # type: List
    for colname, color in zip(
        data.loc[:, "Input Read Pairs":"Dropped Read Percent"].columns, Category20[10]
    ):
        # Each plot gets a tooltip showing sample name and plotted value
        tooltips = [("sample", "@sample_name"), ("value", f"@{{{colname}}}")]

        # First figure gets the range definition, all other plots are linked
        # to this, so zooming one zooms all of them.
        if len(figures) != 0:
            fig = figure(
                x_range=figures[0].x_range,
                plot_width=plot_width,
                plot_height=plot_height,
                title=colname,
                tooltips=tooltips,
            )
        else:
            fig = figure(
                x_range=source.data["sample_name"],
                plot_width=plot_width,
                plot_height=plot_height,
                title=colname,
                tooltips=tooltips,
            )

        # Construct scatterplot
        fig.scatter(
            x="sample_name",
            y=colname,
            source=source,
            color=color,
            size=10,
            hover_fill_alpha=1,
            alpha=0.4,
        )
        fig.xaxis.major_label_orientation = "vertical"
        figures.append(fig)

    output_file(ofname)
    save(gridplot([[_] for _ in figures]))


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
