"""
Source-level comparison.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("../")
import mne
from config import fname
import numpy as np

mne.viz.set_3d_backend("pyvistaqt")
from mne.stats import spatio_temporal_cluster_1samp_test
import pickle


stcs = {}
for level in ["level1", "level2", "level3"]:
    print(level)
    all_subject_stcs = []
    for subject in range(1, 27):
        print(subject)
        if subject not in [17]:
            all_items_stc_morphed = mne.read_source_estimate(
                fname.all_items_stc_morphed(subject=subject, level=level)
            )
            all_subject_stcs.append(all_items_stc_morphed.crop(0.3, 0.5))
    stcs[level] = all_subject_stcs


template_vertices = stcs["level1"][0].vertices


src = mne.read_source_spaces(fname.src_fsaverage)

spatial_adj = mne.spatial_src_adjacency(src)


n_subj = len(stcs["level1"])

pairs = [("level3", "level1"), ("level3", "level2"), ("level2", "level1")]


diff_data = {}
for a, b in pairs:
    # shape: (n_subj, n_vert, n_times)
    X = np.stack([stcs[a][i].data - stcs[b][i].data for i in range(n_subj)], axis=0)
    diff_data[(a, b)] = X


times = stcs["level1"][0].times
_, n_vert, n_times = diff_data[("level3", "level1")].shape


results = {}  # hold stats for each contrast


for (a, b), X in diff_data.items():
    # reshape to (n_subj, n_vert*n_times)
    X_swapped = np.swapaxes(X, 1, 2)

    # Two-sided test around 0 (mean difference = 0)
    T_obs, clusters, cluster_pv, H0 = spatio_temporal_cluster_1samp_test(
        X_swapped,
        adjacency=spatial_adj,
        n_permutations=1000,
        tail=0,
        threshold=2,
        out_type="indices",
        verbose=True,
        n_jobs=14,
        seed=123,
    )
    sig = cluster_pv < 0.05
    avg_data = np.mean(np.mean(X, axis=0), axis=1)
    results[(a, b)] = dict(
        T_obs=T_obs,
        clusters=clusters,
        pvals=cluster_pv,
        sig_mask=sig,
        avg_data=avg_data,
    )


with open("source_level_comp.pkl", "wb") as file:
    pickle.dump(results, file)
