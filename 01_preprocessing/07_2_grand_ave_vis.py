#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize grand average.


@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import mne
from config import fname, filter_list


highpass, lowpass = filter_list[0]
position = "target"

# %% big_cat
# concrete:0, abstract:1
all_evokeds = {}
for level in ["level1", "level2", "level3"]:
    fname_big_cat = fname.grand_average_big_cat(
        highpass=highpass, lowpass=lowpass, position=position, level=level
    )
    current = mne.read_evokeds(fname_big_cat)
    for idx, i in enumerate(current):
        all_evokeds[f"cat{idx}/{level}"] = current[idx]


mne.viz.plot_compare_evokeds(
    all_evokeds,
    colors=dict(level1="r", level2="b", level3="g"),
    linestyles=dict(cat0="solid", cat1="dashed"),
    axes="topo",
    ylim=dict(grad=[-20, 20]),
)


# %% small_cat
# food:0, animals:1,tools:2,body:3,clothing:4,vehicles:5,plants:6,culture:7,
# time:8, emotions:9, work:10, beliefs:11, characteristics:12, relations:13
all_evokeds = {}
for level in ["level1", "level2", "level3"]:
    fname_small_cat = fname.grand_average_small_cat(
        highpass=highpass, lowpass=lowpass, position=position, level=level
    )
    current = mne.read_evokeds(fname_small_cat)
    for idx, i in enumerate(current):
        all_evokeds[f"cat{idx}/{level}"] = current[idx]

# %%
idx_list = [0, 11]
keys_to_extract = [f"cat{idx}/level{l}" for idx in idx_list for l in range(1, 4)]
small_dict = {key: all_evokeds[key] for key in keys_to_extract if key in all_evokeds}

mne.viz.plot_compare_evokeds(
    small_dict,
    colors=dict(level1="r", level2="b", level3="g"),
    linestyles=dict(cat0="solid", cat11="dashed"),
    axes="topo",
    ylim=dict(grad=[-20, 20]),
)


# %% indiv items
word = "sakset"
all_evokeds = {}
for level in ["level1", "level2", "level3"]:
    fname_items = fname.grand_average_items(
        highpass=highpass, lowpass=lowpass, position=position, level=level
    )
    condition_name = f"{word}/target/{level}/"
    current = mne.read_evokeds(fname_items, condition=condition_name)
    all_evokeds[f"{condition_name}"] = current


mne.viz.plot_compare_evokeds(
    all_evokeds, colors=dict(level1="r", level2="b", level3="g"), axes="topo"
)


# %% all items averaged per level (level check)

all_evokeds = {}
for level in ["level1", "level2", "level3"]:
    fname_items = fname.grand_average_items(
        highpass=highpass, lowpass=lowpass, position=position, level=level
    )
    current = mne.read_evokeds(fname_items)
    all_evokeds[f"{level}"] = mne.grand_average(current)


mne.viz.plot_compare_evokeds(
    all_evokeds,
    colors=dict(level1="r", level2="b", level3="g"),
    axes="topo",
    ylim=dict(grad=[-20, 20]),
)
