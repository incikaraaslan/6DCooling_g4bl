import subprocess
import os

def run_g4beamline(input_file):
    try:
        result = subprocess.run(['g4bl', input_file], capture_output=True, text=True, check=True)
        print("G4BL output:")
        print(result.stdout)
        if result.stderr:
            print("G4BL errors:")
            print(result.stderr)
        return result
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running G4beamline: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def run_ecalc9f(input_file):
    try:
        os.rename("./for009.txt", "./for009.dat")
        result = subprocess.run(['./ecalc9f.exe', input_file], capture_output=True, text=True, check=True)
        print("ECALC9F output:")
        print(result.stdout)
        if result.stderr:
            print("ECALC9F errors:")
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running ECALC9F: {e}")
        if e.stderr:
            print(e.stderr)
        return None

if __name__ == "__main__":
    input_file = "./" + input("please write the name of the g4bl input file: ") + ".g4bl"
    ecalc9f_file = "ecalc9f.inp"
    g4blresult = run_g4beamline(input_file)
    
    if g4blresult:
        print("G4beamline simulation completed successfully.")
        ecalcresult = run_ecalc9f(ecalc9f_file)
        if ecalcresult:
            print("Ecalc9f calculations completed successfully.")
        