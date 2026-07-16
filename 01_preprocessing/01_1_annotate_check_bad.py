"""
Check bad channels.

@author: Gayane Ghazaryan

"""

import sys
import argparse

sys.path.append("../")
import mne
from config import fname
from pathlib import Path


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
bad_channel_fname = fname.bad_channels(subject=subject)
Path(bad_channel_fname).parent.mkdir(parents=True, exist_ok=True)

with open(bad_channel_fname, "w") as f:
    f.write("Subject,Run,BadChannels\n")


def add_bad_channels(file_path, subject, run, bad_channels):
    with open(file_path, "a") as f:
        f.write(f"{subject},{run},{str(bad_channels)}\n")


for run in range(1, 5):
    raw = mne.io.read_raw_fif(
        fname.raw(subject=subject, run=run), preload=True, verbose=True
    )

    annotation_copy = raw.copy()

    fig = annotation_copy.filter(1, 40).plot(block=True)

    if annotation_copy.annotations:
        annotation_copy.annotations.save(
            fname.annotations(subject=subject, run=run), overwrite=True
        )

    bads = input("Bad channels or empty for none (e.g.,2542): ").split(",")

    bads = [f"MEG{s}" for s in bads if s]
    bad_channels = list(set(bads))
    bads = " ".join(bads)

    add_bad_channels(bad_channel_fname, subject, run, bads)
    del raw
