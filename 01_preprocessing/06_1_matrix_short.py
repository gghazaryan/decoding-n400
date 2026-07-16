"""
Obtain data matrices suitable for the zero-shot learning algorithm.

@author: Gayane Ghazaryan

"""

import sys

sys.path.append("..")
import argparse
from config import fname, filter_list
import mne
import numpy as np
import scipy.io
from pathlib import Path
import pandas as pd

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


df_all = pd.read_csv(fname.all_trials_file)[["Word", "Category"]]
df_all.columns = ["target", "category"]
targets = df_all["target"]

position = "target"
highpass, lowpass = filter_list[0]

all_epochs = mne.read_epochs(
    fname.clean_epo_merged_dropbad(
        subject=subject, position=position, highpass=highpass, lowpass=lowpass
    )
)

Path(
    fname.mat(
        subject=subject,
        level="level1",
        highpass=highpass,
        lowpass=lowpass,
        position=position,
    )
).parent.mkdir(parents=True, exist_ok=True)


category_info = []
item_info = []


for level in ["level1", "level2", "level3", "all"]:
    print(level)
    current_level_data = []
    for current_word in targets:
        current_epochs = all_epochs[current_word]
        if level == "all":
            current_evoked = current_epochs.apply_baseline((-0.1, 0)).average()
        else:
            current_evoked = current_epochs[level].apply_baseline((-0.1, 0)).average()

        # crop and resample the data
        current_evoked.crop(0, 1)
        current_evoked.resample(50)

        if level == "level1":
            item_info.append(current_word)
            category_info.append(df_all.query("target==@current_word").category.iloc[0])

        current_level_data.append(current_evoked.data)
    scipy.io.savemat(
        fname.mat(
            subject=subject,
            level=level,
            position=position,
            highpass=highpass,
            lowpass=lowpass,
        ),
        {
            "megdata": np.array(current_level_data),
            "items": np.array(item_info),
            "cat_index": np.array(category_info),
        },
    )


del all_epochs
