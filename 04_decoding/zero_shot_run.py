from __future__ import print_function

import sys
import argparse
from scipy.io import loadmat, savemat
import os
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PARENT_DIR))
from zeroshotdecoding import zero_shot_decoding_tc
from pathlib import Path
import numpy as np

norm_file = 'data/target_vectors.mat'

# Handle command line arguments
parser = argparse.ArgumentParser(description='Run zero-shot learning.')

parser.add_argument('input_file', type=str,
                    help='The file that contains the subject data; should be a .mat file.')
parser.add_argument('-input_file2', metavar='filename',type=str,
                    help='The file that contains the test subject data (if different from training); should be a .mat file.')
parser.add_argument('-i', '--subject-id', metavar='N', type=int, default=1,
                    help='The subject-id (as a number). This number is recorded in the output .mat file. Defaults to 1.')
parser.add_argument('-o', '--output', metavar='filename', type=str, default='./results.mat',
                    help='The file to write the results to; should end in .mat. Defaults to ./results.mat.')
parser.add_argument('-n', '--norms', metavar='filename', type=str, default=norm_file,
                    help='The file that contains the norm data. Defaults to %s.' % norm_file)
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Whether to show a progress bar')
parser.add_argument('-b', '--break-after', metavar='N', type=int, default=-1,
                    help='Break after N iterations (useful for testing)')
parser.add_argument('-d', '--distance-metric', type=str, default='sqeuclidean',
                    help=("The distance metric to use. Any distance implemented in SciPy's "
                          "spatial.distance module is supported. See the docstring of "
                          "scipy.spatial.distance.pdict for the exhaustive list of possitble "
                          "metrics. Here are some of the more useful ones: "
                          "'euclidean' - Euclidean distance "
                          "'sqeuclidean' - Squared euclidean distance (the default) "
                          "'correlation' - Pearson correlation "
                          "'cosine' - Cosine similarity "))
parser.add_argument('-tr', '--time-resolved', metavar='N', type=int, default=-1,
                    help='When set, decoding is performed in a time-resolved manner using a sliding window of size N.')
parser.add_argument('-p','--permutation', help="permutation id", type=int, default = -1)
parser.add_argument('-tc','--temporal-cross', help="index for training time",type=int, default = -1)
parser.add_argument('-verts', help='Vertex indices to process',default=None) 



args = parser.parse_args()
verbose = args.verbose

if args.break_after > 0:
    break_after = args.break_after
else:
    break_after = None

print('Subject:', args.subject_id)
print('Input:', args.input_file)
print('Norms:', args.norms)


if args.time_resolved != -1:
    print('Performing time-resolved analysis')

if args.temporal_cross != -1:
    print('Performing temporal cross decoding')
    
if args.permutation != -1:
    np.random.seed(args.permutation)

perm = (args.permutation != -1)

print('Output:', args.output)

# Load MEG data

def load_brain_data(filename,perm):
    m = loadmat(filename)
    X = m['megdata']
    brain_stimuli_labels = [w.strip() for w in m['items']]
    cat_index = m['cat_index']
    
    if perm:
        # item reps in training data (in pooled model)
        if len(X) > 70:
            n_rep = 3
            X = np.array_split(X, n_rep, axis=0) 
            
            idx = np.arange(len(X[0]))
            np.random.shuffle(idx)
            
            X_shuffled = []
            for arr in X:
                arr = arr[idx]  
                X_shuffled.append(arr)
            
            X = np.concatenate(X_shuffled, axis=0) 
            
        else:    
            idx = np.arange(len(X))
            np.random.shuffle(idx)
            X = X[idx]  
            
    return X, brain_stimuli_labels, cat_index


# Load semantic norms

def load_vectors(filename, brain_stimuli_labels):
    m = loadmat(filename)
    y = m['vectors']
    norm_words = m['basic_words']
    norm_words = [i.strip() for i in norm_words]
    order = [norm_words.index(w) for w in brain_stimuli_labels]
    norm_words = [norm_words[i] for i in order]
    y = y[order]
    return y, norm_words



X_train, train_brain_labels, cat_index = load_brain_data(args.input_file,perm=perm)

y_train, train_words = load_vectors(args.norms, train_brain_labels)

