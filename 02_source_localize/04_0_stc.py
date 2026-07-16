"""
Make stcs.

@author: Gayane Ghazaryan

"""

import sys

sys.path.append("..")
import mne
from config import fname
import argparse
from pathlib import Path


# Be verbose
mne.set_log_level("INFO")

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()
subject = args.subject
print("Processing subject:", subject)


if not (args.subject):
    subject = int(input("Enter the value for subject (1,2,3): "))

else:
    subject = args.subject


position = "target"
highpass = 0.1
lowpass = 40
all_epochs_f = fname.clean_epo_merged_dropbad(
    subject=subject, position=position, highpass=highpass, lowpass=lowpass
)

all_epochs = mne.read_epochs(all_epochs_f)


# EVOKED
inverse_operator = mne.minimum_norm.read_inverse_operator(fname.inv(subject=subject))


for level in ["level1", "level2", "level3", "all"]:
    if level == "all":
        epochs = all_epochs
        all_items_ev = epochs.average().apply_baseline((-0.1, 0))
    else:
        epochs = all_epochs[level]
        all_items_ev = epochs.average().apply_baseline((-0.1, 0))

    all_items_stc = mne.minimum_norm.apply_inverse(
        all_items_ev, inverse_operator, method="dSPM"
    )

    Path(fname.all_items_stc(subject=subject, level=level)).parent.mkdir(
        parents=True, exist_ok=True
    )

    all_items_stc.save(
        fname.all_items_stc(subject=subject, level=level), overwrite=True
    )

    items = epochs.event_id

    for item in items:
        print(item)

        current = epochs[item].average().apply_baseline((-0.1, 0))
        stc = mne.minimum_norm.apply_inverse(
            current, inverse_operator, method="dSPM", pick_ori="normal"
        )
        item = item.split("/")[0]

        stc_f = fname.indiv_item_stc(item=item, subject=subject, level=level)
        Path(stc_f).parent.mkdir(parents=True, exist_ok=True)
        stc.save(stc_f, overwrite=True)
        del stc, current

del all_items_stc, inverse_operator, all_epochs
