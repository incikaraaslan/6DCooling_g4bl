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

cols = [2, 3, 4, 5, 6, 7]  # 0-indexed for x,y,z,px,py,pz
data_init = np.loadtxt("initPhase.txt", usecols=cols)
data_final = np.loadtxt("finalPhase.txt", usecols=cols)

fig, ax = plt.subplots(3,2, figsize=(11.0, 16.0))
ax[0,0].scatter(data_init[:,0],data_init[:,3], s=2, alpha=0.5)
ax[0,0].set_xlabel("x [mm]")
ax[0,0].set_ylabel(r"$p_x$ [MeV/c]")
ax[0,0].set_title("Initial Phase Space Distribution in x")
ax[1,0].hist(data_init[:,3], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[1,0].set_xlabel(r"$p_x$ [MeV/c]")
ax[1,0].set_ylabel("Count")
ax[1,0].set_title(r"Histogram for Initial Phase Space Distribution in $p_x$")
ax[2,0].hist(data_init[:,0], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[2,0].set_xlabel("x [mm]")
ax[2,0].set_ylabel("Count")
ax[2,0].set_title("Histogram for Initial Phase Space Distribution in x")
ax[0,1].scatter(data_init[:,0],data_init[:,4], s=2, alpha=0.5)
ax[0,1].set_xlabel("y [mm]")
ax[0,1].set_ylabel(r"$p_y$ [MeV/c]")
ax[0,1].set_title("Initial Phase Space Distribution in y")
ax[1,1].hist(data_init[:,4], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[1,1].set_xlabel(r"$p_y$ [MeV/c]")
ax[1,1].set_ylabel("Count")
ax[1,1].set_title(r"Histogram for Initial Phase Space Distribution in $p_y$")
ax[2,1].hist(data_init[:,1], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[2,1].set_xlabel("y [mm]")
ax[2,1].set_ylabel("Count")
ax[2,1].set_title("Histogram for Initial Phase Space Distribution in y")
plt.savefig("initialPhaseSpace.png")
plt.close()

fig, ax = plt.subplots(3,2, figsize=(11.0, 16.0))
ax[0,0].scatter(data_final[:,0],data_final[:,3], s=2, alpha=0.5)
ax[0,0].set_xlabel("x [mm]")
ax[0,0].set_ylabel(r"$p_x$ [MeV/c]")
ax[0,0].set_title("Final Phase Space Distribution in x")
ax[1,0].hist(data_final[:,3], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[1,0].set_xlabel(r"$p_x$ [MeV/c]")
ax[1,0].set_ylabel("Count")
ax[1,0].set_title(r"Histogram for Final Phase Space Distribution in $p_x$")
ax[2,0].hist(data_final[:,0], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[2,0].set_xlabel("x [mm]")
ax[2,0].set_ylabel("Count")
ax[2,0].set_title("Histogram for Initial Phase Space Distribution in x")
ax[0,1].scatter(data_final[:,1],data_final[:,4], s=2, alpha=0.5)
ax[0,1].set_xlabel("y [mm]")
ax[0,1].set_ylabel(r"$p_y$ [MeV/c]")
ax[0,1].set_title("Final Phase Space Distribution in y")
ax[1,1].hist(data_final[:,4], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[1,1].set_xlabel(r"$p_y$ [MeV/c]")
ax[1,1].set_ylabel("Count")
ax[1,1].set_title(r"Histogram for Final Phase Space Distribution in $p_y$")
ax[2,1].hist(data_final[:,1], bins=64, alpha=0.7, color='b', edgecolor='black')
ax[2,1].set_xlabel("y [mm]")
ax[2,1].set_ylabel("Count")
ax[2,1].set_title("Histogram for Initial Phase Space Distribution in y")
plt.savefig("finalPhaseSpace.png")
plt.close()