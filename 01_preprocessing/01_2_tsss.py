import sys
import argparse

sys.path.append("../")
import mne
from config import fname
import pandas as pd

"""
tSSS


@author: Gayane Ghazaryan

"""

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


# maxfilter the data
fine_cal_file = fname.fine_cal
crosstalk_file = fname.crosstalk
trans_file = fname.raw(subject=subject, run=1)
bad_channel_fname = fname.bad_channels(subject=subject)

mne.set_log_level(verbose="warning")


def get_bad_channels(file_path, subject, run):

    data = pd.read_csv(
        file_path,
    )
    # Query the data
    query_result = data.query("Subject == @subject and Run == @run")
    # Extract and return the bad channels
    if not query_result.empty:
        bad_channels_str = query_result.iloc[0]["BadChannels"]
        bad_channels = bad_channels_str.split()
        return bad_channels
    else:
        return None


for run in range(1, 5):
    tsss_log = fname.tsss_log(subject=subject, run=run)
    Path(tsss_log).parent.mkdir(parents=True, exist_ok=True)

    raw = mne.io.read_raw_fif(
        fname.raw(subject=subject, run=run), preload=True, verbose=True
    )

    subject_info = "_run-" + str(run)

    bad_channels = get_bad_channels(bad_channel_fname, subject, run)

    mne.set_log_file(tsss_log, overwrite=True)

    auto_noisy_chs, auto_flat_chs, auto_scores = (
        mne.preprocessing.find_bad_channels_maxwell(
            raw,
            cross_talk=crosstalk_file,
            calibration=fine_cal_file,
            return_scores=True,
            verbose=True,
        )
    )

    raw.info["bads"] = list(set(bad_channels + auto_noisy_chs + auto_flat_chs))

    print(raw.info["bads"])

    chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw, verbose=True)
    chpi_locs = mne.chpi.compute_chpi_locs(raw.info, chpi_amplitudes, verbose=True)
    head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, verbose=True)

    raw_sss = mne.preprocessing.maxwell_filter(
        raw,
        cross_talk=crosstalk_file,
        calibration=fine_cal_file,
        destination=trans_file,
        st_duration=60,
        head_pos=head_pos,
    )

    tsss_ready = raw_sss.copy()

    tsss_ready.save(fname.tsss(subject=subject, run=run), overwrite=True)

    fig_raw = raw.copy().crop(tmax=60).filter(None, 40)
    fig_tsss_ready = tsss_ready.copy().crop(tmax=60).filter(None, 40)

    Path(
        fname.report_html(subject=subject, analysis="preprocessing", step="tSSS")
    ).parent.mkdir(parents=True, exist_ok=True)

    with mne.open_report(
        fname.report(subject=subject, analysis="preprocessing", step="tSSS")
    ) as report:
        report.title = f"subject-{subject} tSSS"
        report.add_raw(
            raw=fig_raw,
            title=f"Before tsss run-{run}",
            psd=False,
            butterfly=True,
            tags=f"run-{run}",
        )

        report.add_raw(
            raw=fig_tsss_ready,
            title=f"After tsss run-{run}",
            psd=False,
            butterfly=True,
            tags=f"run-{run}",
        )

    report.save(
        fname.report_html(subject=subject, analysis="preprocessing", step="tSSS"),
        overwrite=True,
        open_browser=False,
    )

    del raw, raw_sss, tsss_ready
