#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split matrix.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
from config import fname, filter_list
import scipy.io

highpass, lowpass = filter_list[0]

position = "target"
for ch_type in ["grad"]:
    for level in ["level1", "level2", "level3", "combined"]:
        mat = scipy.io.loadmat(
            fname.mat_average(
                level=level,
                highpass=highpass,
                lowpass=lowpass,
                position=position,
                ch_type=ch_type,
            )
        )

        starts = [5, 15, 25]
        chunks = [mat["megdata"][..., s : s + 10] for s in starts]

        for idx, chunk in enumerate(chunks):
            new_level_name = f"{level}_{idx}"
            print(chunk.shape)
            scipy.io.savemat(
                fname.mat_average(
                    level=new_level_name,
                    highpass=highpass,
                    lowpass=lowpass,
                    position=position,
                    ch_type=ch_type,
                ),
                {
                    "megdata": chunk,
                    "items": mat["items"],
                    "cat_index": mat["cat_index"],
                },
            )
