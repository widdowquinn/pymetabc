# README.md - `pymetabc`

Lightweight trimming, merging, thresholding and visualisation of metabarcoding reads.

[![CircleCI](https://circleci.com/gh/widdowquinn/pymetabc/tree/master.svg?style=shield)](https://circleci.com/gh/widdowquinn/pymetabc/tree/master)
[![codecov](https://codecov.io/gh/widdowquinn/pymetabc/branch/master/graph/badge.svg)](https://codecov.io/gh/widdowquinn/pymetabc)

[![GitHub Issues](https://img.shields.io/github/issues-closed/widdowquinn/pymetabc.svg)](https://github.com/widdowquinn/pymetabc/issues)
[![GitHub Stars](https://img.shields.io/github/stars/widdowquinn/pymetabc.svg)](https://github.com/widdowquinn/pymetabc/stargazers)

[![CodeFactor](https://www.codefactor.io/repository/github/widdowquinn/pymetabc/badge)](https://www.codefactor.io/repository/github/widdowquinn/pymetabc)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/eee9539a9abc42ae82743ebed31b10c8)](https://www.codacy.com/manual/widdowquinn/pymetabc)

<!-- TOC -->

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Bugs, Issues, Problems, and Questions](#bugs-issues-problems-and-questions)
- [Licence](#licence)
- [Graphical Output](#graphical-output)
    - [`trimmomatic` output summaries](#trimmomatic-output-summaries)
    - [Abundance by unique read](#abundance-by-unique-read)
    - [Read abundance by sample](#read-abundance-by-sample)

<!-- /TOC -->

## Overview

`pymetabc` trims and merges your paired metabarcoding reads, then quantifies unique reads in each sample. It will generate plain text `.tab` TSV output describing samples and their counts of unique merged reads, and interactive graphs showing QC output, and the counts of each unique read. It will use as many CPUs as are available for trimming and merging reads.

## Quick Start

```bash
$ pymetabc -v tests/test_input tests/test_output
[...]
INFO: Stage 1: Process input data
INFO: 	Found 16 samples:
INFO: 		EB_Plate1_1, F1_S1, F1_S16, F1_S44, F2_S25, ...
INFO: Writing input file paths to tests/test_output/01_input_files.tab
INFO: Stage 2: Trim input reads
[...]
INFO: 	Total sample:hash combinations: 17
INFO: 	4 unique hashes survived the threshold
INFO: 	Most abundant thresholded read hashes:
INFO: 		fb474975bd65353181801c5a7b857379: 580011
INFO: 		6fd39f5a082f10a0f0877acc24b45710: 552062
INFO: 		981f24f28919efce3dbbe696697b38d0: 287606
INFO: 		5626d1a71a6c37c32049f427b4fdf70b: 1052
INFO: Plotting read abundance by hash to tests/test_output/05_abundance_by_hash.html
INFO: Plotting read abundance by sample to tests/test_output/05_abundance_by_sample.html
INFO: Completed. time taken: 186.956

$ tree tests/test_output -L 1
tests/test_output
├── 01_input_files.tab
├── 02_summaries.html
├── 02_trimmed
├── 02_trimmed.tab
├── 03_merged
├── 03_merged.tab
├── 04_hashed
├── 04_hashed.tab
├── 05_abundance_by_hash.html
├── 05_abundance_by_sample.html
├── 05_thresholded
├── 05_thresholded.tab
└── 05_thresholded_reads.tab
```

## Bugs, Issues, Problems, and Questions

If wou would like to report a bug or problem with `pymetabc`, or ask a question of the developer(s), please raise an issue at the link below:

- [`pymetabc` Issues page](https://github.com/widdowquinn/pymetabc/issues)

## Licence

`pymetabc` is free software released under the [MIT Licence](https://opensource.org/licenses/MIT). Please see the accompanying `LICENSE` file.

```text
    Author: Leighton Pritchard

    Contact: leighton.pritchard@strath.ac.uk

    Address:
    Leighton Pritchard,
    Strathclyde Institute of Pharmacy and Biomedical Sciences
    161 Cathedral Street
    Glasgow
    G4 0RE,
    Scotland,
    UK

Copyright 2019 University of Strathclyde

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## Graphical Output

`pymetabc` produces interactive graphics using [`bokeh`](https://bokeh.org/) that can be embedded in your own reports.

### `trimmomatic` output summaries

<iframe src="tests/test_targets/02_summaries.html"
    sandbox="allow-same-origin allow-scripts"
    width="100%"
    height="1800"
    scrolling="yes"
    seamless="seamless"
    frameborder="0">
</iframe>

### Abundance by unique read

<iframe src="tests/test_targets/04_abundance_by_hash.html"
    sandbox="allow-same-origin allow-scripts"
    width="100%"
    height="800"
    scrolling="yes"
    seamless="seamless"
    frameborder="0">
</iframe>

### Read abundance by sample

<iframe src="tests/test_targets/05_abundance_by_sample.html"
    sandbox="allow-same-origin allow-scripts"
    width="100%"
    height="800"
    scrolling="yes"
    seamless="seamless"
    frameborder="0">
</iframe>