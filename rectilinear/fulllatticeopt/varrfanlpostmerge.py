import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import tqdm
from varrfanlsinglecell import singleCell
import re
import glob

def searchforvals(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Use regex search on the whole content
    mrfgrad = re.search(r'param\s+rf_grad\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mrfphase = re.search(r'param\s+rf_ph\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mrffreq = re.search(r'param\s+rf_fre\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mrfwindowlength = re.search(r'param\s+rf_window_length\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)
    mnocells = re.search(r'param\s+ncells\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', content)

    # Extract number of cavities by looping over lines
    mnocav = None
    for line in content.splitlines():
        match = re.match(r'#\s*(\d+)\s+CAVITIES', line)
        if match:
            mnocav = match
            break

    # Check all matches
    if not all([mrfgrad, mrfphase, mrffreq, mrfwindowlength, mnocav, mnocells]):
        raise ValueError("One or more parameters not found in file.")

    return (
        float(mrfgrad.group(1)),
        float(mrfphase.group(1)),
        float(mrffreq.group(1)),
        float(mrfwindowlength.group(1)),
        int(mnocav.group(1)),
        int(mnocells.group(1))
    )

if __name__ == "__main__":
    # Parameters for random distribution for the RF Gradient Offset/Error
    parser = argparse.ArgumentParser()
    parser.add_argument("--mean", type=float, default=0.0, help="Offset Mean [MV/m]")
    parser.add_argument("--stdev", type=float, default=1.0,  help="Offset Stdev [MV/m]" )
    parser.add_argument("--stdev-phase", type=float, default=10.0,  help="Offset RF Phase Stdev [deg]" )
    parser.add_argument("--sample-size", type=int, default=2,  help="# Trials")
    parser.add_argument("--number-of-particles", type=int, default=2000,  help="# particles in beam")
    args = parser.parse_args()
    
    file_list = sorted(glob.glob("./incis_cleaned_cooling_stage*_variablerfs.g4bl"))
    # noerr_list = sorted(glob.glob("./incis_cleaned_cooling_stage*.g4bl"))
    noerr_list = sorted(f for f in glob.glob("./incis_cleaned_cooling_stage*.g4bl") if re.fullmatch(r"\./incis_cleaned_cooling_stage\d+\.g4bl", f))

    ecalc9f_file = "ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    
    z_last = []
    eperp_avg_last = []
    eperp_noerr_last = []
    eperp_sem_last = []
    elong_avg_last = []
    elong_noerr_last = []
    elong_sem_last = []
    trans_avg_last = [] 
    trans_noerr_last = [] 
    trans_sem_last = []
    
    for i, filename in enumerate(file_list):
        print(filename)
        # ACTUAL VALUES -- READ THEM FROM EACH STAGE PROBABLY
        rfgrad_actual, rfphase_actual, rffreq_actual, rfwindowlength_actual, ncavities, ncells = searchforvals(filename)
        mean = rfgrad_actual + args.mean
        stdev = args.stdev
        meanp = rfphase_actual + args.mean
        stdevp = args.stdev_phase
        print(noerr_list[i])
        singleCell(filename, mean, stdev, meanp, stdevp, args.sample_size, ncavities, ncells, args.number_of_particles, noerr_list[i],i)
        
        # Skipping header, load full table for each
        print(i+1)
        data = np.loadtxt(f"./post_merge_stage{i+1}_output.txt", comments="#")
        # Get the last row ([-1]) which has the last values of each column
        last_values = data[-1]
        
        z_last.append(last_values[0]) 
        eperp_avg_last.append(last_values[1])
        eperp_noerr_last.append(last_values[2])
        eperp_sem_last.append(last_values[3])
        elong_avg_last.append(last_values[4])
        elong_noerr_last.append(last_values[5])
        elong_sem_last.append(last_values[6])
        trans_avg_last.append(last_values[7])
        trans_noerr_last.append(last_values[8])
        trans_sem_last.append(last_values[9])
        
    plt.errorbar(z_last, eperp_avg_last, xerr = None, yerr = eperp_sem_last, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(eperp_noerr_last).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.array(eperp_avg_last) - np.array(eperp_sem_last), np.array(eperp_avg_last) + np.array(eperp_sem_last), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_T$ [mm]")
    plt.title("Transverse Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_eperp"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles) + "_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(z_last, elong_avg_last, xerr = None, yerr = elong_sem_last, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(elong_noerr_last).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.array(elong_avg_last) - np.array(elong_sem_last), np.array(elong_avg_last) + np.array(elong_sem_last), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_L$ [mm]")
    plt.title("Longitudinal Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_elong"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles)+"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(z_last, trans_avg_last, xerr = None, yerr = trans_sem_last, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(trans_noerr_last).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.array(trans_avg_last) - np.array(trans_sem_last), np.array(trans_avg_last) + np.array(trans_sem_last), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel("Transmission [%]")
    plt.title("Transmission v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_trans"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles) +"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()