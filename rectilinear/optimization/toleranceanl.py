import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange

def run_g4beamline(input_file, rf_Grad, i):
    try:
        result = subprocess.run(['g4bl', input_file, f'rf_grad={rf_Grad}', f'filename=for009_{i}'], capture_output=True, text=True, check=True)

        print("Successfully ran for RF Gradient=" + str(values[i]))
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running G4beamline: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def run_ecalc9f(input_file):
    try:
        result = subprocess.run(['./ecalc9f.exe', input_file], capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running ECALC9F: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def randomgaussdist(mean, stdev, sample_size):

    values = []
    while len(values) < sample_size: # get 10 samples
        sample = random.gauss(mean, stdev)
        if sample >= mean - 5*stdev and sample <= mean + 5*stdev:
            values.append(sample)
    
    return values

if __name__ == "__main__":
    
    # Parameters for random distribution for the RF Gradient Offset/Error
    parser = argparse.ArgumentParser()
    parser.add_argument("--mean", type=float, default=0.0, help="Offset Mean [MV/m]")
    parser.add_argument("--stdev", type=float, default=1.0,  help="Offset Mean [MV/m]" )
    parser.add_argument("--sample-size", type=int, default=10,  help="# Trials")
    parser.add_argument("--number-of-particles", type=int, default=2000,  help="# particles in beam")
    args = parser.parse_args()
    
    rfgrad_actual = 22.508192486472524
    mean = rfgrad_actual + args.mean
    stdev = args.stdev
    sample_size = args.sample_size
    
    values = randomgaussdist(mean, stdev, sample_size)
    input_file = "./" + input("please write the name of the g4bl input file: ") + ".g4bl"
    ecalc9f_file = "ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    
    # G4BL VALUES
    
    for i in trange(len(values)):
        g4blresult = run_g4beamline(input_file, values[i] ,i)
        
        if g4blresult:
            print("G4beamline simulation completed successfully.")
    
    # ECALC6F VALUES
    
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
    
    for i in trange(sample_size):
        if os.path.exists("./for009.dat") and i == 0:
            os.rename("./for009.dat", "./for009"+ f"prev"+".txt")
            os.rename("./for009"+ f"_{i}"+".txt", "./for009.dat")
        elif os.path.exists("./for009.dat") and i != 0:
            os.rename("./for009.dat", "./for009"+ f"_{i-1}"+".txt")
            os.rename("./for009"+ f"_{i}"+".txt", "./for009.dat")
        else:
            os.rename("./for009"+ f"_{i}"+".txt", "./for009.dat")

        ecalcresult = run_ecalc9f(ecalc9f_file)
        data_final = np.loadtxt(ecalcfinal_file,skiprows=13, usecols=cols)
        
        # OK, let's collect all eperp, elong, trans data (but then we need to avg over trials)
        zvals.append(data_final[:,1])
        eperps.append(data_final[:,2]*1000)
        elongs.append(data_final[:,3]*1000)
        transs.append(data_final[:,4]/data_final[0,4]*100)
        
    
    if ecalcresult:
            print("Ecalc9f calculations completed successfully.")
    
    # DATA ANALYSIS + PLOTTING
    for a in trange(len(eperps)):
        
        for i in trange(len(eperps[a])):
            p = []
            l = []
            t = []

            for j in trange(len(eperps)):
                p.append(eperps[j][i])
                l.append(elongs[j][i])
                t.append(transs[j][i])
                
            
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
    vals_formatted = [f'{x:.3f}' for x in values]
    plt.errorbar(zvals[0], eperps_avg, xerr = None, yerr = eperps_sem, color='black')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_T$ [mm]")
    plt.title("Transverse Emittance v. Beam Axis (z)")
    plt.figtext(0.5, 0.95, "RF Gradient Values [MW/m]: " + str(vals_formatted), horizontalalignment='center', fontsize=10)
    plt.savefig("./rfgradtol_eperp"+"_sample-size: " + str(sample_size)+".png")
    plt.show()
    
    plt.errorbar(zvals[0], elongs_avg, xerr = None, yerr = elongs_sem, color='black')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_L$ [mm]")
    plt.title("Longitudinal Emittance v. Beam Axis (z)")
    plt.figtext(0.5, 0.95, "RF Gradient Values [MW/m]: " + str(vals_formatted), horizontalalignment='center', fontsize=10)
    plt.savefig("./rfgradtol_elong"+"_sample-size: " + str(sample_size)+".png")
    plt.show()
    
    plt.errorbar(zvals[0], transs_avg, xerr = None, yerr = transs_sem, color='black')
    plt.xlabel("z [m]")
    plt.ylabel("Transmission [%]")
    plt.title("Transmission v. Beam Axis (z)")
    plt.figtext(0.5, 0.95, "RF Gradient Values [MW/m]: " + str(vals_formatted), horizontalalignment='center', fontsize=10)
    plt.savefig("./rfgradtol_trans"+"_sample-size: " + str(sample_size)+".png")
    plt.show()
    
    
            
    
        
