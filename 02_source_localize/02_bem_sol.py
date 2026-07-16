"""
Source space and BEM model

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import mne
from config import fname
import argparse

# Be verbose
mne.set_log_level("INFO")

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()


# Check if the required arguments are provided
if not (args.subject):
    subject = int(input("Enter the value for subject"))
else:
    subject = args.subject


print("Processing subject:", subject)

freesurfer_dir = fname.freesurfer_subjects_dir


mri_subject = f"sub-{subject:02d}"

model = mne.make_bem_model(
    subject=mri_subject,
    ico=4,
    conductivity=(0.3),
    subjects_dir=fname.freesurfer_subjects_dir,
)

bem = mne.make_bem_solution(model)

mne.write_bem_solution(fname.bem(subject=subject), bem, overwrite=True, verbose=True)
