input_file = "beam_stage3_out.txt"     # Replace with your actual filename
output_file = "beam_stage3_upt.txt"   # Output will be saved here

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
            new_line = " ".join(parts)
            outfile.write(new_line + "\n")
        else:
            # Handle lines that don't match expected format
            outfile.write(line)

print(f"Updated file saved as '{output_file}'")