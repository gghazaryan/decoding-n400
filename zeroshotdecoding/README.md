 Zero shot learning on Redness data
----------------------------------

The set of code is used to perform semantic norm decoding using linear regression model similar to Sudre et al., Neuroimage 2012

The data folder contains model input: MEG data (target x time x sensor/source points),target_word_labels,  category_labels, category indices and the norms (i.e. the features). This data file is generated for each subject by extract_data_matrix_SUBJECT.py


The model can be run on sensor (sensor_level.m) or source level  (source_level.m) data. For both data types the threshold for significance can be deteremined using random_permutation.m. The random_permutation.m shuffles the real data for a random subjects for a specified number of iterations and thus simulates a distribution of random data, from whihc the probablity of the null hypothesis can be estimated. Running the premutation test on source level is *possibly* too demanding computationally (if 1000 iterations are used). 

=======
Originally written by Ali Faisal and Annika Hultén in MATLAB.
Rewritten in Python by Marijn van Vliet.


Running the zeroshot or permutation test on Taito/Triton 
---------------------------------------------------

Mount a folder in your home directory on to Taito 
   >> sshfs annika@taito.csc.fi:/wrk/annika/redness1/sensor/ /net/psyko/home/annika/TaitoRun
   This ony needs to be done once

To run the code:

 1. Copy the `.mat` data files (not included in this repository) to Taito
 2. Copy all the files in this directory to Taito (i.e. clone the git repo / git pull)
 3. check the paths of the input files in `sensor_level.py`, `source_level.py` and `random_permutation.py`
 4. check path of the output in `sensor_level.py`, `sensor_level.sh`, `source_level.py`, `source_level.sh`, `random_permutation.py`, `random_permutations.sh`
 5. Choose the analysis you want to run:
    - To run sensor level analysis, run on Taito: `sbatch sensor_level.sh`
    - To run source level analysis, run on Taito: `sbatch source_level.sh`
    - To run random permutation test, run on Taito: `sbatch random_permutations.sh`

4. On Taito/Triton run you batch by the command
   >> sbatch random_permutation.sh
(or  sbatch source_level.sh or  sbatch sensor_level.sh depending on what you want to do)

Usefull commands on Taito: 
Check status 
squeue -l -u username

Cancel a job
scancel [jobid]

For more operation see csc taito slurm commands.
=======

