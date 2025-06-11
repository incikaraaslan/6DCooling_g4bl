import argparse
import math
import os
import pathlib

import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

# Load .txt file
filename_input = input("File name (include .txt/.dat):")
cols = [0,1,3,4]  # 0-indexed for region, z, emittanceperp, emittancelong
data_final = np.loadtxt(filename_input, usecols=cols)


plt.plot(data_final[:,1],data_final[:,2])
plt.xlabel("z [m]")
plt.ylabel(r"$\epsilon_T$ [m rad]")
plt.title("Transverse Emittance v. Beam Axis (z)")
plt.show()
plt.plot(data_final[:,1],data_final[:,3])
plt.xlabel("z [m]")
plt.ylabel(r"$\epsilon_L$ [m rad]")
plt.title("Longitudinal Emittance v. Beam Axis (z)")
plt.show()