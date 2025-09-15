import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from convertZ import convertZ, extract_region_beam
import time
import shutil

def run_ecalc9f(input_file):
    if os.path.exists("ecalc9f.dat"):
        try:
            # Just in case remove your ecalc9f.dat
            os.remove("ecalc9f.dat")
        
        except Exception as e:
            print(f"WARNING: Could not delete ecalc9f.dat before ECALC9F run: {e}")
    try:
        # Run ECALC9F for a given file.
        
        old_name = input_file
        os.rename(old_name, "./ecalc9f.inp")
        result = subprocess.run(['./ecalc9f.exe', "./ecalc9f.inp"], capture_output=True, text=True, check=True)
        os.rename("./ecalc9f.inp", old_name)
        
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running ECALC9F: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def singleStageNoErr(noerrfile, number_of_particles, stage_no):
    """
    Runs the "no deviation from the original" case for a single stage.
    """
    
    ecalcfinal_file = "./ecalc9f.dat"
    try:
        result_noerr = subprocess.run(['g4bl', noerrfile, f'filename=for009_noerr_{stage_no}', f"last={number_of_particles}"], capture_output=True, text=True, check=True)
        
        # Extract regions in the extreg9.inp files for each stage.
        extract_region_beam(f"for009_noerr_{stage_no}.txt", f"./extregs/extreg9_{stage_no}.inp", f"beam_stage{stage_no}_noerrout.txt")
        
        # Reset the z coordinate of your resultant beam to z = 0 in order to use this output for the next stage.
        if os.path.exists(f"beam_stage{stage_no}_noerrout.txt"):
            convertZ(f"beam_stage{stage_no}_noerrout.txt", f"beam_stage{stage_no}_noerr_upt.txt")
    
    except subprocess.CalledProcessError as e:
        print(f"Error running G4beamline: {e}")
        if e.stderr:
            print(e.stderr)

    # No Err Case
    if os.path.exists(f"./for009_noerr_{stage_no}.txt"):
        os.rename(f"./for009_noerr_{stage_no}.txt", "./for009.dat")
        
        if int(stage_no) < 5:
            ecalc9f_file = "ecalc9f352.inp"
            ecalcresult = run_ecalc9f(ecalc9f_file)
        else:
            ecalc9f_file = "ecalc9f704.inp"
            ecalcresult = run_ecalc9f(ecalc9f_file)
        
        data_final = np.loadtxt(ecalcfinal_file,skiprows=13, usecols=[0,1,3,4,12])
        
        
        zvals_noerr = data_final[:,1]
        eperps_noerr = data_final[:,2]*1000
        elongs_noerr = data_final[:,3]*1000
        transs_noerr = data_final[:,4]/data_final[0,4]*100
        
        print("NOERR G4bl and Ecalc9f calculations completed successfully.")
        
        os.rename("./for009.dat", f"./for009_noerr_{stage_no}"+".txt")
        shutil.move(f"./for009_noerr_{stage_no}"+".txt", f"./for009outputs/for009_noerr_{stage_no}"+".txt")
    
    datanoerr = np.column_stack((zvals_noerr,np.asarray(eperps_noerr).flatten(),np.asarray(elongs_noerr).flatten(), np.asarray(transs_noerr).flatten()))
    return datanoerr
