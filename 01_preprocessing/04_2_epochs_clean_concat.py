"""
Concatenate epochs.


@author: Gayane Ghazaryan

"""

import sys

sys.path.append("..")
import argparse
import mne
from config import fname, filter_list


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


for f in filter_list:
    highpass, lowpass = f
    all_epochs = []

    for run in range(1, 5):
        # fname.clean_epo_run_long
        epochs = mne.read_epochs(
            fname.clean_epo_run(
                subject=subject, run=run, highpass=highpass, lowpass=lowpass
            )
        )
        epochs.pick_types(meg=True)

        all_epochs.append(epochs)
        del epochs

    all_epochs = mne.concatenate_epochs(all_epochs)

    for position in ["prime1", "prime2", "target"]:
        print(position)
        print(
            fname.clean_epo_merged(
                subject=subject, position=position, highpass=highpass, lowpass=lowpass
            )
        )
        all_epochs[position].save(
            fname.clean_epo_merged(
                subject=subject, position=position, highpass=highpass, lowpass=lowpass
            ),
            overwrite=True,
        )

    del all_epochs

# =============================================================================
# # long epochs
# for f in filter_list:
#
#     highpass,lowpass = f
#     all_epochs = []
#
#     for run in range(1, 5):
#         #fname.clean_epo_run_long
#         epochs = mne.read_epochs(fname.clean_epo_run_long(subject=subject,run=run,highpass=highpass,lowpass=lowpass))
#         epochs.pick_types(meg=True).crop(-0.2,3)
#
#         all_epochs.append(epochs)
#         del epochs
#
#     all_epochs = mne.concatenate_epochs(all_epochs)
#
#     for position in ['prime1']:
#         all_epochs[position].save(fname.clean_epo_merged_long(subject = subject,position=position,
#                                                               highpass=highpass,lowpass=lowpass),overwrite=True)
#
#     del all_epochs
# =============================================================================

# =============================================================================
# with mne.open_report(fname.report(subject=subject,analysis="preprocessing",step="clean_epochs")) as report:
#       report.title = f"subject-{subject} Clean Epochs"
#
#       report.add_epochs(epochs=all_epochs, title='All clean epochs')
#
#
#
# report.save(fname.report(subject=subject,analysis="preprocessing",step="clean_epochs"), overwrite=True)
# report.save(fname.report_html(subject=subject,analysis="preprocessing",step="clean_epochs"), overwrite=True, open_browser=False)
# =============================================================================
