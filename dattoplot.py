import argparse
import math
import os
import pathlib

import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

# Load .txt file
filename_input = input("File name (include .txt/.dat):")
filename2_input = input("File name (include .txt/.dat):")
cols = [0,1,3,4]  # 0-indexed for region, z, emittanceperp, emittancelong
data_final = np.loadtxt(filename_input, usecols=cols)
data_final2 = np.loadtxt(filename2_input, usecols=cols)


plt.plot(data_final[:,1],data_final[:,2]*1000, color='black', label = "With Fringe Fields")
plt.plot(data_final2[:,1],data_final2[:,2]*1000, color='red', label = "Without Fringe Fields")
plt.xlabel("z [m]")
plt.ylabel(r"$\epsilon_T$ [mm]")
plt.legend()
plt.title("Transverse Emittance v. Beam Axis (z)")
plt.show()
plt.plot(data_final[:,1],data_final[:,3]*1000, color='black', label = "With Fringe Fields")
plt.plot(data_final2[:,1],data_final2[:,3]*1000, color='red', label = "Without Fringe Fields")
plt.xlabel("z [m]")
plt.ylabel(r"$\epsilon_L$ [mm]")
plt.legend()
plt.title("Longitudinal Emittance v. Beam Axis (z)")
plt.show()