if args.input_file2 is None:
    print("Using the same file for training and testing")
    X_test = X_train
    y_test = y_train
    test_words = train_words
    test_brain_labels = train_brain_labels
    
else:
    # training done on a file loaded earlier
    print("Using a different file for training")
    # load the test file to use
    X_test, test_brain_labels,cat_index = load_brain_data(args.input_file2, perm=perm)
    y_test, test_words = load_vectors(args.norms, test_brain_labels)


if args.verts is not None:
    print("Extracting specific ROI")
    verts_list = list(map(int, args.verts.split(",")))
    X_train = X_train[:, verts_list, :]
    X_test = X_test[:, verts_list, :] 

    
n_targets = y_test.shape[1]
print(X_train.shape)
_, n_vertices, n_times = X_train.shape

pairwise_accuracies = []
weights = []
feat_scores = []
predicted_y = []
patterns = []
alphas = []

if args.temporal_cross != -1:
    t_train=args.t_train
    X_train_slice = X_train[:, :, t_train:t_train + args.temporal_cross].reshape(-1, n_vertices * args.temporal_cross)
    for t_test in range(n_times - args.temporal_cross + 1):
        X_test_slice = X_test[:, :, t_test:t_test + args.temporal_cross].reshape(-1, n_vertices * args.temporal_cross)
        if verbose:
            print(f'Training on t {t_train} to (not including) {t_train + args.temporal_cross}')
            print(f'Testing on t {t_test} to (not including) {t_test + args.temporal_cross}') 
        result = zero_shot_decoding_tc(
             X_train_slice, X_test_slice, y_train, y_test, verbose=verbose, break_after=break_after, metric=args.distance_metric, 
             train_words = train_words,test_words=test_words,
         )
        # extract the results
        pairwise_accuracies.append(result[0])
        weights.append(result[1].coef_)
        alphas.append(result[1].alpha_)
        feat_scores.append(result[2])
        predicted_y.append(result[3])
        patterns.append(result[4].reshape(n_vertices, args.time_resolved, n_targets).transpose(2, 1, 0))

elif args.time_resolved != -1:             
    for t in range(n_times - args.time_resolved):
    # slice t: t+window_size and reshape
    #t=args.t_train

        X_train_slice = X_train[:, :, t:t + args.time_resolved].reshape(-1, n_vertices * args.time_resolved)
        X_test_slice = X_test[:, :,  t:t + args.time_resolved].reshape(-1, n_vertices *  args.time_resolved)
    
        if verbose:
            print('Decoding window %d-%d' % (t, t + args.time_resolved))
        # run the decoding for the current slice
        result = zero_shot_decoding_tc(
             X_train_slice, X_test_slice, y_train, y_test, verbose=verbose, break_after=break_after, metric=args.distance_metric, 
             train_words = train_words,test_words=test_words,
         )
        # extract the results
        pairwise_accuracies.append(result[0])
        weights.append(result[1].coef_)
        alphas.append(result[1].alpha_)
        feat_scores.append(result[2])
        predicted_y.append(result[3])
        patterns.append(result[4].reshape(n_vertices, args.time_resolved, n_targets).transpose(2, 1, 0)) 

else:
    if verbose:
        print("Whole brain and time decoding")

    X_train = X_train.reshape(-1, n_vertices * n_times)
    X_test= X_test.reshape(-1, n_vertices * n_times)

    
    # run the decoding for the current slice
    pairwise_accuracies, model, feat_scores, predicted_y, patterns = zero_shot_decoding_tc(
         X_train, X_test, y_train, y_test, verbose=verbose, break_after=break_after, metric=args.distance_metric, 
         train_words = train_words,test_words=test_words,
     )
    weights = model.coef_
    alphas = model.alpha_
    patterns = patterns.reshape(n_vertices, n_times, n_targets).transpose(2, 1, 0)


results = {
    'pairwise_accuracies': pairwise_accuracies,
    'weights': weights,
    'feat_scores': feat_scores,
    'subject': args.subject_id,
    'inputfile': args.input_file,
    'normfile': args.norms,
    'alphas': alphas,
    'target_word_labels': test_brain_labels ,
    'cat_index': cat_index,
    'predicted_y': predicted_y,
    'patterns': patterns,
    'time_resolved': args.time_resolved,
}

Path(args.output).parent.mkdir(parents=True, exist_ok=True)
savemat(args.output, results)

