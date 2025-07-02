import subprocess
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import trange
from varrftol import insert_generated_blocks

def run_g4beamline(input_file, gradients, phases, i):
    try:
        insert_generated_blocks("./g4blfilesin/"+ input_file + ".g4bl", "./g4blfilesout/"+ input_file + f"_{i}_with_cavities.g4bl", gradients, phases)
        result = subprocess.run(['g4bl', "./g4blfilesout/" + input_file + f"_{i}_with_cavities.g4bl", f'filename=for009_{i}', f"last={args.number_of_particles}"], capture_output=True, text=True, check=True)
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
    
    
    mean = rfgrad_actual + args.mean
    stdev = args.stdev
    meanp = rfphase_actual + args.mean
    stdevp = args.stdev_phase

    input_file = "./" + input("please write the name of the g4bl input file: ")
    ecalc9f_file = "ecalc9f.inp"
    ecalcfinal_file = "./ecalc9f.dat"
    
    # G4BL RUN for each sample file (1σ)
    for i in trange(args.sample_size): # THIS IS SUPPOSED TO RUN IT FOR ALL SAMPLE SIZES SO SAMPLE_SIZE, NOT len(values) = 30, values.size = 180 
        values = np.random.normal(mean, stdev, size=(31, 6)) # 30 + 1 due to g4bl shenanigans
        valuesp = np.random.normal(meanp, stdevp, size=(31, 6))
        g4blresult = run_g4beamline(input_file, values, valuesp, i) # (name, 180 values in (30,6), sample #)
        
        if g4blresult:
            print("G4beamline simulation completed successfully.")
    
    # Run No Error Case
    result_noerr = subprocess.run(['g4bl', "./g4blfilesin/incis_cleaned_cooling_stage1.g4bl", f'filename=for009_noerr', f"last={args.number_of_particles}"], capture_output=True, text=True, check=True)
    
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
    
    for i in trange(args.sample_size):
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
    
    zvals_noerr = []
    eperps_noerr = []
    elongs_noerr = []
    transs_noerr = []
    
    # No Err Case
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
        
        print("NOERR G4bl and Ecalc9f calculations completed successfully.")
    
    
    
    plt.errorbar(zvals[0], eperps_avg, xerr = None, yerr = eperps_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(zvals[0], np.asarray(eperps_noerr).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(zvals[0], np.array(eperps_avg) - np.array(eperps_sem), np.array(eperps_avg) + np.array(eperps_sem), color='blue', alpha=0.3, label=f'σ = ±{stdev}, σRFp = ±{stdevp}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_T$ [mm]")
    plt.title("Transverse Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./varrfgradphtol_eperp"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles) + "_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(zvals[0], elongs_avg, xerr = None, yerr = elongs_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(zvals[0], np.asarray(elongs_noerr).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(zvals[0], np.array(elongs_avg) - np.array(elongs_sem), np.array(elongs_avg) + np.array(elongs_sem), color='blue', alpha=0.3, label=f'σ = ±{stdev}, σRFp = ±{stdevp}')
    plt.xlabel("z [m]")
    plt.ylabel(r"$\epsilon_L$ [mm]")
    plt.title("Longitudinal Emittance v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./varrfgradphtol_elong"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles)+"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
    plt.errorbar(zvals[0], transs_avg, xerr = None, yerr = transs_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
    plt.plot(zvals[0], np.asarray(transs_noerr).flatten(), color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
    plt.fill_between(zvals[0], np.array(transs_avg) - np.array(transs_sem), np.array(transs_avg) + np.array(transs_sem), color='blue', alpha=0.3, label=f'σ = ±{stdev}, σRFp = ±{stdevp}')
    plt.xlabel("z [m]")
    plt.ylabel("Transmission [%]")
    plt.title("Transmission v. Beam Axis (z)")
    plt.grid(True)
    plt.legend()
    plt.savefig("./varrfgradphtol_trans"+"_sample-size_" + str(args.sample_size) +"_"+str(args.number_of_particles) +"_"+str(args.stdev)+"_"+str(args.stdev_phase)+".png")
    plt.close()
    
            
    
        
