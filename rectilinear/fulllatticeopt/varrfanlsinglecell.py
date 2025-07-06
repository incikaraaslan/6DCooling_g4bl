import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from varrftol import insert_generated_blocks
import time

def run_g4beamline(input_file, gradients, phases, which_stage, which_file, number_of_particles):
    try:
        insert_generated_blocks(input_file, f"./incis_cleaned_cooling_stage_{which_stage}_with_file_{which_file}_cavities.g4bl", gradients, phases) # _file_{which_file}
        result = subprocess.run(['g4bl', f"./incis_cleaned_cooling_stage_{which_stage}_with_file_{which_file}_cavities.g4bl", f'filename=for009_{which_file}', f"last={number_of_particles}"], capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running G4beamline: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def run_ecalc9f(input_file):
    if os.path.exists("ecalc9f.dat"):
        try:
            os.remove("ecalc9f.dat")
        except Exception as e:
            print(f"WARNING: Could not delete ecalc9f.dat before ECALC9F run: {e}")
    try:
        result = subprocess.run(['./ecalc9f.exe', input_file], capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running ECALC9F: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def singleCell(input_file, mean, stdev, meanp, stdevp, sample_size, no_cavities, ncells, number_of_particles, noerrfile, stage_no):
    ecalc9f_file = "./ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    # G4BL RUN for each sample file
    for j in trange(sample_size): # THIS IS SUPPOSED TO RUN IT FOR ALL SAMPLE SIZES SO SAMPLE_SIZE, NOT len(values) = 30, values.size = 180 
        values = np.random.normal(mean, stdev, size=(ncells+1, no_cavities)) # 30 + 1 due to g4bl shenanigans
        valuesp = np.random.normal(meanp, stdevp, size=(ncells+1, no_cavities))
        g4blresult = run_g4beamline(input_file, values, valuesp, stage_no+1, j, number_of_particles) # (name, 180 values in (30,6), sample #)
        
        if g4blresult:
            print("G4beamline simulation completed successfully.")
    
    # ECALC6F RUN for each sample file
    eperps = []
    elongs = []
    transs = []
    zvals = []
    eperps_avg = []
    elongs_avg = []
    transs_avg = []
    eperps_sem = []
    elongs_sem = []
    transs_sem = []
    cols = [0,1,3,4,12]
    
    for j in trange(sample_size): # for x in range 0 - 9
        if os.path.exists("./for009.dat") and j == 0:
            os.rename("./for009.dat", "./for009"+ f"prev"+".txt")
            os.rename("./for009"+ f"_{j}"+".txt", "./for009.dat")
        elif os.path.exists("./for009.dat") and j != 0:
            os.rename("./for009.dat", "./for009"+ f"_{j-1}"+".txt")
            os.rename("./for009"+ f"_{j}"+".txt", "./for009.dat") 
        else:
            os.rename("./for009"+ f"_{j}"+".txt", "./for009.dat")

        try: 
            ecalcresult = run_ecalc9f(ecalc9f_file)
            print("ECALC9F stdout:\n", ecalcresult.stdout)
            print("ECALC9F stderr:\n", ecalcresult.stderr)
            
            # Wait to ensure ECALC9F finishes writing the file
            time.sleep(0.3)  # Wait 300 ms to ensure ecalc9f.dat is flushed to disk
            
            # Check the output file is valid before reading it
            if not os.path.exists(ecalcfinal_file) or os.path.getsize(ecalcfinal_file) < 100:
                raise ValueError(f"{ecalcfinal_file} does not exist or is too small — possible ECALC9F crash or truncation.")
        except subprocess.CalledProcessError as e:
            print(f"ECALC9F crashed: {e}")
            print("stdout:\n", e.stdout)
            print("stderr:\n", e.stderr)
            return  # Skip this sample
        
        try:
            if not os.path.exists(ecalcfinal_file) or os.path.getsize(ecalcfinal_file) == 0:
                raise ValueError(f"{ecalcfinal_file} does not exist or is empty")

            data_final = np.loadtxt(ecalcfinal_file, skiprows=13, usecols=cols)
            
            if data_final.size == 0:
                raise ValueError(f"{ecalcfinal_file} is empty after skipping rows.")

            print(data_final)
        except Exception as e:
            print(f"Error loading {ecalcfinal_file}: {e}")
            return  # Skip this sample if data is invalid

        # OK, let's collect all eperp, elong, trans data (but then we need to avg over trials)
        zvals.append(data_final[:,1])
        eperps.append(data_final[:,2]*1000)
        elongs.append(data_final[:,3]*1000)
        transs.append(data_final[:,4]/data_final[0,4]*100)
        
    
    if ecalcresult:
            print("Ecalc9f calculations completed successfully.")
    
    # DATA ANALYSIS + PLOTTING
    for a in trange(len(eperps)):
        
        for k in trange(len(eperps[a])):
            p = []
            l = []
            t = []

            for c in trange(len(eperps)):
                p.append(eperps[c][k])
                l.append(elongs[c][k])
                t.append(transs[c][k])
                
            
            p = np.asarray(p)
            l = np.asarray(l)
            t = np.asarray(t)
            
            eperps_avg.append(np.average(p))
            elongs_avg.append(np.average(l))
            transs_avg.append(np.average(t))
            eperps_sem.append(np.std(p)/np.sqrt(p.shape[0]))
            elongs_sem.append(np.std(l)/np.sqrt(l.shape[0]))
            transs_sem.append(np.std(t)/np.sqrt(t.shape[0]))
        
        break
    
    # Run No Error Case
    result_noerr = subprocess.run(['g4bl', noerrfile, f'filename=for009_noerr', f"last={number_of_particles}"], capture_output=True, text=True, check=True)
    
    zvals_noerr = []
    eperps_noerr = []
    elongs_noerr = []
    transs_noerr = []
    
    # No Err Case
    if os.path.exists("./for009.dat") and os.path.exists("./for009_noerr.txt"):
        a = sample_size - 1
        os.rename("./for009.dat", "./for009"+ f"_{a}"+".txt")
        os.rename("./for009_noerr.txt", "./for009.dat")
        
        ecalcresult = run_ecalc9f(ecalc9f_file)
        try:
            if not os.path.exists(ecalcfinal_file) or os.path.getsize(ecalcfinal_file) == 0:
                raise ValueError(f"{ecalcfinal_file} does not exist or is empty")

            data_final = np.loadtxt(ecalcfinal_file, skiprows=13, usecols=cols)

            if data_final.size == 0:
                raise ValueError(f"{ecalcfinal_file} is empty after skipping rows.")

            zvals_noerr.append(data_final[:,1])
            eperps_noerr.append(data_final[:,2]*1000)
            elongs_noerr.append(data_final[:,3]*1000)
            transs_noerr.append(data_final[:,4]*100/data_final[0,4])
        except Exception as e:
            print(f"Error loading no-error data: {e}")
            return  # or continue, depending on what you want to do

        
        print("NOERR G4bl and Ecalc9f calculations completed successfully.")
        os.rename("./for009.dat", f"./for009_noerr{int(stage_no+1)}.txt", )
    
    data = np.column_stack([zvals[0], eperps_avg, np.asarray(eperps_noerr).flatten(), eperps_sem, elongs_avg, np.asarray(elongs_noerr).flatten(), elongs_sem, transs_avg, np.asarray(transs_noerr).flatten(), transs_sem])
    header = "ZVals\teperpErrAvg\teperpNoErr\teperpErrB\telongErrAvg\telongNoErr\telongErrB\ttransErrAvg\ttransNoErr\ttransErrB"
    np.savetxt(f"./post_merge_stage{int(stage_no+1)}_output.txt", data, fmt="%.6e", delimiter="\t", header=header)
    return None
        
