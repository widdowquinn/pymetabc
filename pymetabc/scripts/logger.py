# -*- coding: utf-8 -*-
"""Module providing logger convenience functions."""

import logging
import sys
import time

from argparse import Namespace
from pathlib import Path


def build_logger(name: str, args: Namespace) -> logging.Logger:
    """Return a logging.Logger object to use in the script.

    :param name:  str, name for logger
    :param args:  Namespace, parsed command-line arguments

    Instantiate a logger for the script, and add basic info.
    """
    # Instantiate the logger with DEBUG logging level
    logger = logging.getLogger(f"{name}: {time.asctime}")
    logger.setLevel(logging.DEBUG)

    # Stream errors to sys.stderr and format as LEVEL: MSG
    err_handler = logging.StreamHandler(sys.stderr)
    err_formatter = logging.Formatter("%(levelname)s: %(message)s")
    err_handler.setFormatter(err_formatter)

    # If user selects verbose report INFO, otherwise WARNING
    if args.verbose:
        err_handler.setLevel(logging.INFO)
    else:
        err_handler.setLevel(logging.WARNING)
    logger.addHandler(err_handler)

    # If a logfile output path was specified, use it
    if args.logfile is not None:
        # Check that parent directory exists and create if not
        logdir = Path(str(args.logfile.parents))
        try:
            if logdir != Path.cwd():
                logdir.mkdir(exist_ok=True)
            logstream = args.logfile.open("w")
        except OSError:
            logger.error("Could not open %s for logging", args.logfile, exc_info=True)
            raise SystemExit(1)

        # Add logging output file to error handler
        err_handler_file = logging.StreamHandler(logstream)
        err_handler_file.setFormatter(err_formatter)
        err_handler_file.setLevel(logging.INFO)
        logger.addHandler(err_handler_file)

    # Report arguments to logger for diagnosis
    args.cmdline = " ".join(sys.argv)
    logger.info("Processed arguments: %s", args)
    logger.info("command-line: %s", args.cmdline)

    return logger
