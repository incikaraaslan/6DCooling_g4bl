import numpy as np
import matplotlib.pyplot as plt

# ---- LaTeX Setup for Matplotlib ----
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif",  # Uses Computer Modern by default
    "axes.labelsize": 18,
    "font.size": 16,
    "legend.fontsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.dpi": 300,
    "figure.dpi": 300,
    "text.latex.preamble": r"\usepackage{amsmath}"  # DON'T add newtxtext/newtxmath!
})
# Read the saved file, skip the header row
data = np.loadtxt("results00to025.txt", skiprows=1)

fractional_errors = data[:, 0]
e6ds = data[:, 1]
transmissions = data[:, 2]
eps6D_ci95 = data[:, 3]
trans_ci95 = data[:, 4]

fig, ax1 = plt.subplots()

ax1.set_xlabel('Fractional Gradient Error (MV/m)')#(r'Phase error ($^\circ$)')
ax1.set_ylabel(r'$\epsilon_{6D}$ (mm$^3$)', color='black')
ax1.errorbar(fractional_errors, e6ds, yerr=eps6D_ci95, fmt='s-', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(0.018, 0.034)

ax2 = ax1.twinx()
ax2.set_ylabel('Transmission', color='red')
ax2.errorbar(fractional_errors, transmissions, yerr=trans_ci95, fmt='s-', color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0.06, 0.24)

# plt.grid(True)
plt.tight_layout()
plt.savefig("testfull10stagesplotrf.png",transparent=True)
plt.show()
plt.close()