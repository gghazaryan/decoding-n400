"""
Forward solution and Inverse operator.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import mne
from config import fname, n_jobs
import argparse
from mne.minimum_norm import make_inverse_operator

# Be verbose
mne.set_log_level("INFO")

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()
subject = args.subject
print("Processing subject:", subject)

if not (args.subject):
    subject = int(input("Enter the value for subject (1,2,3): "))
    mri_check = int(input("Is MRI available for this subject? (1-yes, 0-no): "))

    if not mri_check:
        src_f = fname.src_fsaverage
        bem_f = fname.bem_fsaverage
    else:
        src_f = fname.src(subject=subject)
        bem_f = fname.bem(subject=subject)

else:
    subject = args.subject
    src_f = fname.src(subject=subject)
    bem_f = fname.bem(subject=subject)


highpass = 0.1
lowpass = 40
position = "target"
all_epochs_f = fname.clean_epo_merged_dropbad(
    subject=subject, position=position, highpass=highpass, lowpass=lowpass
)

epochs = mne.read_epochs(all_epochs_f)
# epochs= epochs.pick_types("grad")

fwd = mne.make_forward_solution(
    info=epochs.info,
    trans=fname.trans_coreg(subject=subject),
    src=src_f,
    bem=bem_f,
    meg=True,
    eeg=False,
    n_jobs=n_jobs,
    verbose=True,
    mindist=5.0,
)

mne.write_forward_solution(fname.fwd(subject=subject), fwd, overwrite=True)

noise_cov = mne.compute_covariance(epochs, tmax=0.0)
noise_cov = mne.cov.regularize(noise_cov, epochs.info)
noise_cov.save(fname.noise_cov(subject=subject), overwrite=True)

inverse_operator = make_inverse_operator(
    epochs.info, fwd, noise_cov, loose="auto", depth=0.8
)
mne.minimum_norm.write_inverse_operator(
    fname.inv(subject=subject), inverse_operator, overwrite=True
)
