#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check ICA

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
run = 1

dirty = mne.io.read_raw_fif(
    fname.filtered(subject=subject, run=run, highpass=0.1, lowpass=40),
    preload=True,
    verbose=True,
)


clean = mne.io.read_raw_fif(
    fname.clean(subject=subject, run=run, highpass=0.1, lowpass=40),
    preload=True,
    verbose=True,
)

dirty.plot(lowpass=40, highpass=0.1)
clean.plot(lowpass=40, highpass=0.1)


del dirty, clean
