"""
Use ICA to removed EOG and ECG artifacts from the data.

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


for run in range(1, 5):
    if (subject == 1) & (run == 1):
        run = 2

    ica = mne.preprocessing.read_ica(fname.ica(subject=subject, run=run))

    for f in filter_list:
        highpass, lowpass = f
        filtered_apply = mne.io.read_raw_fif(
            fname.filtered(
                subject=subject, run=run, highpass=highpass, lowpass=lowpass
            ),
            preload=True,
        )

        clean_data = ica.apply(filtered_apply)
        # clean_data.plot(block=True)
        clean_data.save(
            fname.clean(subject=subject, run=run, highpass=highpass, lowpass=lowpass),
            overwrite=True,
        )

    del clean_data, filtered_apply, ica
