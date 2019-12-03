# _*_ coding: utf-8 -*-
"""Module providing plotting functions."""

from pathlib import Path

import pandas as pd

from bokeh.palettes import Category20  # pylint: disable=no-name-in-module
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, HoverTool, Legend, LegendItem
from bokeh.plotting import figure, output_file, save
from bokeh.transform import factor_cmap, jitter


def plot_read_hash_abundances(dfm: pd.DataFrame, ofname: Path) -> None:
    """Plot distribution of unique read counts.

    :param dfm:  pd.DataFrame containing one row per sample/hash combination
    :param ofname:  Path to output file for figure
    """
    # Set data sources
    dfm["read_hash"] = dfm["read_hash"].str.slice(0, 6)
    source = ColumnDataSource(dfm)
    categories = sorted(set(source.data["read_hash"]))
    colours = factor_cmap(
        "read_hash", palette=Category20[len(categories)], factors=categories
    )

    # Render abundances
    tooltips = [("sample", "@sample_name"), ("abundance", "@abundance")]
    fig = figure(
        x_range=categories,
        plot_width=100 * len(categories),
        plot_height=600,
        title="Unique Read Abundances By Hash",
        y_axis_type="log",
        tooltips=tooltips,
    )
    fig.scatter(
        x=jitter("read_hash", width=0.4, range=fig.x_range),
        y="abundance",
        source=source,
        size=10,
        alpha=0.6,
        hover_fill_alpha=1,
        fill_color=colours,
    )

    # Save figure
    output_file(ofname)
    save(fig)


def plot_sample_hash_abundances(
    data: pd.DataFrame, ofname: Path, plot_width: int = 1800, plot_height: int = 600
) -> None:
    """Render bokeh plot of unique read hash abundance in each sample."""
    # Set data sources
    data["read_hash"] = data["read_hash"].str.slice(0, 6)
    data = data.reset_index(level=0)
    source = ColumnDataSource(data)
    categories = sorted(set(source.data["read_hash"]))
    sample_names = sorted(set(source.data["sample_name"]))

    # HoverTool tooltip
    hover = HoverTool(
        tooltips=[
            ("sample", "@sample_name"),
            ("read hash", "@read_hash"),
            ("abundance", "@abundance"),
        ]
    )

    # Render abundances
    fig = figure(
        x_range=sample_names,
        plot_width=plot_width,
        plot_height=plot_height,
        title="Unique Read Abundance by Sample",
        y_axis_type="log",
        tools=[hover, "tap", "box_zoom", "wheel_zoom", "save", "reset"],
    )
    legend_items = []  # holds LegendItems
    for rhash, color in zip(categories, Category20[len(categories)]):
        dfm = data.loc[data["read_hash"] == rhash]
        rdr = fig.circle(
            "sample_name",
            "abundance",
            size=10,
            alpha=0.7,
            hover_fill_alpha=1,
            fill_color=color,
            muted_color=color,
            muted_alpha=1,
            source=dfm,
        )
        legend_items.append(LegendItem(label=rhash, renderers=[rdr]))

    # Configure plot
    fig.xaxis.major_label_orientation = "vertical"
    legend = Legend(items=legend_items, location=(0, 0))
    legend.click_policy = "mute"
    fig.add_layout(legend, "left")

    #  Save file
    output_file(ofname)
    save(fig)


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
    figures = list()  # type: ignore
    for colname, color in zip(
        data.loc[:, "Input Read Pairs":"Dropped Read Percent"].columns,  # type: ignore
        Category20[10],
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
