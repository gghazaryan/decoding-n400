#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract adjacency.

@author: Gayane Ghazaryan
"""

import mne
from config import fname
import pandas as pd
import numpy as np

src_to = mne.read_source_spaces(fname.src_fsaverage)
src = mne.add_source_space_distances(src_to)


adj = mne.spatial_src_adjacency(src)  # sparse
adj = adj.tocoo()


# Edge list
edges = np.c_[adj.row, adj.col]

# drop avoid duplicates
edges = edges[edges[:, 0] < edges[:, 1]]

# ertex numbers on the surface
lh_verts = src[0]["vertno"]
rh_verts = src[1]["vertno"]


vertex_number = np.r_[lh_verts, rh_verts]
hemi = np.array(["lh"] * len(lh_verts) + ["rh"] * len(rh_verts))

edges_df = pd.DataFrame(edges, columns=["from", "to"])

edges_df.to_csv("../02_decoding/source-level/src_edges.csv", index=False)

lh_verts = src[0]["vertno"]
rh_verts = src[1]["vertno"]

vertices_df = pd.DataFrame(
    {
        "idx": np.arange(len(lh_verts) + len(rh_verts)),
        "hemi": ["lh"] * len(lh_verts) + ["rh"] * len(rh_verts),
        "vertex_number": np.r_[lh_verts, rh_verts],
    }
)


vertices_df.to_csv("../02_decoding/source-level/src_vertices.csv", index=False)
