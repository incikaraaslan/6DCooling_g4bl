import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from convertZ import convertZ, extract_region_beam
from varfortol import insert_generated_blocks
import shutil

def run_g4beamline(input_file, gradients, phases, which_stage, which_file, number_of_particles):
    try:
        # Create your 1 file with random Gaussian generated RF cavities.
        insert_generated_blocks(input_file, input_file.replace(".g4bl", "") + f"_with_file_{which_file}_cavities.g4bl", gradients, phases) # _file_{which_file}
        
        # Run G4BL for the generated file.
        print(f'filein="./beam_stage{which_stage-1}_{which_file}_upt.txt"')
        result = subprocess.run(['g4bl', input_file.replace(".g4bl", "") + f"_with_file_{which_file}_cavities.g4bl", f'filename=for009_werr_{which_stage}_{which_file}', f"last={number_of_particles}", f'filein=beam_stage{which_stage-1}_{which_file}_upt.txt'], capture_output=True, text=True, check=True)
        # Save stdout (program output) to a file
        with open("g4bl_output.txt", "w") as f:
            f.write(result.stdout)
        # Extract regions in the extreg9.inp files for each stage.
        extract_region_beam(f"./for009_werr_{which_stage}_{which_file}.txt", f"./extregs/extreg9_{which_stage}.inp", f"./beam_stage{which_stage}_{which_file}_out.txt")
        
        # Reset the z coordinate of your resultant beam to z = 0 in order to use this output for the next stage.
        if os.path.exists(f"./beam_stage{which_stage}_{which_file}_out.txt"):
            convertZ(f"./beam_stage{which_stage}_{which_file}_out.txt", f"./beam_stage{which_stage}_{which_file}_upt.txt") # Each sample will go through all 10 stages so keep the file ig?
            
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

def singleStage(input_file, mean, stdev, meanp, stdevp, no_cavities, ncells, number_of_particles, stage_no, sample_no): #SINGLE SAMPLE!
    
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
    cols = [0,1,3,4,5,12]
    
    # If we delete the for009s after each sample, we can just say this is the prev stage's one
    # wait why not delete all smh
    if os.path.exists(f"./for009_werr_{stage_no}_{sample_no}.txt"):
        
        if os.path.exists("./for009.dat"):
            os.remove("./for009.dat")
        
        os.rename(f"./for009_werr_{stage_no}_{sample_no}.txt", "./for009.dat")
    
        if int(stage_no) < 5:
            ecalc9f_file = "ecalc9f352.inp"
            ecalcresult = run_ecalc9f(ecalc9f_file)
            
            data_final = np.loadtxt("./ecalc9f.dat",skiprows=13, usecols=[0,1,3,4,5,12])
        else:
            ecalc9f_file = "ecalc9f704.inp"
            ecalcresult = run_ecalc9f(ecalc9f_file)
    
            data_final = np.loadtxt("./ecalc9f.dat",skiprows=13, usecols=[0,1,3,4,5,12])
        
        zvals = data_final[:,1] # mm to m conversion
        eperps = data_final[:,2]*1000 # mm to m conversion
        elongs = data_final[:,3]*1000 # mm to m conversion
        e6ds = data_final[:,4]*(1000**3) # mm^3 to m^3 conversion
        transs= data_final[:,5]/data_final[0,5] # Fraction Conversion

        if ecalcresult:
                print("Ecalc9f calculations completed successfully.")
    
        os.rename("./for009.dat", f"./for009_werr_{stage_no}_{sample_no}.txt")
        shutil.move(f"./for009_werr_{stage_no}_{sample_no}.txt", f"./doneFOR009/for009_werr_{stage_no}_{sample_no}.txt")
    
    data = np.column_stack((zvals, eperps, elongs, e6ds, transs))
    return data


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
        
        data_final = np.loadtxt(ecalcfinal_file,skiprows=13, usecols=[0,1,3,4,5,12])
        
        
        zvals_noerr = data_final[:,1]
        eperps_noerr = data_final[:,2]*1000
        elongs_noerr = data_final[:,3]*1000
        e6ds_noerr = data_final[:,4]*(1000**3) # mm^3 to m^3 conversion
        transs_noerr = data_final[:,5]/data_final[0,5] # Fraction Conversion
        
        if ecalcresult:
                print("Ecalc9f calculations completed successfully.")
        
        print("NOERR G4bl calculations completed successfully.")
        
        os.rename("./for009.dat", f"./for009_noerr_{stage_no}"+".txt")
        shutil.move(f"./for009_noerr_{stage_no}"+".txt", f"./doneFOR009/for009_noerr_{stage_no}"+".txt")
    
    datanoerr = np.column_stack((zvals_noerr,np.asarray(eperps_noerr).flatten(),np.asarray(elongs_noerr).flatten(),np.asarray(e6ds_noerr).flatten(), np.asarray(transs_noerr).flatten()))
    return datanoerr
