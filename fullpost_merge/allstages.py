import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from singlestage import singleStageNoErr
import re
import glob
from natsort import natsorted
from itertools import islice

if __name__ == "__main__":
    """
    
        We'd like to go through all 10 stages in one go FOR ALL # sample sizes. So ideally, it should create the 0th file for all 10 stages FIRST
        and then go back and create the 1st file for all 10.
    
    """
    # Parameters for random distribution for the RF Gradient Offset/Error
    parser = argparse.ArgumentParser()
    parser.add_argument("--number-of-particles", type=int, default=7000,  help="# particles in Stage 1")
    args = parser.parse_args()
    
    noerr_list = natsorted(f for f in glob.glob("./incis_cleaned_cooling_stage*.g4bl") if re.fullmatch(r"\./incis_cleaned_cooling_stage\d+\.g4bl", f))

    noerr_data = []
    
    last_data = []
    
    # NO ERR NEEDED ONCE
    for i, nfilename in enumerate(noerr_list):
        print(nfilename)
        stage_no = i+1
        datanoerr = singleStageNoErr(nfilename, args.number_of_particles, stage_no)
        z_noerr, eperp_noerr, elong_noerr, trans_noerr = datanoerr.T
    
        plt.plot(z_noerr, eperp_noerr, color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
        plt.xlabel("z [m]")
        plt.ylabel(r"$\epsilon_T$ [mm]")
        plt.title("Transverse Emittance v. Beam Axis (z)")
        plt.grid(True)
        plt.legend()
        plt.savefig("./allstgradphtol_eperp"+"_stage_" + str(stage_no) + "_no_" + str(args.number_of_particles) + "_.png")
        plt.close()
        
        
        plt.plot(z_noerr, elong_noerr, color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
        plt.xlabel("z [m]")
        plt.ylabel(r"$\epsilon_L$ [mm]")
        plt.title("Longitudinal Emittance v. Beam Axis (z)")
        plt.grid(True)
        plt.legend()
        plt.savefig("./allstgradphtol_elong"+"_stage_" + str(stage_no) + "_no_" + str(args.number_of_particles)+ "_.png")
        plt.close()
        
        plt.plot(z_noerr, trans_noerr, color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
        plt.xlabel("z [m]")
        plt.ylabel("Transmission [%]")
        plt.title("Transmission v. Beam Axis (z)")
        plt.grid(True)
        plt.legend()
        plt.savefig("./allstgradphtol_trans"+"_stage_"+ str(stage_no) + "_no_" + str(args.number_of_particles)+ "_.png")
        plt.close()