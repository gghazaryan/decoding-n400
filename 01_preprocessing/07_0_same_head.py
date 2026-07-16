"""
Bring all subjects' heads to the same head position.

@author: Gayane Ghazaryan

"""

import sys

sys.path.append("..")
import subprocess
import argparse
import mne
from config import fname, filter_list
from pathlib import Path
import shutil


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


highpass, lowpass = filter_list[0]

fine_cal_file = fname.fine_cal
crosstalk_file = fname.crosstalk


for position in ["prime1", "prime2", "target"]:
    for level in ["level1", "level2", "level3", "all"]:
        # specify input and output files
        input_file = fname.ave_indiv(
            subject=subject,
            highpass=highpass,
            lowpass=lowpass,
            position=position,
            level=level,
        )

        input_file_project = input_file.replace("scratch", "project")
        Path(input_file_project).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_file, input_file_project)

        output_file = fname.ave_indiv_head_same(
            subject=subject,
            highpass=highpass,
            lowpass=lowpass,
            position=position,
            level=level,
        )
        output_file_project = output_file.replace("scratch", "project")
        Path(output_file_project).parent.mkdir(parents=True, exist_ok=True)

        # bring all subjects evoked data to the same position
        trans_file = fname.ave_indiv(
            subject=13,
            highpass=highpass,
            lowpass=lowpass,
            position=position,
            level=level,
        )

        trans_file_project = trans_file.replace("scratch", "project")
        Path(trans_file_project).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(trans_file, trans_file_project)

        # save the log
        log_file = fname.trans_log(
            subject=subject,
            highpass=highpass,
            lowpass=lowpass,
            level=level,
            position=position,
        )

        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        # run maxfilter
        args = [
            "maxfilter",
            "-f",
            input_file_project,
            "-o",
            output_file_project,
            "-trans",
            trans_file_project,
            "-v",
            "-force",
            "-cal",
            fine_cal_file,
            "-ctc",
            crosstalk_file,
        ]

        with open(log_file, "w") as log_output:
            subprocess.run(args=args, stdout=log_output, stderr=log_output)

        shutil.copy2(output_file_project, output_file)
