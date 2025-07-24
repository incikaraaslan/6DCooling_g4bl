import re

def insert_generated_blocks(input_path, output_path, ):
    with open(input_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'#\s*(\d+)\s+CAVITIES', line)
            if match:
                no_cavs = int(match.group(1))

    # Define markers
    def_start = "# -- START CAVITY DEFINITIONS --"
    def_end = "# -- END CAVITY DEFINITIONS --"
    place_start = "# -- START CAVITY PLACEMENTS --"
    place_end = "# -- END CAVITY PLACEMENTS --"

    # Find indexes for insert locations
    def_start_idx = lines.index(def_start + "\n") + 1
    def_end_idx = lines.index(def_end + "\n")
    place_start_idx = lines.index(place_start + "\n") + 1
    place_end_idx = lines.index(place_end + "\n")

    # Generate cavity definitions
    def_block = []
    for i in range(len(gradients)):
        for j, (grad,ph) in enumerate(zip(gradients[i], phases[i])):
            # def_block.append(f"# Cavity {j} in Cavity Block {i} with gradient {grad} MV/m\n")
            def_block.append(f"pillbox cav{i}{j} innerLength=$rf_length irisRadius=$pipe_radius frequency=$rf_fre maxGradient={grad} phaseAcc={ph} winMat=Be cavityMaterial=$cavity_gas win1Thick=$rf_window_length win2Thick=$rf_window_length wallThick=$wallthick collarThick=0 kill=1")
            def_block.append("\n")
    def_block.append("\n")

    if no_cavs == 6:
        # Generate placement block
        place_block = []
        for i in range(len(gradients)): # Run n cell times each times
            place_block.append(f"\nplace cav{i}0 z={i}*$cell_length+$cell_length/2-(2*$rf_length+2*2*$wallthick+$wallthick+$rf_length/2) rename=rf_a_{i}0 \nplace cav{i}1 z={i}*$cell_length+$cell_length/2-($rf_length+2*$wallthick+$wallthick+$rf_length/2) rename=rf_b_{i}1 \nplace cav{i}2 z={i}*$cell_length+$cell_length/2-($wallthick+$rf_length/2) rename=rf_c_{i}2 \nplace cav{i}3 z={i}*$cell_length+$cell_length/2+($wallthick+$rf_length/2) rename=rf_d_{i}3 \nplace cav{i}4 z={i}*$cell_length+$cell_length/2+($rf_length+2*$wallthick+$wallthick+$rf_length/2) rename=rf_e_{i}4 \nplace cav{i}5 z={i}*$cell_length+$cell_length/2+(2*$rf_length+2*2*$wallthick+$wallthick+$rf_length/2) rename=rf_f_{i}5 \n")
        def_block.append("\n")
        
        # Rebuild file with inserted content
        new_lines = (
            lines[:def_start_idx]
            + def_block
            + lines[def_end_idx:place_start_idx]
            + place_block
            + lines[place_end_idx:]
        )

        with open(output_path, "w") as f:
            f.writelines(new_lines)
    
    elif no_cavs == 5:
        # Generate placement block
        place_block = []
        for i in range(len(gradients)): # Run n cell times each times
            place_block.append(f"\nplace cav{i}0 z={i}*$cell_length+$cell_length/2-(4*$wallthick+2*$rf_length) rename=rf_b_{i}0 \nplace cav{i}1 z={i}*$cell_length+$cell_length/2-(2*$wallthick+$rf_length) rename=rf_c_{i}1\nplace cav{i}2 z={i}*$cell_length+$cell_length/2 rename=rf_d_{i}2 \nplace cav{i}3 z={i}*$cell_length+$cell_length/2+(2*$wallthick+$rf_length) rename=rf_e_{i}3 \nplace cav{i}4 z={i}*$cell_length+$cell_length/2+(4*$wallthick+2*$rf_length) rename=rf_f_{i}4\n")
        def_block.append("\n")
        # Rebuild file with inserted content
        new_lines = (
            lines[:def_start_idx]
            + def_block
            + lines[def_end_idx:place_start_idx]
            + place_block
            + lines[place_end_idx:]
        )

        with open(output_path, "w") as f:
            f.writelines(new_lines)
    
    elif no_cavs == 4:
        # Generate placement block
        place_block = []
        for i in range(len(gradients)): # Run n cell times each times
            place_block.append(f"\nplace cav{i}0 z={i}*$cell_length+$cell_length/2-($rf_length+2*$wallthick+$wallthick+$rf_length/2) rename=rf_b_{i}0 \nplace cav{i}1 z={i}*$cell_length+$cell_length/2-($wallthick+$rf_length/2) rename=rf_c_{i}1 \nplace cav{i}2 z={i}*$cell_length+$cell_length/2+($wallthick+$rf_length/2) rename=rf_d_{i}2 \nplace cav{i}3 z={i}*$cell_length+$cell_length/2+($rf_length+2*$wallthick+$wallthick+$rf_length/2) rename=rf_e_{i}3\n")
        def_block.append("\n")
        # Rebuild file with inserted content
        new_lines = (
            lines[:def_start_idx]
            + def_block
            + lines[def_end_idx:place_start_idx]
            + place_block
            + lines[place_end_idx:]
        )

        with open(output_path, "w") as f:
            f.writelines(new_lines)
    
    elif no_cavs == 3:
        # Generate placement block
        place_block = []
        for i in range(len(gradients)): # Run n cell times each times
            place_block.append(f"\nplace cav{i}0 z={i}*$cell_length+$cell_length/2-(2*$wallthick+$rf_length) rename=rf_c_{i}0 \nplace cav{i}1 z={i}*$cell_length+$cell_length/2 rename=rf_d_{i}1 \nplace cav{i}2 z={i}*$cell_length+$cell_length/2+(2*$wallthick+$rf_length) rename=rf_e_{i}2\n")
        def_block.append("\n")
        # Rebuild file with inserted content
        new_lines = (
            lines[:def_start_idx]
            + def_block
            + lines[def_end_idx:place_start_idx]
            + place_block
            + lines[place_end_idx:]
        )

        with open(output_path, "w") as f:
            f.writelines(new_lines)
    
    else:
        print(f"Error in the number of cavities within each cell, you have {no_cavs} number of cavities instead.")
        
# USER MANUAL (lol)
"""gradients = [[24.00586596, 22.97162972, 22.68531508, 21.59488107, 21.84042006, 22.23430783], [25.03124466, 23.35994608, 23.74424217, 22.27301468, 22.94704933, 22.70687983], [20.65858234, 22.41546774, 23.09293982, 22.91203449, 22.08366004, 21.5020332 ],[22.8346084,  21.56626751, 21.7996121,  23.40608934 ,23.9203137,  24.08566412]]
phases = [[ 17.26902484,  -5.1016164,   -7.84609131,  11.34479744,  12.88698456, 1.76219211], [0.28240336,   2.73403383,  -3.90181116,  -1.3851406,    0.29234236,-2.18776988], [ -8.07993123,  17.32303104,  23.02737228,  12.01571614 ,  6.99142426, 26.11407104],[  1.68960281,   0.30955107,  -2.85123669,  10.53355376,   8.95687002, 13.45700969]]
insert_generated_blocks("incis_cleaned_cooling_stage1_variablerfs.g4bl", "incis_cleaned_cooling_stage1_TEST.g4bl", gradients, phases)"""