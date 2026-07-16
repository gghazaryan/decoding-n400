#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract patch indices.

@author: Gayane Ghazaryan
"""

import mne
from config import fname
from scipy.io import loadmat
import mne_rsa
from mne_rsa.source_level import _get_distance_matrix
import pandas as pd

src_to = mne.read_source_spaces(fname.src_fsaverage)
src = mne.add_source_space_distances(src_to)

dist = _get_distance_matrix(src)

test_data = loadmat(fname.average_stc_mat(level="combined", tmin=100, tmax=300))[
    "megdata"
]

sl = mne_rsa.searchlight(shape=test_data[0].shape, dist=dist, spatial_radius=0.02)


patches = [(i, patch[sl.series_dim]) for i, patch in enumerate(sl)]


df = pd.DataFrame(patches, columns=["patch_idx", "vertices_list"])
df["vertices"] = df["vertices_list"].apply(lambda v: ",".join(map(str, v)))
df = df.drop(columns=["vertices_list"])
df.to_csv("../02_decoding/source-level/patches.tsv", sep="\t", index=False)
