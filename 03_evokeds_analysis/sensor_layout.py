#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 11:18:23 2025

@author: Gayane Ghazaryan
"""

import mne
from config import fname
import pandas as pd

highpass = 0.1
lowpass = 40
ch_type = "grad"
position = "target"
level = "level3"

fname_items = fname.grand_average_items(
    highpass=highpass, lowpass=lowpass, position=position, level=level
)
current = mne.read_evokeds(fname_items)

layout = mne.channels.find_layout(current[0].info, ch_type="grad")

xywh = layout.pos  # columns: x, y, width, height
names = layout.names

df2d = pd.DataFrame(
    {
        "ch_name": names,
        "x": xywh[:, 0],
        "y": xywh[:, 1],
        "w": xywh[:, 2],
        "h": xywh[:, 3],
    }
)


df2d.to_csv("grad_layout_2d.csv", index=False)

selections = {
    "roi_left_temporal.txt": mne.read_vectorview_selection("Left-temporal"),
    "roi_left_parietal.txt": mne.read_vectorview_selection("Left-parietal"),
    "roi_left_frontal.txt": mne.read_vectorview_selection("Left-frontal"),
}

selections_clean = {
    roi: [ch.replace(" ", "") for ch in chs] for roi, chs in selections.items()
}

names_all = []
chs = set(current[0].pick("grad").info["ch_names"])
for fname_save, sel in selections_clean.items():
    names = sorted(chs.intersection(sel))
    names_all.append(names)
    with open(fname_save, "w", encoding="utf-8") as f:
        f.write("\n".join(names) + "\n")


# %%

mne.viz.plot_layout(layout, picks=names_all[0], show_axes=False, show=True)

# %%
mne.viz.plot_sensors(current[0].info, kind="topomap", ch_type="grad", show_names=False)
