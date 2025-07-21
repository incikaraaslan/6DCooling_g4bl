import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from varrftol import insert_generated_blocks
from convertZ import convertZ
import time
import shutil

def run_g4beamline(input_file, gradients, phases, which_stage, which_file, number_of_particles):
    try:
        # Create your 1 file with random Gaussian generated RF cavities.
        insert_generated_blocks(input_file, input_file.replace(".g4bl", "") + f"_with_file_{which_file}_cavities.g4bl", gradients, phases) # _file_{which_file}
        
        # Run G4BL for the generated file.
        result = subprocess.run(['g4bl', input_file.replace(".g4bl", "") + f"_with_file_{which_file}_cavities.g4bl", f'filename=for009_{which_file}', f"last={number_of_particles}"], capture_output=True, text=True, check=True)
        
        # Reset the z coordinate of your resultant beam to z = 0 in order to use this output for the next stage.
        if os.path.exists(f"beam_stage{which_stage}_out.txt"):
            convertZ(f"beam_stage{which_stage}_out.txt", f"beam_stage{which_stage}_upt.txt")
        if os.path.exists(f"beam_stage{which_stage}_noerr_out.txt"):
            convertZ(f"beam_stage{which_stage}_noerr_out.txt", f"beam_stage{which_stage}_noerr_upt.txt")
        
        return result
    
    except subprocess.CalledProcessError as e:
        print(f"Error running G4beamline: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def run_ecalc9f(input_file):
    if os.path.exists("ecalc9f.dat"):
        try:
            # Just in case remove your ecalc9f.dat
            os.remove("ecalc9f.dat")
        
        except Exception as e:
            print(f"WARNING: Could not delete ecalc9f.dat before ECALC9F run: {e}")
    try:
        # Run ECALC9F for a given file.
        result = subprocess.run(['./ecalc9f.exe', input_file], capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running ECALC9F: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def singleStage(input_file, mean, stdev, meanp, stdevp, no_cavities, ncells, number_of_particles, stage_no, sample_no):
    ecalc9f_file = "ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    
    # RUN G4BL for the stage:
    gradients = np.random.normal(mean, stdev, size=(ncells+1, no_cavities)) # (31,6) 30 + 1 due to g4bl shenanigans
    phases = np.random.normal(meanp, stdevp, size=(ncells+1, no_cavities))
    g4blresult = run_g4beamline(input_file, gradients, phases, stage_no, sample_no, number_of_particles) # (name, 180 values in (30,6), sample #)
    
    if g4blresult:
        print("G4beamline simulation completed successfully.")
    
    # Now we'd like to get zvals, eperps, elongs, transmissions for this file, only to run the stats in another file.
    eperps = []
    elongs = []
    transs = []
    zvals = []
    cols = [0,1,3,4,12]
    
    if os.path.exists("./for009.dat") and sample_no == 0:
        os.rename("./for009.dat", "./for009"+ f"prev"+".txt")
        os.rename("./for009"+ f"_{sample_no}"+".txt", "./for009.dat")
    elif os.path.exists("./for009.dat") and i != 0:
        os.rename("./for009.dat", "./for009"+ f"_{sample_no-1}"+".txt")
        os.rename("./for009"+ f"_{sample_no}"+".txt", "./for009.dat") 
    else:
        os.rename("./for009"+ f"_{sample_no}"+".txt", "./for009.dat")

    ecalcresult = run_ecalc9f(ecalc9f_file)
    data_final = np.loadtxt(ecalcfinal_file,skiprows=13, usecols=cols)
    
    zvals = data_final[:,1] # mm to m conversion
    eperps = data_final[:,2]*1000 # mm to m conversion
    elongs = data_final[:,3]*1000 # mm to m conversion
    transs= data_final[:,4]/data_final[0,4]*100 # Percentage Conversion

    if ecalcresult:
            print("Ecalc9f calculations completed successfully.")
    
    os.rename("./for009.dat", "./for009"+ f"_{sample_no}"+ f"_{stage_no}"+".txt")
    shutil.move("./for009"+ f"_{sample_no}"+ f"_{stage_no}"+".txt", "./doneFOR009/for009"+ f"_{sample_no}"+ f"_{stage_no}"+".txt")
    
    data = np.column_stack([zvals, eperps, elongs, transs])
    """header = "ZVals\teperpErr\telongErr\ttransErr"
    np.savetxt(f"./dataforAnl/post_merge_{sample_no}_stage{stage_no}_output.txt", data, fmt="%.6e", delimiter="\t", header=header)"""
    return data

def singleStageNoErr(noerrfile, number_of_particles, stage_no):
    """
    Runs the "no deviation from the original" case for a single stage.
    """
    ecalc9f_file = "ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    
    result_noerr = subprocess.run(['g4bl', noerrfile, f'filename=for009_noerr', f"last={number_of_particles}"], capture_output=True, text=True, check=True)

    # No Err Case
    if os.path.exists("./for009_noerr.txt"):
        os.rename("./for009_noerr.txt", "./for009.dat")
        
        ecalcresult = run_ecalc9f(ecalc9f_file)
        data_final = np.loadtxt(ecalcfinal_file,skiprows=13, usecols=cols)
        
        
        zvals_noerr = data_final[:,1]
        eperps_noerr = data_final[:,2]*1000
        elongs_noerr = data_final[:,3]*1000
        transs_noerr = data_final[:,4]/data_final[0,4]*100
        
        print("NOERR G4bl and Ecalc9f calculations completed successfully.")
        
        os.rename("./for009.dat", f"./for009_noerr"+ f"_{stage_no}"+".txt")
        shutil.move(f"./for009_noerr"+ f"_{stage_no}"+".txt", "./doneFOR009/for009_noerr"+ f"_{stage_no}"+".txt")
    
    datanoerr = np.column_stack(zvals_noerr[0],np.asarray(eperps_noerr).flatten(),np.asarray(elongs_noerr).flatten(), np.asarray(transs_noerr).flatten())
    """header = "eperpNoErr\telongNoErr\ttransNoErr"
    np.savetxt(f"./dataforAnl/post_merge_stage{stage_no}_noerroutput.txt", datanoerr, fmt="%.6e", delimiter="\t", header=header)"""
    return datanoerr
