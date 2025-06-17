import subprocess
import shutil
from string import Template
import os

# -------- CONFIG --------
G4BL_TEMPLATE = "incis_cleaned_cooling_stage1.g4bl"
G4BL_INPUT = "run.g4bl"
G4BL_OUTPUT = "for009.dat"       # or whatever G4BL outputs
ECALC_INPUT = "for009.dat"
ECALC_EXEC = "./ecalc9f.exe"
ECALC_OUTPUT = "ecalc9f_output.dat"    # replace with your actual output name
# ------------------------

def write_g4bl_file(params):
    with open(G4BL_TEMPLATE, "r") as f:
        template = Template(f.read())
    filled = template.substitute(
        rf_freq_opt=params[0],
        rf_gradient_opt=params[1],
        rf_phase_opt=params[2],
        rf_window_len_opt=params[3],
        dipole_strength_opt=params[4],
    )
    with open(G4BL_INPUT, "w") as f:
        f.write(filled)

def run_g4bl():
    subprocess.run(["g4bl", G4BL_INPUT], check=True)

def run_ecalc9f():
    # Rename G4BL output to expected ecalc9 input
    shutil.copyfile(G4BL_OUTPUT, ECALC_INPUT)
    subprocess.run([ECALC_EXEC], check=True, stdout=open("ecalc9_output.dat", "w"))

def parse_ecalc_output():
    n0_vals = []
    emit_t_vals = []
    emit_l_vals = []

    current_section = None

    with open(ECALC_OUTPUT, "r") as f:
        for line in f:
            lower_line = line.lower().strip()

            # Detect section headers
            if "n0" in lower_line:
                current_section = "n0"
                continue
            elif "eperp" in lower_line:
                current_section = "eperp"
                continue
            elif "elong" in lower_line:
                current_section = "elong"
                continue

            # Accumulate values under each section
            if current_section and line.strip():
                try:
                    val = float(line.strip().split()[0])  # Use first column
                    if current_section == "n0":
                        n0_vals.append(val)
                    elif current_section == "eperp":
                        emit_t_vals.append(val)
                    elif current_section == "elong":
                        emit_l_vals.append(val)
                except ValueError:
                    pass  # Ignore lines that aren't valid numbers

    # Take last value from each
    trans = float(n0_vals[0])/float(n0_vals[-1]) if n0_vals else float("inf")
    emit_t = float(emit_t_vals[-1]) if emit_t_vals else float("inf")
    emit_l = float(emit_l_vals[-1]) if emit_l_vals else float("inf")

    return trans, emit_t, emit_l

def objective(params):
    try:
        write_g4bl_file(params)
        run_g4bl()
        run_ecalc9f()
        trans, emit_t, emit_l = parse_ecalc_output()

        # Example: maximize transmission, minimize emittance
        score = -trans + 0.1 * (emit_t + emit_l)
        print(score)
        return score

    except Exception as e:
        print("Error in pipeline:", e)
        return 1e6  # Penalize failures
