#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grand average same head position.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import mne
from config import fname, filter_list
import pandas as pd
from pathlib import Path

highpass, lowpass = filter_list[0]


all_stimuli = pd.read_csv(fname.stimuli_info)
target_cat_combo = all_stimuli[["target", "category", "type"]].drop_duplicates(
    subset="target"
)
sorted_targets = target_cat_combo.sort_values(by=["type", "category"])


def grand_average_evokeds(evoked_dict, fname):
    grand_ave_evokeds_list = []
    for key, value in evoked_dict.items():
        grand_average = mne.grand_average(value)
        grand_average.comment = value[0].comment
        grand_ave_evokeds_list.append(grand_average)
    mne.write_evokeds(fname, grand_ave_evokeds_list, overwrite=True)


for level in ["level1", "level2", "level3"]:
    for position in ["prime1", "prime2", "target"]:
        evokeds_dict_items = {}
        evokeds_dict_small_cat = {}
        evokeds_dict_big_cat = {}
        for subject in range(1, 27):
            if subject in [17]:
                continue

            evokeds_all = mne.read_evokeds(
                fname.ave_indiv_head_same(
                    subject=subject,
                    highpass=highpass,
                    lowpass=lowpass,
                    position=position,
                    level=level,
                )
            )

            for evokeds in evokeds_all:
                evoked_name = evokeds.comment.split("/")[0]
                # individual items
                if evoked_name in evokeds_dict_items.keys():
                    evokeds_dict_items[evoked_name].append(evokeds)
                else:
                    evokeds_dict_items[evoked_name] = [evokeds]

                # small categories (animals,food, etc)
                small_cat = sorted_targets.query("target == @evoked_name")[
                    "category"
                ].values[0]

                if small_cat in evokeds_dict_small_cat.keys():
                    evokeds_dict_small_cat[small_cat].append(evokeds)
                else:
                    evokeds_dict_small_cat[small_cat] = [evokeds]

                # big categories (abstract vs concrete)
                big_cat = sorted_targets.query("target == @evoked_name")["type"].values[
                    0
                ]

                if big_cat in evokeds_dict_big_cat.keys():
                    evokeds_dict_big_cat[big_cat].append(evokeds)
                else:
                    evokeds_dict_big_cat[big_cat] = [evokeds]
            del evokeds_all

        fname_items = fname.grand_average_items(
            highpass=highpass, lowpass=lowpass, position=position, level=level
        )
        fname_small_cat = fname.grand_average_small_cat(
            highpass=highpass, lowpass=lowpass, position=position, level=level
        )
        fname_big_cat = fname.grand_average_big_cat(
            highpass=highpass, lowpass=lowpass, position=position, level=level
        )

        Path(fname_items).parent.mkdir(parents=True, exist_ok=True)

        grand_average_evokeds(evokeds_dict_items, fname_items)
        grand_average_evokeds(evokeds_dict_small_cat, fname_small_cat)
        grand_average_evokeds(evokeds_dict_big_cat, fname_big_cat)

        del evokeds_dict_big_cat, evokeds_dict_small_cat, evokeds_dict_items
