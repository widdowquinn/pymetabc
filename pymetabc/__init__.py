# -*- coding: utf-8 -*-
"""Package to support metabarcoding read trimmming, merging, and quantitation."""
import os

__version__ = "0.1.0-alpha"

_ROOT = os.path.abspath(os.path.dirname(__file__))
ADAPTER_PATH = os.path.join(_ROOT, "data", "TruSeq3-PE.fa")
