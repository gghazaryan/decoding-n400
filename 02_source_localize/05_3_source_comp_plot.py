"""
Source-level comparison plot.

@author: Gayane Ghazaryan

"""

import sys

sys.path.append("../")
import mne
import numpy as np

mne.viz.set_3d_backend("pyvistaqt")
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.colors import TwoSlopeNorm
import scipy
import pickle
import os

os.environ["SUBJECTS_DIR"] = "data"


template_vertices = [
    np.arange(2562),
    np.arange(2562),
]


names = {
    ("level3", "level1"): "UR-HR",
    ("level3", "level2"): "UR-MR",
    ("level2", "level1"): "MR-HR",
}

DATA_PATH = "data"

with open(f"{DATA_PATH}/source_level_comp.pkl", "rb") as file:
    results = pickle.load(file)


pos_lims = [0, 0.3, 0.6]

fig, axes = plt.subplots(1, 3, figsize=[6, 4.2])
row = 0
column = 0

name_order = []
min_p = []
peaks = []
for a, b in names:
    name_order.append((a, b))
    res = results[(a, b)]

    # add borders for significant clusters
    T_obs, cluster_pv, clusters, avg_data = (
        res["T_obs"],
        res["pvals"],
        res["clusters"],
        res["avg_data"],
    )
    T_obs = np.transpose(T_obs)
    good_cluster_inds = np.where(cluster_pv < 0.05)[0]
    min_p.append(np.min(res["pvals"]))

    stc_avg = mne.SourceEstimate(
        avg_data, vertices=template_vertices, tmin=0.3, tstep=0.001, subject="fsaverage"
    )

    # plot the average STC
    brain = stc_avg.plot(
        background="white",
        hemi="split",
        views="lateral",
        colormap="coolwarm",
        colorbar=False,
        size=(1400, 1000),
        view_layout="horizontal",
        clim=dict(kind="value", pos_lims=pos_lims),
    )

    current_peaks = []

    for cluster_idx in good_cluster_inds:
        lh_n = stc_avg.lh_data.shape[0]

        cluster_time_index, cluster_vertex_index = clusters[cluster_idx]

        time_index, n_vertices = np.unique(
            cluster_time_index,
            return_counts=True,
        )
        time_index = time_index[np.argmax(n_vertices)]

        draw_vertex_index = [
            v
            for v, t in zip(cluster_vertex_index, cluster_time_index)
            if t == time_index
        ]

        verts = np.unique(draw_vertex_index)
        lh = verts[verts < lh_n]
        rh = verts[verts >= lh_n] - lh_n

        if lh.size:
            lab_lh = mne.Label(
                vertices=lh,  # <-- use 'vertices'
                hemi="lh",
                name=f"sig_cluster_{cluster_idx}_lh",
                subject="fsaverage",
            )
            lab_lh = lab_lh.smooth(smooth=5, subject="fsaverage")

            brain.add_label(lab_lh, borders=1, color="white", alpha=1.0)

        if rh.size:
            lab_rh = mne.Label(
                vertices=rh,  # <-- use 'vertices'
                hemi="rh",
                name=f"sig_cluster_{cluster_idx}_rh",
                subject="fsaverage",
            )
            lab_rh = lab_rh.smooth(smooth=5, subject="fsaverage")

            brain.add_label(lab_rh, borders=1, color="white", alpha=1.0)
    peaks.append(current_peaks)

    screenshot = brain.screenshot()
    brain.close()
    nonwhite_pix = (screenshot != 255).any(-1)
    nonwhite_row = nonwhite_pix.any(1)
    nonwhite_col = nonwhite_pix.any(0)
    cropped_screenshot = screenshot[nonwhite_row][:, nonwhite_col]
    axes[column].imshow(cropped_screenshot, interpolation="nearest", resample=False)
    axes[column].aspect = "equal"
    axes[column].set_axis_off()  # hides ticks + labels
    axes[column].set_frame_on(False)  # removes the subplot border (frame)

    title = names[(a, b)]
    axes[column].set_title(title, fontsize=12, pad=6)
    column += 1


vmax = pos_lims[-1]
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
sm = plt.cm.ScalarMappable(cmap=matplotlib.colormaps["coolwarm"], norm=norm)


bbox = mtransforms.Bbox.union([ax.get_position() for ax in axes])
gap = 0.012
cb_h = 0.025
cb_w = 0.45  # width as a fraction of the figure

cax = fig.add_axes(
    [
        bbox.x0 + (bbox.width - cb_w) / 2.0,  # center under all columns
        bbox.y0 - gap - cb_h,  # just below the subplots
        cb_w,
        cb_h,
    ]
)
cb = plt.colorbar(sm, cax=cax, orientation="horizontal")
cb.set_label("dSPM", fontsize=12, labelpad=6)

cb.set_ticks([-vmax, 0, vmax])


fig_w_in = 7.09
cur_w, cur_h = fig.get_size_inches()
fig_h_in = fig_w_in * (cur_h / cur_w)
fig.set_size_inches(fig_w_in, fig_h_in)

fig.savefig("figures/source.pdf", bbox_inches="tight", dpi=300)


scipy.stats.false_discovery_control(min_p)
