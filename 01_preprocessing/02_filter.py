"""
Apply bandpass filters to the data.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import argparse
import mne
from config import fname, filter_list, n_jobs
import matplotlib.pyplot as plt
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


for run in range(1, 5):
    # Load the tSSS transformed data.

    raw = mne.io.read_raw_fif(
        fname.raw(subject=subject, run=run), preload=False, verbose=True
    )

    tsss = mne.io.read_raw_fif(fname.tsss(subject=subject, run=run), preload=True)

    for f in filter_list:
        highpass, lowpass = f
        filtered_data = tsss.copy().filter(
            highpass,
            lowpass,
            l_trans_bandwidth="auto",
            h_trans_bandwidth="auto",
            filter_length="auto",
            phase="zero",
            fir_window="hamming",
            fir_design="firwin",
            n_jobs=n_jobs,
        )

        f_filtered = fname.filtered(
            subject=subject, run=run, highpass=highpass, lowpass=lowpass
        )
        Path(f_filtered).parent.mkdir(parents=True, exist_ok=True)

        filtered_data.save(f_filtered, overwrite=True)

        with mne.open_report(
            fname.report(subject=subject, analysis="preprocessing", step="filter")
        ) as report:
            report.title = f"subject-{subject} filter"

            report.remove(
                title=f"PSD before filtering run-{run}, highpass-{highpass},lowpass-{lowpass}"
            )
            report.add_figure(
                fig=tsss.compute_psd().plot(show=False),
                title=f"PSD before filtering run-{run}, highpass-{highpass},lowpass-{lowpass}",
                image_format="PNG",
                tags=f"run-{run}",
            )
            plt.close()

            report.remove(
                title=f"PSD after filtering run-{run},highpass-{highpass},lowpass-{lowpass}"
            )
            report.add_figure(
                fig=filtered_data.compute_psd().plot(show=False),
                title=f"PSD after filtering run-{run},highpass-{highpass},lowpass-{lowpass}",
                image_format="PNG",
                tags=f"run-{run}",
            )
            plt.close()

report.save(
    fname.report_html(subject=subject, analysis="preprocessing", step="filter"),
    overwrite=True,
    open_browser=False,
)
