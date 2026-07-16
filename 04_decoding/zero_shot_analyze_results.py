"""
Analyze predictions made by the zero-shot learning and write the results to a
CSV file. The file contains the following columns:

subject:
The subject on which the analysis was run.

X and Y:
The categories that are being compared. For example, X='Animal' versus
Y='Tool_Artifact'. For within category comparisons, X and Y are the same, for example
X='Animal' versus Y='Animal'. The X='all' versus Y='all' comparison compares
all words against all words (this would be the overall accuracy and the one you
are probably the most interested in at the moment). There is also X='category'
versus Y='within', which contains the overall within-category accuracy and
there is X='category' versus Y='between', which contains the overall
between-category accuracy.

accuracy:
The mean accuracy for the X versus Y comparison.

iteration:
For the random permutations, this column contains values 1-1000 which
correspond to the iteration which was run.

Author: Marijn van Vliet <marijn.vanvliet@aalto.fi>
"""

import sys
import os
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PARENT_DIR))

import argparse
import os.path as op
from scipy.io import loadmat
import pandas
from pathlib import Path
from zeroshotdecoding import predictions_breakdown
import numpy as np

# Deal with command line arguments
parser = argparse.ArgumentParser(description='Analyze predictions made by the zero-shot learning and write the results to a CSV file.')
parser.add_argument('input_file', nargs='+', type=str, help='The file(s) to use as input; should be (a) .mat file(s).')
parser.add_argument('-o', '--output', metavar='filename', type=str, default='./results.csv', help='The filename to use to write the output; should end in ".csv". Defaults to "./results.csv".')
parser.add_argument('-v', '--verbose', help='Print the stats as they are computed', action='store_true')
args = parser.parse_args()

# Obtain results for all input files
results = []
for i, fname in enumerate(args.input_file, 1):
    m = loadmat(fname, variable_names=['pairwise_accuracies', 'iteration', 'cat_index','target_word_labels'])
    subject = op.basename(fname).split('_')[0]

    category_labels = {}

    cateind = m['cat_index'].ravel()
    
    for idx, i in enumerate(np.unique(cateind)):
        category_labels[idx] = i
    
    new_cateind = []
    for i in cateind:
        for key, value in category_labels.items():
            if value == i:
                new_cateind.append(key)
                
    #print(category_labels)
    cateind=new_cateind
    pairwise_accuracies = m['pairwise_accuracies']

    stimuli=m['target_word_labels'].ravel()

    # Even when not doing time-resolved analysis, add a time dimension to the results
    if pairwise_accuracies.ndim == 2:
        pairwise_accuracies = [pairwise_accuracies]

    # Analyze results for each time point
    for t, acc in enumerate(pairwise_accuracies):
        df = predictions_breakdown(acc, cateind, category_labels,stimuli=stimuli, verbose=args.verbose)
        df['t'] = t
        df['subject'] = subject
        if 'iteration' in m: df['iteration'] = i
        results.append(df.reset_index())

        # Do abstract versus concrete
        
        big_category_labels = {
        'animals        ': 'Concrete',
        'bodyparts      ': 'Concrete',
        'clothing       ': 'Concrete',
        'economic       ': 'Abstract',
        'food           ': 'Concrete',
        'nature         ': 'Concrete',
        'plants         ': 'Concrete',
        'vehicles       ': 'Concrete',
        'characteristics': 'Abstract',
        'culture        ': 'Abstract',
        'emotions       ': 'Abstract',
        'environment    ': 'Abstract',
        'belief         ': 'Abstract',
        'roles          ': 'Abstract',
        'time           ': 'Abstract',
        'tools          ': 'Concrete'
    }
        
        new_cateind = []
        for i in cateind:
            small_cat_label = category_labels[i]
            big_category_label = big_category_labels[small_cat_label]
            if big_category_label == "Concrete":
                new_cateind.append(1)
            else:
                new_cateind.append(2)
                    
        df = predictions_breakdown(
            acc,
            new_cateind,
            {1: 'Concrete', 2: 'Abstract'},
            stimuli=stimuli,
            verbose=args.verbose
        ).iloc[[1, 2, 3], :]
        df['t'] = t
        df['subject'] = subject
        if 'iteration' in m: df['iteration'] = i
        results.append(df.reset_index())

# Collect all the results in one big table
results = pandas.concat(results, ignore_index=True)

# Set the proper index, based on whether we are analyzing real data or random
# permutations.
if 'iteration' in results:
    results = results.set_index(['iteration', 'X', 'Y', 't'])
else:
    results = results.set_index(['subject', 'X', 'Y', 't'])

# Save the table
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
results.to_csv(args.output)
