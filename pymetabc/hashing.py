# -*- coding: utf-8 -*-
"""Functions to hash and quantify merged reads."""

import hashlib

from argparse import Namespace
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Generator, List

import pandas as pd

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from tqdm import tqdm


def add_hashed_reads(dfm: pd.DataFrame, args: Namespace) -> Generator:
    """Generate one output directory per sample under the root directory.

    :param dfm:  pd.DataFrame containing one row per sample
    :param args:  Namespace of parsed command-line options

    Yields path (as str) to the directory
    """
    for _, row in tqdm(
        dfm.iterrows(), disable=args.disable_tqdm
    ):  # one subdirectory per sample
        readfile = list(Path(row["merged_dir"]).glob("*.extendedFrags.fastq"))[0]
        ofname = (args.hashdir / readfile.name).with_suffix(".fasta")
        if not args.dryrun:
            hashed_reads = fastq_to_hash_abundance(readfile)
            SeqIO.write(hashed_reads, ofname, "fasta")
        yield str(ofname)


def count_unique_hashes(indir: Path) -> Dict:
    """Return a Dict of counts keyed by hash for merged reads in the passed directory.

    :param indir:  Path to directory containing FASTA files of merged, hashed reads

    Does not return counts of reads with abundance equal to 1
    """
    hashdict = defaultdict(int)  # type: Dict[str, int]
    for fname in indir.iterdir():
        with fname.open("r") as ifh:
            for seqdata in SeqIO.parse(ifh, "fasta"):
                hsh, cnt = seqdata.id.split("_")
                hashdict[hsh] += int(cnt)
    return hashdict


def fastq_to_hash_abundance(fpath: Path) -> List[Any]:
    """Return a list of deduplicated FASTA sequences from FASTQ input.

    :param fpath:  Path to FASTQ input file

    Load the passed FASTQ file and return a list of nonredundant
    FASTA sequences, whose IDs are the MD5 hash of the sequence,
    and the abundance of that sequence in the original file.
    """
    with fpath.open("r") as ifh:
        counter = Counter((str(_.seq.upper()) for _ in SeqIO.parse(ifh, "fastq")))
    hashed = []
    for key, val in counter.items():
        hashid = hashlib.md5(key.encode("ascii")).hexdigest()
        hashed.append(SeqRecord(id=f"{hashid}_{val}", seq=Seq(key)))
    return hashed


def get_hashes_by_sample(indir: Path, args: Namespace) -> pd.DataFrame:
    """Return pandas DataFrame in tidy format with read hash and abundance by sample.

    :param indir:  Path to input directory of hashed read files
    :param args:  Namespace of parsed command-line options
    """
    data = list()
    for ifname in tqdm(indir.iterdir(), disable=args.disable_tqdm):
        if ifname.suffix == ".fasta":
            fstem = ifname.stem.split("_")[0]
            with ifname.open("r") as ifh:
                for read in SeqIO.parse(ifh, "fasta"):
                    rhash, abundance = read.id.split("_")
                    data.append((fstem, rhash, int(abundance)))
    return pd.DataFrame(
        data, columns=["sample_name", "read_hash", "abundance"]
    ).set_index("sample_name")
