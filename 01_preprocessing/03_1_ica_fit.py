#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Use ICA to removed EOG and ECG artifacts from the data.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import argparse
import mne
from mne.preprocessing import ICA, create_ecg_epochs, create_eog_epochs
from config import fname, n_jobs
import pandas as pd
import os
from pathlib import Path


# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()

# Check if the required arguments are provided
if not (args.subject):
    subject = int(input("Enter the value for subject: "))

else:
    subject = args.subject

print("Processing subject:", subject)


def get_bad_components(file_path, subject, run):

    data = pd.read_csv(
        file_path,
    )
    print(data)
    # Query the data
    query_result = data.query("Subject == @subject and Run == @run")
    # Extract and return the bad componenets
    if not query_result.empty:
        bad_componenets_str = query_result.iloc[0]["BadComp"]
        bad_componenets = bad_componenets_str.split()
        return bad_componenets
    else:
        print("No componenets")
        return None


def add_bad_comp(file_path, subject, run, bad_comp):
    with open(file_path, "a") as f:
        f.write(f"{subject},{run},{str(bad_comp)}\n")


n_components = 0.95
bad_comp_fname = fname.components(subject=subject)


for run in range(1, 5):
    if os.path.exists(bad_comp_fname):
        components = get_bad_components(bad_comp_fname, subject, run)

    else:
        components = None  # None indicates no information is available
        Path(bad_comp_fname).parent.mkdir(parents=True, exist_ok=True)
        with open(bad_comp_fname, "w") as f:
            f.write("Subject,Run,BadComp\n")

    if components is None:
        print("No information available.")

        # eog channels not recorded in this block, second block ica will be used
        if (subject == 1) & (run == 1):
            continue

        filtered_fit = mne.io.read_raw_fif(
            fname.filtered(subject=subject, run=run, highpass=1, lowpass=40),
            preload=True,
        )

        # annotated segments rejected when fitting ica
        if os.path.exists(fname.annotations(subject=subject, run=run)):
            annot_from_file = mne.read_annotations(
                fname.annotations(subject=subject, run=run)
            )
            filtered_fit.set_annotations(annot_from_file)

        ica = ICA(method="fastica", random_state=42, n_components=n_components)
        ica.fit(
            filtered_fit,
            decim=5,
            reject_by_annotation=True,
        )

        print(
            "Fit %d components (explaining at least %0.1f%% of the variance)"
            % (ica.n_components_, 100 * n_components)
        )

        # ica done manually but automatic detection is used as suggestions
        eog_indices, eog_scores = ica.find_bads_eog(
            filtered_fit,
            reject_by_annotation=True,
        )
        ecg_indices, ecg_scores = ica.find_bads_ecg(
            filtered_fit,
            method="correlation",
            threshold="auto",
            reject_by_annotation=True,
        )

        components = eog_indices + ecg_indices

        eog_evoked = create_eog_epochs(filtered_fit).average()
        eog_evoked.apply_baseline(baseline=(None, -0.2))
        ecg_evoked = create_ecg_epochs(filtered_fit).average()
        ecg_evoked.apply_baseline(baseline=(None, -0.2))

        # print suggested bad componenets
        print(components)

        ica.plot_sources(filtered_fit, show_scrollbars=True, block=True)

        manual = input("Bad componenets: ").split(",")
        manual = [int(i) for i in manual]
        ica.exclude = list(set(manual))
        properties = ica.plot_properties(filtered_fit, picks=ica.exclude)

        # save files
        ica.save(fname.ica(subject=subject, run=run), overwrite=True)
        save = " ".join([str(i) for i in ica.exclude])
        add_bad_comp(bad_comp_fname, subject, run, save)

        with mne.open_report(
            fname.report(subject=subject, analysis="preprocessing", step="ICA")
        ) as report:
            report.title = f"subject-{subject} ICA"

            report.remove(title=f"ICA cleaning run-{run}")
            report.add_ica(
                ica=ica,
                title=f"ICA cleaning run-{run}",
                picks=ica.exclude,
                inst=filtered_fit,
                eog_evoked=eog_evoked,
                eog_scores=eog_scores,
                ecg_evoked=ecg_evoked,
                ecg_scores=ecg_scores,
                tags=f"run-{run}",
                n_jobs=n_jobs,
            )

        report.save(
            fname.report(subject=subject, analysis="preprocessing", step="ICA"),
            overwrite=True,
        )
        report.save(
            fname.report_html(subject=subject, analysis="preprocessing", step="ICA"),
            overwrite=True,
            open_browser=False,
        )

        del filtered_fit

    else:
        print(f"Recorded bad componenets: {components}")
