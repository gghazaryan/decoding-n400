#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 10:52:58 2025

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
from config import fname, filter_list
import mne
import numpy as np

import pandas as pd


highpass, lowpass = filter_list[0]
ch_type = "grad"
position = "target"

picks = "grad"
scale = 1e13


def rms_over_channels(ev: mne.Evoked, ch_names):
    chs = [ch for ch in ch_names if ch in ev.ch_names]
    if not chs:
        raise ValueError("None of the requested ROI channels are present.")
    X = ev.copy().pick(chs).get_data()
    y = np.sqrt((X**2).mean(axis=0)) * scale
    return y


rows = []

for level in ["level1", "level2", "level3"]:
    fname_items = fname.grand_average_items(
        highpass=highpass, lowpass=lowpass, position=position, level=level
    )
    current = mne.read_evokeds(fname_items)
    for roi in ["Left-frontal", "Left-temporal", "Left-parietal"]:
        chans = mne.read_vectorview_selection(
            roi, info=current[0].info
        )  # list of ch names for this selection
        chans = [ch for ch in chans if ch in current[0].ch_names]  # keep only present
        for evoked in current:
            name = evoked.comment.split("/")
            item = name[0]
            level = name[2]
            times = evoked.times
            time_ms = (times * 1000).round(3)
            y = rms_over_channels(evoked, chans)
            rows.append(
                pd.DataFrame(
                    {
                        "item": item,
                        "roi": roi,
                        "rms": y,
                        "time": time_ms,
                        "level": level,
                    }
                )
            )
    del current


df_long = pd.concat(rows, ignore_index=True)

# save to CSV (tidy long format)
df_long.to_csv("grandave_evokeds_rms.csv", index=False)
