import numpy as np
import matplotlib.pyplot as plt

# Load the file: each column becomes a NumPy array
data = np.loadtxt("./chnbychn.txt").T  # Transpose so columns are easier to access

# Access each column individually (optional)
zvals      = data[0]
eperps_avg      = data[1]
eperps_sem      = data[2]
eperps_noerr     = data[3]
elongs_avg       = data[4]
elongs_sem       = data[5]
elongs_noerr     = data[6]
transs_avg    = data[7]
transs_sem    = data[8]
transs_noerr  = data[9]

stages = np.linspace(1, 8, num=len(zvals))

plt.errorbar(stages, eperps_avg, xerr = None, yerr = eperps_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
plt.plot(stages, eperps_noerr, color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
plt.fill_between(stages, np.array(eperps_avg) - np.array(eperps_sem), np.array(eperps_avg) + np.array(eperps_sem), color='blue', alpha=0.3, label=f'σ = ±1.0, σRFp = ±10.0')
plt.xlabel("Stages (post-merge)")
plt.xticks([1,2,3,4,5,6,7,8])
plt.ylabel(r"$\epsilon_T$ [mm]")
plt.title("Transverse Emittance v. Stages")
plt.grid(True)
plt.legend()
plt.savefig("./tot_varrfgradphtol_eperp.png")
plt.close()

plt.errorbar(stages, elongs_avg, xerr = None, yerr = elongs_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
plt.plot(stages, elongs_noerr, color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
plt.fill_between(stages, np.array(elongs_avg) - np.array(elongs_sem), np.array(elongs_avg) + np.array(elongs_sem), color='blue', alpha=0.3, label=f'σ = ±1.0, σRFp = ±10.0')
plt.xlabel("Stages (post-merge)")
plt.xticks([1,2,3,4,5,6,7,8])
plt.ylabel(r"$\epsilon_L$ [mm]")
plt.title("Longitudinal Emittance v. Stages")
plt.grid(True)
plt.legend()
plt.savefig("./tot_varrfgradphtol_elong.png")
plt.close()

plt.errorbar(stages, transs_avg, xerr = None, yerr = transs_sem, color='black', ecolor='blue', capsize=2.5, capthick=1.5, elinewidth=0.7, linestyle="dashed")
plt.plot(stages, transs_noerr, color = "red", label = "RF gradient = μG (σ = 0), RF phase = μP (σRFp = 0)")
plt.fill_between(stages, np.array(transs_avg) - np.array(transs_sem), np.array(transs_avg) + np.array(transs_sem), color='blue', alpha=0.3, label=f'σ = ±1.0, σRFp = ±10.0')
plt.xlabel("Stages (post-merge)")
plt.xticks([1,2,3,4,5,6,7,8])
plt.ylabel("Transmission [%]")
plt.title("Transmission v. Stages")
plt.grid(True)
plt.legend()
plt.savefig("./tot_varrfgradphtol_trans.png")
plt.close()