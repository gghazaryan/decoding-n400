"""
Obtain data matrices suitable for the zero-shot learning algorithm.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
from config import fname, filter_list
import mne
import numpy as np
import scipy.io
import pandas as pd


# %%
all_trials_file = fname.all_trials_file

df_all = pd.read_csv(all_trials_file)[["Word", "Category"]]
df_all.columns = ["target", "category"]

highpass, lowpass = filter_list[0]
position = "target"
for ch_type in ["meg", "grad", "mag"]:
    for level in ["level1", "level2", "level3"]:
        item_info = []
        category_info = []
        current_level_data = []
        for index, row in df_all.iterrows():
            word = row["target"]
            cat = row["category"]
            fname_items = fname.grand_average_items(
                highpass=highpass, lowpass=lowpass, position=position, level=level
            )
            condition_name = f"{word}/{position}/{level}/"
            current_evoked = mne.read_evokeds(fname_items, condition=condition_name)

            item_info.append(word)
            category_info.append(cat)

            # crop and resample the data
            current_evoked.crop(0, 1)
            current_evoked.resample(50)

            current_level_data.append(current_evoked.copy().pick(ch_type).data)
            scipy.io.savemat(
                fname.mat_average(
                    level=level,
                    highpass=highpass,
                    lowpass=lowpass,
                    position=position,
                    ch_type=ch_type,
                ),
                {
                    "megdata": np.array(current_level_data),
                    "items": np.array(item_info),
                    "cat_index": np.array(category_info),
                },
            )


# %% concat into one mat for the big model
highpass = 0.1
lowpass = 40
ch_type = "grad"
for ch_type in ["meg", "grad", "mag"]:
    all_levels = []
    for level in ["level1", "level2", "level3"]:
        mat = scipy.io.loadmat(
            fname.mat_average(
                level=level,
                highpass=highpass,
                lowpass=lowpass,
                position=position,
                ch_type=ch_type,
            )
        )
        mat["level"] = np.full((len(mat["items"]),), level)
        all_levels.append(mat)

    combined = {}

    keys = [k for k in all_levels[0].keys() if not k.startswith("__")]

    for key in keys:
        arrays = []
        for d in all_levels:
            arr = d[key]
            # Trim spaces if string arrays
            if arr.dtype.kind in ("U", "S"):
                arr = np.char.strip(arr)
            arrays.append(arr)

        # Stack along rows
        combined[key] = np.concatenate(arrays)

    scipy.io.savemat(
        fname.mat_average(
            level="combined",
            highpass=highpass,
            lowpass=lowpass,
            position=position,
            ch_type=ch_type,
        ),
        combined,
    )
