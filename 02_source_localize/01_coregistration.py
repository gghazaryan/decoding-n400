"""
Coregister MRI and MEG.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
from mne.bem import make_scalp_surfaces
from config import fname
import mne


# %%
subject = 26
run = 1
mri_subject = f"sub-{subject:02d}"

# %%

make_scalp_surfaces(
    mri_subject,
    subjects_dir=fname.freesurfer_subjects_dir,
    force=True,
    overwrite=True,
    no_decimate=False,
    threshold=20,
    # mri='T1.mgz',
    mri="T1_smoothed_6.mgz",
    verbose=None,
)


# %%
plot_bem_kwargs = dict(
    subject=mri_subject,
    brain_surfaces="white",
    orientation="coronal",
    src=f"{mri_subject}-ico-4-src.fif",
)


mne.viz.plot_bem(**plot_bem_kwargs)


# %%
meg_inst = fname.tsss(subject=subject, run=run)
trans_coreg = fname.trans_coreg(subject=subject)


info = mne.io.read_info(meg_inst)

# %%

# %% coregister
coreg = mne.gui.coregistration(
    subject=mri_subject,
    subjects_dir=fname.freesurfer_subjects_dir,
    inst=meg_inst,
    trans=None,
    orient_to_surface=True,
    scale_by_distance=True,
)

# %% check coregistration
mne.viz.plot_alignment(
    info,
    trans=fname.trans_coreg(subject=subject),
    subject=mri_subject,
    subjects_dir=fname.freesurfer_subjects_dir,
    surfaces="head-dense",
    show_axes=True,
    dig=True,
    eeg=[],
    meg="sensors",
    coord_frame="meg",
)


# %%
