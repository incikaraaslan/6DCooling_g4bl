"""

Produces transverse phase space distribution plots from .txt files. The format of the .txt files is assumed to be:
x y z Px Py Pz t PDGid EventID TrackID ParentID Weight 

    
"""

import argparse
import math
import os
import pathlib

import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

# Load .txt file
filename_input = input("File name (include .txt):")
cols = [0, 6, 7, 8, 9, 10, 11]  # 0-indexed for ievt, x,y,z,px,py,pz
data_final = np.loadtxt(filename_input, usecols=cols)

x_fin = []
y_fin = []
px_fin = []
py_fin = []
count = 0

for i in data_final:
    if i[0] == 0.0:
        if count == 0:
            x_fin.append(i[1])
            y_fin.append(i[2])
            px_fin.append(i[4])
            py_fin.append(i[5])
            count += 1
        
        else:
            fig, ax = plt.subplots(3,2, figsize=(13.0, 16.0))
            ax[0,0].scatter(x_fin,px_fin, s=2, alpha=0.5)
            ax[0,0].set_xlabel("x [mm]")
            ax[0,0].set_ylabel(r"$p_x$ [MeV/c]")
            ax[0,0].set_title("Phase Space Distribution in x")
            ax[1,0].hist(px_fin, bins=64, alpha=0.7, color='b', edgecolor='black')
            ax[1,0].set_xlabel(r"$p_x$ [MeV/c]")
            ax[1,0].set_ylabel("Count")
            ax[1,0].set_title(r"Histogram for Phase Space Distribution in $p_x$")
            ax[2,0].hist(x_fin, bins=64, alpha=0.7, color='b', edgecolor='black')
            ax[2,0].set_xlabel("x [mm]")
            ax[2,0].set_ylabel("Count")
            ax[2,0].set_title("Histogram for Phase Space Distribution in x")

            ax[0,1].scatter(y_fin,py_fin, s=2, alpha=0.5)
            ax[0,1].set_xlabel("y [mm]")
            ax[0,1].set_ylabel(r"$p_y$ [MeV/c]")
            ax[0,1].set_title("Phase Space Distribution in y")
            ax[1,1].hist(py_fin, bins=64, alpha=0.7, color='b', edgecolor='black')
            ax[1,1].set_xlabel(r"$p_y$ [MeV/c]")
            ax[1,1].set_ylabel("Count")
            ax[1,1].set_title(r"Histogram for Phase Space Distribution in $p_y$")
            ax[2,1].hist(y_fin, bins=64, alpha=0.7, color='b', edgecolor='black')
            ax[2,1].set_xlabel("y [mm]")
            ax[2,1].set_ylabel("Count")
            ax[2,1].set_title("Histogram for Phase Space Distribution in y")
            
            plt.savefig(filename_input + "_cell_" +str(count) + "_PhaseSpace.png")
            plt.close()
            
            count +=1
            
            x_fin.clear()
            y_fin.clear()
            px_fin.clear()
            py_fin.clear()
            
            x_fin.append(i[1])
            y_fin.append(i[2])
            px_fin.append(i[4])
            py_fin.append(i[5])
    
    elif i[0] != 0.0:
        x_fin.append(i[1])
        y_fin.append(i[2])
        px_fin.append(i[4])
        py_fin.append(i[5])

""" 
# TRANSVERSE X
# Load x, xprime, p data from G4BL
x = px_fin       # mm
xprime = px_fin/pz_fin       # rad
p = np.sqrt(px_fin**2 + py_fin**2 + pz_fin**2)         # MeV/c
p_ref = 200.0   # MeV/c

δ = (p - p_ref) / p_ref

# Centered data
x -= np.mean(x)
xprime -= np.mean(xprime)
δ -= np.mean(δ)

# Moments
var_x   = np.mean(x**2)
var_xprime  = np.mean(xprime**2)
cov_x_xprime = np.mean(x * xprime)
cov_x_δ = np.mean(x * δ)
cov_xprime_δ = np.mean(xprime * δ)
var_δ = np.mean(δ**2)

# Dispersion
D = cov_x_δ / var_δ
Dp = cov_xprime_δ / var_δ

# Remove dispersion
var_x_beta = var_x - D**2 * var_δ
var_xprime_beta = var_xprime - Dp**2 * var_δ
cov_x_xprime_beta = cov_x_xprime - D * Dp * var_δ

# Emittance and Twiss
ε = np.sqrt(np.abs(var_x_beta * var_xprime_beta - cov_x_xprime_beta**2))
β = var_x_beta / ε
γ = var_xprime_beta / ε
α = -cov_x_xprime_beta / ε

# TRANSVERSE Y
# Load y, yprime, p data from G4BL
y = py_fin       # mm
yprime= py_fin/pz_fin       # rad
p = np.sqrt(px_fin**2 + py_fin**2 + pz_fin**2)         # MeV/c
p_ref = 200.0   # MeV/c

δy = (p - p_ref) / p_ref

# Centered data
y -= np.mean(y)
yprime-= np.mean(yprime)
δy -= np.mean(δy)

# Moments
var_y   = np.mean(y**2)
var_yprime = np.mean(yprime**2)
cov_y_yprime= np.mean(y * yprime)
cov_y_δy = np.mean(y * δy)
cov_yprime_δy = np.mean(yprime* δy)
var_δy = np.mean(δy**2)

# Dispersion
Dy = cov_y_δy / var_δy
Dyprime= cov_yprime_δy / var_δy

# Remove dispersion
var_y_beta = var_y - Dy**2 * var_δy
var_yprime_beta = var_yprime- Dyprime**2 * var_δy
cov_y_yprime_beta = cov_y_yprime- Dy * Dyprime* var_δy

# Emittance and Twiss
εy = np.sqrt(np.abs(var_y_beta * var_yprime_beta - cov_y_yprime_beta**2))
βy = var_y_beta / εy
γy = var_yprime_beta / εy
αy = -cov_y_yprime_beta / εy

print("Emittance x: "+ str(ε) + " Emittance y: " + str(εy))
plt.figtext(
    0.5, 0.91, r"$\epsilon_x$: "+ str(ε) + r" $\epsilon_y$: " + str(εy), horizontalalignment='center', fontsize=20
)
plt.savefig(filename_input + "_PhaseSpace.png")
plt.close()
"""