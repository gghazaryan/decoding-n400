"""
Create epochs.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import argparse
import mne
from config import fname, epoch_tmin, epoch_tmax, filter_list
import pandas as pd
import numpy as np


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


event_id_csv = pd.read_csv(fname.event_id_file)
event_ids = event_id_csv.set_index("id")["trigger_code"].to_dict()


all_trials_file = fname.all_trials_file

df_all = pd.read_csv(all_trials_file)
value_map_big_cat = {2: "abstract", 1: "concrete"}

value_map_domain = {0: "taxonomic", 1: "thematic", 2: None}

value_map_dist = {0: 1, 2: 2, 4: 3}

df_all.columns = df_all.columns.str.strip("'\"")

df_all["big_cat"] = df_all["type"].replace(value_map_big_cat)
df_all["domain2"] = df_all["domain"].replace(value_map_domain)
df_all["dist_group"] = df_all["dist_group"].replace(value_map_dist)


df_all["target"] = df_all["target"].str.strip("'")
df_all = df_all.apply(lambda col: col.str.strip("'") if col.dtype == "object" else col)


def read_block(block_example_file):

    with open(block_example_file, "r") as file:
        lines = file.readlines()
        data = []
        for line in lines:
            # Split the line using one or more spaces as the delimiter
            split_line = line.split()
            # Remove any empty strings resulting from multiple spaces in a row
            split_line = [item for item in split_line if item]
            data.append(split_line)

    df_ids = pd.DataFrame(
        data,
        columns=[
            "primer1",
            "primer2",
            "target",
            "target_index",
            "level",
            "block",
            "trigger_combo_p1",
            "trigger_combo_p2",
            "trigger_combo_tagrget",
            "trial_type",
        ],
    )

    return df_ids[["primer1", "primer2", "target", "block", "trial_type", "level"]]


for f in filter_list:
    highpass, lowpass = f

    for run in range(1, 5):
        clean_data = mne.io.read_raw_fif(
            fname.clean(subject=subject, run=run, highpass=highpass, lowpass=lowpass),
            preload=True,
        )

        events = mne.find_events(
            clean_data, stim_channel="STI101", initial_event=True, shortest_event=0.02
        )

        current_event_ids = dict()

        for event in range(len(events)):
            # Check if the item is a value in the dictionary
            if (events[event][2] in event_ids.values()) & (
                events[event][2] not in [512, 1024]
            ):
                # Find the key corresponding to the value
                key = next(
                    key for key, value in event_ids.items() if value == events[event][2]
                )
                # Add the key-value pair to the new dictionary
                current_event_ids[key] = events[event][2]

        # create dirty epochs and save
        clean_epochs = mne.Epochs(
            clean_data,
            events,
            current_event_ids,
            epoch_tmin,
            epoch_tmax,
            baseline=None,
            preload=True,
        )

        # make metadata
        block_example_file = fname.block(run=1)

        current_block_info = read_block(block_example_file)
        current_block_info["target2"] = current_block_info["target"]
        current_block_info2 = pd.melt(
            current_block_info,
            id_vars=["target", "block", "trial_type", "level"],
            var_name="position",
            value_name="word",
        )

        value_map = {"primer1": "prime1", "primer2": "prime2", "target2": "target"}

        current_block_info2["position"] = current_block_info2["position"].replace(
            value_map
        )

        keys_list = list(clean_epochs.event_id.keys())

        df = pd.DataFrame(keys_list, columns=["event_id"])
        df[["target", "position", "level", "random"]] = df["event_id"].str.split(
            "/", expand=True
        )
        df["level"] = df["level"].str.extract("(\d+)", expand=False)

        df.drop(columns="random", inplace=True)

        merged_df = df.merge(current_block_info2, on=["target", "position", "level"])

        #### Changes in this part to get correct domain (iterate through the correct trial rows)
        # In the original version, the same trial would get different domain info values
        index = 0
        while index < len(merged_df):
            # Collect components of the current trial (prime1, prime2, and target)
            prime1_word = None
            prime2_word = None
            target_word = None

            trial_rows = merged_df.iloc[index : index + 3]

            for _, trial_row in trial_rows.iterrows():
                position = trial_row["position"]
                if position == "prime1":
                    prime1_word = trial_row["word"]
                elif position == "prime2":
                    prime2_word = trial_row["word"]
                elif position == "target":
                    target_word = trial_row["word"]

            # Perform the query to find a matching row in df_all
            detailed_query = (
                f"primer1 == @prime1_word & "
                f"primer2 == @prime2_word & "
                f"target == @target_word"
            )

            matching_rows = df_all.query(detailed_query)

            if not matching_rows.empty:
                # Select the first match and update merged_df accordingly
                match_row = matching_rows.iloc[0]
                for trial_index, trial_row in trial_rows.iterrows():
                    word = trial_row["word"]
                    merged_df.at[trial_index, "word_len"] = len(word)
                    merged_df.at[trial_index, "target_small_category"] = str(
                        match_row["category"]
                    )
                    merged_df.at[trial_index, "target_big_category"] = str(
                        match_row["big_cat"]
                    )
                    merged_df.at[trial_index, "trial_domain"] = str(
                        match_row["domain2"]
                    )
                    position = trial_row["position"]
                    if position == "prime1":
                        merged_df.at[trial_index, "word_trans"] = str(
                            match_row["primer1_en"]
                        )
                    elif position == "prime2":
                        merged_df.at[trial_index, "word_trans"] = str(
                            match_row["primer2_en"]
                        )
                    else:
                        merged_df.at[trial_index, "word_trans"] = str(
                            match_row["target_en"]
                        )

            index += 3  # Move to the next block of rows

        values_created = merged_df[["word"]].values.flatten()
        values_expected = current_block_info[
            ["primer1", "primer2", "target"]
        ].values.flatten()
        are_equal = np.all(values_created == values_expected)

        if are_equal:
            print("Generated metadata GOOD")

        clean_epochs.metadata = merged_df
        clean_epochs.save(
            fname.clean_epo_run(
                subject=subject, run=run, highpass=highpass, lowpass=lowpass
            ),
            overwrite=True,
        )

        del clean_epochs
        clean_epochs_long = mne.Epochs(
            clean_data,
            events,
            current_event_ids,
            -0.2,
            2.8,
            baseline=None,
            preload=True,
            reject_by_annotation=None,
        )
        #        print(clean_epochs_long.drop_log)
        clean_epochs_long.metadata = merged_df

        clean_epochs_long["prime1"].save(
            fname.clean_epo_run_long(
                subject=subject, run=run, highpass=highpass, lowpass=lowpass
            ),
            overwrite=True,
        )
        del clean_epochs_long, clean_data
