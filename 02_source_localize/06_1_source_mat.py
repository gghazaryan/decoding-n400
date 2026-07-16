"""
Source-localized matrix

@author: Gayane Ghazaryan
"""

import mne
from config import fname
import numpy as np
import pandas as pd
import scipy


df_all = pd.read_csv(fname.all_trials_file)[["Word", "Category"]]
df_all.columns = ["target", "category"]
time_wins = [(100, 300), (300, 500), (500, 700)]
levels = ["level1", "level2", "level3"]

for level in levels:
    stcs_by_win = [[] for _ in time_wins]
    item_info = []
    cat_info = []

    for index, row in df_all.iterrows():
        item = row["target"]
        cat = row["category"]

        item_info.append(item)
        cat_info.append(cat)

        stc = mne.read_source_estimate(fname.item_average_stc(item=item, level=level))

        for w_idx, (tmin, tmax) in enumerate(time_wins):
            stcs_by_win[w_idx].append(
                stc.copy().crop(tmin / 1000, tmax / 1000).resample(50).data
            )

        del stc

    for w_idx, (tmin, tmax) in enumerate(time_wins):
        arr = np.array(stcs_by_win[w_idx])
        out_fname = fname.average_stc_mat(level=level, tmin=tmin, tmax=tmax)
        scipy.io.savemat(
            out_fname,
            {
                "megdata": arr,
                "items": np.array(item_info),
                "cat_index": np.array(cat_info),
            },
        )

        del arr

    del stcs_by_win


# concat levels into a singe file per findow
for tmin, tmax in time_wins:
    meg_list = []

    for level in levels:
        d = scipy.io.loadmat(fname.average_stc_mat(level=level, tmin=tmin, tmax=tmax))
        meg_list.append(d["megdata"])

    megdata = np.concatenate(meg_list, axis=0)

    items = np.tile(d["items"], len(levels))
    cats = np.tile(d["cat_index"], len(levels))

    scipy.io.savemat(
        fname.average_stc_mat(tmin=tmin, tmax=tmax, level="combined"),
        {"megdata": megdata, "items": items, "cat_index": cats},
    )
