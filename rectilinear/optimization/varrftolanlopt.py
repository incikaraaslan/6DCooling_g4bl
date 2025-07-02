import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from varrftol import insert_generated_blocks

from scipy.optimize import differential_evolution
from multiprocessing import Pool, cpu_count
import hashlib
import tempfile
from itertools import count
tag_counter = count()

def pack_inputs(gradients, phases):
    return np.concatenate([gradients.flatten(), phases.flatten()])

def unpack_inputs(x):
    gradients = np.array(x[:186]).reshape(31, 6)
    phases = np.array(x[186:]).reshape(31, 6)
    return gradients, phases

def run_ecalc9f(input_file):
    try:
        result = subprocess.run(['./ecalc9f.exe', input_file], capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running ECALC9F: {e}")
        if e.stderr:
            print(e.stderr)
        return None


def run_g4beamline(input_file, gradients, phases, tag):
    try:
        input_with_cavities = f"{input_file}_{tag}_with_cavities.g4bl"
        insert_generated_blocks(input_file + ".g4bl", input_with_cavities, gradients, phases)
        
        result = subprocess.run([
            'g4bl', input_with_cavities, 
            f'filename=for009_{tag}', 
            f"last={args.number_of_particles}"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode != 0:
                print(f"[{tag}] G4beamline exited with code {result.returncode}")
                print(f"[{tag}] stdout:\n{result.stdout}")
                print(f"[{tag}] stderr:\n{result.stderr}")
                return None
        
        return result

    except Exception as e:
        print(f"[{tag}] G4beamline exception: {e}")
        return None

def objective(x):
    
    # Unique tag for temp files to avoid collisions
    tag = next(tag_counter)
    
    gradients, phases = unpack_inputs(x)
    ecalc9f_file = "ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    
    # Run G4BL
    result = run_g4beamline(input_file, gradients, phases, tag)
    
    # Rename output for ECALC
    if os.path.exists("./for009.dat") and tag == 0:
            os.rename("./for009.dat", "./for009"+ f"prev"+".txt")
            os.rename("./for009"+ f"_{tag}"+".txt", "./for009.dat")
    elif os.path.exists("./for009.dat") and tag != 0:
            os.rename("./for009.dat", "./for009"+ f"_{tag-1}"+".txt")
            os.rename("./for009"+ f"_{tag}"+".txt", "./for009.dat") 
    else:
        os.rename("./for009"+ f"_{tag}"+".txt", "./for009.dat")
    
    # Run ECALC9f
    run_ecalc9f(ecalc9f_file)

    try:
        data = np.loadtxt(ecalcfinal_file, skiprows=13, usecols=[0,1,3,4,5,12]) 
        epsilon_6D = data[:, 4] * 1e9
        epsilon_T = data[:, 2] * 1000
        epsilon_L = data[:, 3] * 1000
        transmission = data[:, 4] / data[0, 4] * 100
        
        # Use inverse so we minimize
        emittance_metric = (epsilon_6D) / transmission
        
        return emittance_metric
    
    except Exception as e:
        print(f"Failed ECALC parse for {tag}: {e}")
        return 1e9

if __name__ == "__main__":
    # Parameters for random distribution for the RF Gradient Offset/Error
    parser = argparse.ArgumentParser()
    parser.add_argument("--mean", type=float, default=0.0, help="Offset Mean [MV/m]")
    parser.add_argument("--stdev", type=float, default=1.0,  help="Offset Stdev [MV/m]" )
    parser.add_argument("--stdev-phase", type=float, default=10.0,  help="Offset RF Phase Stdev [deg]" )
    parser.add_argument("--sample-size", type=int, default=10,  help="# Trials")
    parser.add_argument("--number-of-particles", type=int, default=2000,  help="# particles in beam")
    args = parser.parse_args()
    
    # ACTUAL VALUES
    rfgrad_actual = 22.508192486472524
    rfphase_actual = 32.84244060974717
    rffreq_actual=0.352
    rfwindowlength_actual = 0.1
    
    input_file = "./" + input("please write the name of the g4bl input file: ")
    
    bounds = [(20.0, 25.0)] * 186 + [(0, 360)] * 186  # Adjust bounds to physical limits

    print("Starting optimization...")
    result = differential_evolution(
        objective,
        bounds,
        strategy='best1bin',
        popsize=5,         # reduce for faster iteration
        maxiter=10,
        workers=-1,        # parallel on all cores
        updating='deferred',
        polish=True,
    )

    zvals_noerr = []
    eperps_noerr = []
    elongs_noerr = []
    transs_noerr = []
    
    """# No Err Case
    result_noerr = subprocess.run(['g4bl', "incis_cleaned_cooling_stage1.g4bl", f'filename=for009_noerr', f"last={args.number_of_particles}"], capture_output=True, text=True, check=True)
    
    if os.path.exists("./for009.dat") and os.path.exists("./for009_noerr.txt"):
        i = args.sample_size - 1
        os.rename("./for009.dat", "./for009"+ f"_{i}"+".txt")
        os.rename("./for009_noerr.txt", "./for009.dat")
        
        ecalcresult = run_ecalc9f(ecalc9f_file)
        data_final = np.loadtxt(ecalcfinal_file,skiprows=13, usecols=cols)
        
        # OK, let's collect all eperp, elong, trans data (but then we need to avg over trials)
        zvals_noerr.append(data_final[:,1])
        eperps_noerr.append(data_final[:,2]*1000)
        elongs_noerr.append(data_final[:,3]*1000)
        transs_noerr.append(data_final[:,4]/data_final[0,4]*100)
        
        print("NOERR G4bl and Ecalc9f calculations completed successfully.")"""

    print("Best emittance config found:")
    print("Minimized value:", result.fun)
    np.save("best_rf_config.npy", result.x)