import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from varrfanlsinglestage import singleStageNoErr, singleStage
import re
import glob
from natsort import natsorted
import matplotlib.pyplot as plt
from itertools import islice

def searchforVals(filename):
    """
        Look for parameters for a given stage.
    """
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
    """
    
        We'd like to go through all 10 stages in one go FOR ALL # sample sizes. So ideally, it should create the 0th file for all 10 stages FIRST
        and then go back and create the 1st file for all 10.
    
    """
    # ---- LaTeX Setup for Matplotlib ----
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",  # Uses Computer Modern by default
        "axes.labelsize": 18,
        "font.size": 16,
        "legend.fontsize": 14,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.dpi": 300,
        "figure.dpi": 300,
        "text.latex.preamble": r"\usepackage{amsmath}"  # DON'T add newtxtext/newtxmath!
    })
    # Parameters for random distribution for the RF Gradient Offset/Error
    parser = argparse.ArgumentParser()
    parser.add_argument("--mean", type=float, default=0.0, help="Offset Mean [MV/m]")
    parser.add_argument("--stdev", type=float, default=1.0,  help="Offset Stdev [MV/m]" )
    parser.add_argument("--stdev-phase", type=float, default=10.0,  help="Offset RF Phase Stdev [deg]" )
    parser.add_argument("--sample-size", type=int, default=2,  help="# Trials")
    parser.add_argument("--number-of-particles", type=int, default=200,  help="# particles in Stage 1")
    grabOption = input("0: Show all stages in one single plot, 1: Show data for each stage individually for all stages. ")
    args = parser.parse_args()
    
    file_list = natsorted(glob.glob("./incis_cleaned_cooling_stage*_variablerfs.g4bl"))
    noerr_list = natsorted(f for f in glob.glob("./incis_cleaned_cooling_stage*.g4bl") if re.fullmatch(r"\./incis_cleaned_cooling_stage\d+\.g4bl", f))
    
    err_data = []
    noerr_data = []
    last_data = []
    z_data = []

    for sample_no in trange(args.sample_size):
        
        print("Sample #: " + str(sample_no))
        
        for i, filename in enumerate(file_list): # going through stages
            print(filename)
            stage_no = i+1
            # ACTUAL VALUES -- READ THEM FROM EACH STAGE
            rfgrad_actual, rfphase_actual, rffreq_actual, rfwindowlength_actual, ncavities, ncells = searchforVals(filename)
            mean = rfgrad_actual + args.mean
            stdev = args.stdev
            meanp = rfphase_actual + args.mean
            stdevp = args.stdev_phase
            
            data = singleStage(filename, mean, stdev, meanp, stdevp, ncavities, ncells, args.number_of_particles, stage_no, sample_no)
            
            # GRAB OPTION 0
            # Get the last row ([-1]) which has the last values of each column
            last_values = data[-1]
            last_data.append([last_values[0],last_values[1],last_values[2],last_values[3], last_values[4]])
            z_data.append(last_values[0])

    # GRAB OPTION 0
    z_last = []
    z_avg = []
    z_sem =[]
    eperp_last = []
    eperp_sem = []
    eperp_avg = []
    elong_last = []
    elong_avg = []
    elong_sem = []
    e6d_last =[]
    e6d_avg = []
    e6d_sem = []
    trans_last = []
    trans_avg = []
    trans_sem = []
    
    zcur = 0
    trans = 1
    stage_no = 10
    for i in trange(stage_no):
        for j in trange(args.sample_size):
            if j == 0:
                zcur += last_data[i:stage_no*args.sample_size:stage_no][j][0]
                z_last.append(zcur)
                
            eperp_last.append(last_data[i:stage_no*args.sample_size:stage_no][j][1])
            elong_last.append(last_data[i:stage_no*args.sample_size:stage_no][j][2])
            e6d_last.append(last_data[i:stage_no*args.sample_size:stage_no][j][3])
            trans_last.append(last_data[i:stage_no*args.sample_size:stage_no][j][4])
        
        # z_avg.append(np.average(np.asarray(z_last[i*args.sample_size:args.sample_size*i+args.sample_size])))
        eperp_avg.append(np.average(np.asarray(eperp_last[i*args.sample_size:args.sample_size*i+args.sample_size])))
        elong_avg.append(np.average(np.asarray(elong_last[i*args.sample_size:args.sample_size*i+args.sample_size])))
        e6d_avg.append(np.average(np.asarray(e6d_last[i*args.sample_size:args.sample_size*i+args.sample_size])))
        trans_avg.append(np.average(np.asarray(trans_last[i*args.sample_size:args.sample_size*i+args.sample_size])))
        
        # z_sem.append(np.std(np.asarray(z_last[i*args.sample_size:args.sample_size*i+args.sample_size])) / np.sqrt(np.asarray(z_last[i*args.sample_size:args.sample_size*i+args.sample_size]).shape[0]))
        eperp_sem.append(np.std(np.asarray(eperp_last[i*args.sample_size:args.sample_size*i+args.sample_size])) / np.sqrt(np.asarray(eperp_last[i*args.sample_size:args.sample_size*i+args.sample_size]).shape[0]))
        elong_sem.append(np.std(np.asarray(elong_last[i*args.sample_size:args.sample_size*i+args.sample_size])) / np.sqrt(np.asarray(elong_last[i*args.sample_size:args.sample_size*i+args.sample_size]).shape[0]))
        e6d_sem.append(np.std(np.asarray(e6d_last[i*args.sample_size:args.sample_size*i+args.sample_size])) / np.sqrt(np.asarray(e6d_last[i*args.sample_size:args.sample_size*i+args.sample_size]).shape[0]))
        trans_sem.append(np.std(np.asarray(trans_last[i*args.sample_size:args.sample_size*i+args.sample_size])) / np.sqrt(np.asarray(trans_last[i*args.sample_size:args.sample_size*i+args.sample_size]).shape[0]))
    
    # NO ERR NEEDED ONCE
    eperp_noerrl = []
    elong_noerrl = []
    e6d_noerrl = []
    trans_noerrl = []
    for i, nfilename in enumerate(noerr_list):
        print(nfilename)
        stage_no = i+1
        datanoerr = singleStageNoErr(nfilename, args.number_of_particles, stage_no)
        z_noerr, eperp_noerr, elong_noerr, e6d_noerr, trans_noerr = datanoerr.T
        
        eperp_noerrl.append(eperp_noerr[-1])
        elong_noerrl.append(elong_noerr[-1])
        e6d_noerrl.append(e6d_noerr[-1])
        trans_noerrl.append(trans_noerr[-1])
    
    plt.errorbar(z_last, np.asarray(eperp_avg), xerr = None, yerr = eperp_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(eperp_noerrl).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.asarray(eperp_avg) - np.asarray(eperp_sem), np.asarray(eperp_avg) + np.asarray(eperp_sem), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_T$ [mm]")
    # plt.title("Transverse Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_eperp"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles) + "_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(z_last, np.asarray(elong_avg), xerr = None, yerr = elong_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(elong_noerrl).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.asarray(elong_avg) - np.asarray(elong_sem), np.asarray(elong_avg) + np.asarray(elong_sem), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_L$ [mm]")
    # plt.title("Longitudinal Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_elong"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles)+"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(z_last, np.asarray(e6d_avg), xerr = None, yerr = elong_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(e6d_noerrl).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.asarray(e6d_avg) - np.asarray(e6d_sem), np.asarray(e6d_avg) + np.asarray(e6d_sem), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_{6D}$ [$mm^3$]")
    # plt.title("6D Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_e6d"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles)+"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(z_last, np.asarray(trans_avg), xerr = None, yerr = trans_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(z_last, np.asarray(trans_noerrl).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(z_last, np.asarray(trans_avg) - np.asarray(trans_sem), np.asarray(trans_avg) + np.asarray(trans_sem), color='blue', alpha=0.3, label=f'σ = ±{args.stdev}, σRFp = ±{args.stdev_phase}')
    plt.xlabel("z [m]")
    plt.ylabel("Transmission [%]")
    plt.title("Transmission v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./allstvarrfgradphtol_trans"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles) +"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()