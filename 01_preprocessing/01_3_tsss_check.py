#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check tSSS

@author: Gayane Ghazaryan
"""

import sys
import argparse

sys.path.append("../")
import mne
from config import fname


# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()

# Check if the required arguments are provided
if not (args.subject):
    subject = int(input("Enter the value for subject: "))

else:
    subject = args.subject

print("Processing subject:", subject)

# %%
run = 2
raw = mne.io.read_raw_fif(
    fname.raw(subject=subject, run=run), preload=True, verbose=True
)

tsss = mne.io.read_raw_fif(
    fname.tsss(subject=subject, run=run), preload=True, verbose=True
)

raw.plot(lowpass=40, highpass=0.1)
tsss.plot(lowpass=40, highpass=0.1)


del raw, tsss
