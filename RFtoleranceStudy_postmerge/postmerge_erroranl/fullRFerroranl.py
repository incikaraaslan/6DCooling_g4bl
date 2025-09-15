import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
import re
import glob
from natsort import natsorted
import matplotlib.pyplot as plt
from itertools import islice
from tolRFallstages import allStages
from scipy.stats import norm

parser = argparse.ArgumentParser()
parser.add_argument("--mean", type=float, default=0.0, help="Offset Mean [MV/m]")
parser.add_argument("--stdev", type=float, default=0.0,  help="Offset RF Gradient Stdev [MV/m]" )
parser.add_argument("--stdev-phase", type=float, default=0.0,  help="Offset RF Phase Stdev [deg]" )
parser.add_argument("--sample-size", type=int, default=2,  help="# Trials")
parser.add_argument("--number-of-particles", type=int, default=200,  help="# particles in Stage 1")
# grabOption = input("0: Show all stages in one single plot, 1: Show data for each stage individually for all stages. ")
args = parser.parse_args()

# Fractional Error Plot
fractional_errors =  np.arange(0.0, 11, 2.5) # np.arange(0.0, 0.06, 0.01)
stdevs = []
stdev_phases = []

transmissions = []
e6ds = []
eps6D_ci95 = []
trans_ci95 = []

for i, frac_err in enumerate(fractional_errors):
    print(f"Starting fractional error {frac_err} analysis...")
    stdev_phases.append(frac_err)
    # stdevs.append(frac_err * 10 / 0.39422) # The last value here is \Sigma_i{(1/mu_i)} where i is the stage number (10 stages!)
    
    trnoerr, tr, trsem, e6dnoerr, e6d, e6dsem = allStages(args.mean, args.stdev, stdev_phases[i], args.sample_size, args.number_of_particles)
    
    if i == 0:
        transmissions.append(trnoerr)
        e6ds.append(e6dnoerr)
        eps6D_ci95.append(0.0)
        trans_ci95.append(0.0)
        
    else:
        transmissions.append(tr)
        e6ds.append(e6d)
        eps6D_ci95.append(norm.ppf(0.975) * e6dsem)
        trans_ci95.append(norm.ppf(0.975) * trsem)

data = np.column_stack((fractional_errors, e6ds, transmissions, eps6D_ci95, trans_ci95))
np.savetxt("results00to10.txt", data, header="FractionalError   E6D(mm^3)   Transmission(%)   E6D(mm^3)95%CL  Transmission(%)95%CL", fmt="%.5f", comments='')