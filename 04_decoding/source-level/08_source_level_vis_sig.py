#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 15:22:36 2026

@author: ghazarg1
"""

import pandas as pd
import numpy as np
import mne
import matplotlib.pyplot as plt
import matplotlib
import os

os.environ["SUBJECTS_DIR"] = "data"
src = mne.read_source_spaces("data/fsaverage-ico4-src.fif")

DATA_PATH = "data"
all_levels_df = pd.read_csv(f"{DATA_PATH}/source_decoding_all_merged.csv")

unique_pairs = all_levels_df[["X", "Y"]].drop_duplicates()
allowed = ["all"]

mask = unique_pairs[["X", "Y"]].isin(allowed).any(axis=1)
unique_pairs = unique_pairs[mask]


times = [[100, 300], [300, 500], [500, 700]]
lims = [50, 60, 70]

level_names = ["HR", "MR", "UR"]


levels = all_levels_df.level.unique()
n_levels = len(levels)
n_timepoints = len(times)


for row in unique_pairs.itertuples(index=False):
    fig, axes = plt.subplots(
        n_levels,
        n_timepoints,
        figsize=(4 * n_timepoints, 2 * n_levels),  # auto-sized figure
    )

    # If only 1 row/column, keep axes 2D
    if n_levels == 1:
        axes = np.expand_dims(axes, axis=0)
    if n_timepoints == 1:
        axes = np.expand_dims(axes, axis=1)

    cat1 = row.X
    cat2 = row.Y

    stats_df_all = pd.read_csv(f"data/source_stats_{cat1}-{cat2}_results.csv")
    stats_df = stats_df_all.query("pval<0.05")

    current_comp_df = all_levels_df.query("X==@cat1 and Y == @cat2")

    colnum = pd.to_numeric(current_comp_df.columns, errors="coerce")
    mask = (colnum >= 0) & (colnum <= 5123)
    range_df = current_comp_df.loc[:, mask]

    mx = range_df.to_numpy().max() * 100

    lims = [50, 60, int(mx)]

    # -----------------------------------------
    # PLOT LOOP
    # -----------------------------------------
    for row, level in enumerate(levels):
        for column, t in enumerate(times):
            tmin, tmax = t
            current_level_df = current_comp_df.query(
                "level==@level and tmin==@tmin and tmax==@tmax"
            )
            current_stats_df = stats_df.query(
                "test_level==@level and tmin==@tmin and tmax==@tmax"
            )
            current_level_df = current_level_df.loc[:, mask]

            acc = current_level_df.to_numpy()[0] * 100

            stc = mne.SourceEstimate(
                data=acc[:, np.newaxis],
                vertices=[src[0]["vertno"], src[1]["vertno"]],
                tmin=0.0,
                tstep=1.0,
            )

            brain = stc.plot(
                subject="fsaverage",
                background="white",
                hemi="split",
                views=["lateral"],
                colormap="magma",
                colorbar=False,
                size=(900, 450),
                view_layout="vertical",
                clim=dict(kind="value", lims=lims),
                show_traces=False,
            )

            lh_n = stc.lh_data.shape[0]

            for row_s in current_stats_df.itertuples(index=False):
                verts = row_s.verts
                verts = np.array([int(i) for i in verts.split(",")])
                verts = np.sort(verts)

                if np.max(verts) <= lh_n:
                    hemi = "lh"
                else:
                    hemi = "rh"
                    verts = verts - lh_n

                lab = mne.Label(
                    vertices=verts,  # <-- use 'vertices'
                    hemi=hemi,
                    subject="fsaverage",
                )
                lab = lab.smooth(smooth=5, subject="fsaverage")

                brain.add_label(lab, borders=1, color="white", alpha=1.0)

            # Screenshot and crop
            screenshot = brain.screenshot()
            brain.close()

            nonwhite = (screenshot != 255).any(-1)
            cropped = screenshot[nonwhite.any(1)][:, nonwhite.any(0)]

            ax = axes[row, column]
            ax.imshow(cropped, interpolation="nearest", resample=False)

            # Hide ticks but keep ylabel and titles
            ax.set_xticks([])
            ax.set_yticks([])
            # ax.set_frame_on(False)

            p_fdr = current_stats_df["p_fdr"].min()
            pval = current_stats_df["pval"].min()

            p_fdr = 0  # no red square
            # keep frame ON and style spines
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)
                spine.set_edgecolor("red" if ((p_fdr > 0.05) & (pval < 0.05)) else None)

            # Column titles: timepoints
            if row == 0:
                time_name = t
                ax.set_title(f"{time_name[0]}-{time_name[1]} ms", fontsize=20, pad=6)

            # Row labels: levels
            if column == 0:
                level_name = level_names[row]
                ax.set_ylabel(
                    level_name, fontsize=20, rotation=90, labelpad=25, va="center"
                )

    # -----------------------------------------
    # COLORBAR
    # -----------------------------------------

    maxval = lims[-1]
    norm = matplotlib.colors.Normalize(vmin=lims[0], vmax=maxval)
    sm = plt.cm.ScalarMappable(cmap="magma", norm=norm)

    # Place colorbar centered under the entire grid
    fig.subplots_adjust(bottom=0.12)
    cax = fig.add_axes(
        [
            0.5 - 0.17,  # center
            0.1,  # vertical offset
            0.34,  # width
            0.02,  # height
        ]
    )

    cb = mne.viz.plot_brain_colorbar(
        ax=cax,
        clim=dict(kind="value", lims=lims),
        colormap="magma",
        transparent=True,
        orientation="horizontal",
        bgcolor="0.7",
    )

    # tick numbers
    cb.ax.tick_params(labelsize=20)

    # colorbar label
    cb.set_label("Accuracy", fontsize=20)
    fig.tight_layout(rect=[0, 0.1, 1, 1])

    fig.savefig(
        f"figures/source_decoding_{cat1}-{cat2}.pdf", bbox_inches="tight", dpi=300
    )
    plt.close(fig)
