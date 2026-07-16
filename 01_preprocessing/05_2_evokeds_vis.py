"""
Visualize evoked responses.


@author: Gayane Ghazaryan

"""

import sys

sys.path.append("..")
import argparse
import mne
from config import fname, filter_list
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


report_path = fname.report_path


for f in filter_list:
    highpass, lowpass = f

    # position check
    ave_short = mne.read_evokeds(
        fname.ave_positions(subject=subject, highpass=highpass, lowpass=lowpass)
    )

    ave_short = [i.pick("grad") for i in ave_short]
    plt.figure()
    mne.viz.plot_compare_evokeds(
        ave_short,
        ylim=dict(grad=[-50, 50]),
        axes="topo",
        show=False,
        title=f"sub-{subject}-highpass-{highpass}",
    )
    fname_current = (
        f"/{report_path}/sub-{subject:02d}_highpass-{highpass}_wordpos_evokeds.pdf"
    )
    Path(fname_current).parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(fname_current, format="pdf")
    plt.close()

    # taregt short evokeds

    for position in ["prime1", "prime2", "target"]:
        # level check
        ave_list_short = mne.read_evokeds(
            fname.ave_levels(
                subject=subject, highpass=highpass, lowpass=lowpass, position=position
            )
        )

        ave_list_short = [i.pick("grad") for i in ave_list_short]

        plt.figure()
        mne.viz.plot_compare_evokeds(
            ave_list_short,
            ylim=dict(grad=[-30, 30]),
            axes="topo",
            show=False,
            title=f"sub-{subject}-highpass-{highpass}",
        )
        fname_current = f"/{report_path}/sub-{subject:02d}_highpass-{highpass}_{position}-levels_evokeds.pdf"
        plt.savefig(fname_current, format="pdf")
        plt.close()

    # long evokeds
    all_ave_long = mne.read_evokeds(
        fname.ave_long(subject=subject, highpass=highpass, lowpass=lowpass)
    )
    allave_long = [i.pick("grad") for i in all_ave_long]

    plt.figure()
    mne.viz.plot_compare_evokeds(
        all_ave_long, show=False, vlines=[], title=f"sub-{subject}-highpass-{highpass}"
    )

    fname_current = (
        f"/{report_path}/sub-{subject:02d}_highpass-{highpass}_long_evokeds.pdf"
    )
    plt.savefig(fname_current, format="pdf")
    plt.close()

    ave_list_long = mne.read_evokeds(
        fname.ave_long_levels(subject=subject, highpass=highpass, lowpass=lowpass)
    )

    ave_list_long = [i.pick("grad") for i in ave_list_long]

    plt.figure()
    mne.viz.plot_compare_evokeds(
        ave_list_long,
        ylim=dict(grad=[-50, 50]),
        axes="topo",
        show=False,
        title=f"sub-{subject}-highpass-{highpass}",
    )

    fname_current = (
        f"/{report_path}/sub-{subject:02d}_highpass-{highpass}_long-levels_evokeds.pdf"
    )
    plt.savefig(fname_current, format="pdf")
    plt.close()
