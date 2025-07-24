import os

def extract_region_beam(for009_path, extreg_path, output_path):
    
    # Step 1: Read target region from extreg9.inp
    with open(extreg_path, 'r') as f:
        lines = f.readlines()
        if len(lines) < 3:
            raise ValueError("extreg9.inp does not have enough lines")
        region = int(lines[2].strip())

    # Step 2: Prepare header for G4beamline .beam format
    with open(output_path, 'w') as out:
        out.write("#BLTrackFile solenoid_cooling_channel\n")
        out.write("#x y z Px Py Pz t PDGid EvNum TrkId Parent weight\n")

        # Step 3: Parse for009.dat and extract/convert entries
        with open(for009_path, 'r') as infile:
            for line in infile:
                if line.startswith('#') or not line.strip():
                    continue
                fields = line.strip().split()
                if len(fields) < 18:
                    continue  # skip malformed lines

                jsrg = int(fields[4])
                if jsrg != region:
                    continue

                # Extract values (G4 units: meters & GeV/c → convert)
                t_ns     = float(fields[5]) * 1e9         # ns
                x_mm     = float(fields[6]) * 1000        # mm
                y_mm     = float(fields[7]) * 1000        # mm
                z_mm     = float(fields[8]) * 1000        # mm
                px_MeV   = float(fields[9]) * 1000        # MeV/c
                py_MeV   = float(fields[10]) * 1000
                pz_MeV   = float(fields[11]) * 1000
                weight   = float(fields[15])

                event_id = int(fields[0])
                track_id = int(fields[1])
                parent_id = 0  # or from elsewhere if needed
                pdg_id = -13  # for μ⁺

                out.write(f"{x_mm:.6f} {y_mm:.6f} {z_mm:.6f} {px_MeV:.6f} {py_MeV:.6f} {pz_MeV:.6f} {t_ns:.6f} {pdg_id} {event_id} {track_id} {parent_id} {weight:.6f}\n")

    print(f"Converted region {region} data to G4beamline format in '{output_path}'.")

    """# Step 1: Read region number from 3rd row of extreg9.inp
    with open(extreg_path, 'r') as extreg:
        lines = extreg.readlines()
        if len(lines) < 3:
            raise ValueError("extreg9.inp does not have 3 rows")
        region = int(lines[2].strip())

    # Step 2: Read for009.dat and extract lines matching region
    with open(for009_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            if line.startswith('#'):
                continue  # skip comments
            fields = line.strip().split()
            if len(fields) < 6:
                continue  # malformed line
            jsrg = int(fields[4])  # 5th column (0-indexed)
            if jsrg == region:
                outfile.write(line)

    print(f"✅ Extracted particles from region {region} into '{output_path}'.")"""

def convertZ(input_file, output_file):
    event_id_counter = 1
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            # Skip header lines (those starting with #)
            if line.strip().startswith("#"):
                outfile.write(line)
                continue

            # Split the line into columns
            parts = line.strip().split()
            if len(parts) >= 12:
                parts[2] = "0"  # Set the 3rd column (z) to 0
                # Replace event ID (assuming it's the 9th column, zero-based index 8)
                # Adjust if your event ID is in a different column
                parts[8] = str(event_id_counter)
                event_id_counter += 1
                new_line = " ".join(parts)
                outfile.write(new_line + "\n")
            else:
                # Handle lines that don't match expected format
                outfile.write(line)
    print(f"Updated file saved as '{output_file}'")
    os.remove(input_file)
    return None