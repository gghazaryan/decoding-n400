#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check epochs


@author: Gayane Ghazaryan

"""

import mne
from config import fname
import numpy as np

# %%
subject = 26
position = "target"
highpass = 0.1
lowpass = 40

epochs = mne.read_epochs(
    fname.clean_epo_merged_dropbad(
        subject=subject, position=position, highpass=0.1, lowpass=40
    )
)


epochs.plot()

# %%

bad_idx = np.where([(len(r) > 0) and ("IGNORED" not in r) for r in epochs.drop_log])[0]

print("Bad indices:", bad_idx)

# %%
np.savetxt(
    fname.dropbad_list(subject=subject, position=position, highpass=0.1, lowpass=40),
    bad_idx,
    fmt="%d",
)
# %%
epochs.drop_bad()

epochs.drop_log_stats()

# %%
epochs.save(
    fname.clean_epo_merged_dropbad(
        subject=subject, position=position, highpass=highpass, lowpass=lowpass
    ),
    overwrite=True,
)


# %%
del epochs
