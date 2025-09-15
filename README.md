<!---
Theory: This is a standard template that can be used for feature documentation. Using a template helps to reduce cognitive load while reading documentation and to make it easier to find what you are looking for. Some things to think about when writing documentation:

- Think about the audience for this document and what you want them to know
- Favor conciseness and clarity when writing documentation
- Use simple language wherever possible
- Use headings, bullet points, and short paragraphs

Guide: Here is a guide to each section of this document and how to use it:

- Terminology: Add any terminology that you come across when writing up this document that the average person would not know. Consider this from the perspective of someone who does not work within your domain, and what definitions they would need when reading this document to best understand it.
- Feature details: Add a subsection here for any specific details about this feature. Try to group information together in a logical way.
- Troubleshooting: Add any common knowledge on how to troubleshoot this feature here
- FAQ: This is a great spot to add any common questions you have come across while working on this feature
- References: Include any documentation that you know of that is relevant to this feature, such as epics, ADRs, product spec documents, etc.

Checklist: Complete the following while writing up this document
- [ ] Complete the template with all items that are relevant to what you're trying to describe
- [ ] Remove any section that isn't relevant to what you're trying to describe
- [ ] Update the Table of Contents with all relevant sections for easy navigability
- [ ] Edit each section of the document for simplicity, favoring conciseness and clarity. Consider the following:
    - [ ] Could the document be improved with more images?
    - [ ] Could the document be more clear with diagrams, like entity-relationship diagrams?
    - [ ] Could linking to other documents make this document easier to understand?
- [ ] Use the documentation guide to determine where this document should live relative to other documents

-->

# Tolerance Studies for the IMCC Rectilinear 6D Post-Merge Ionization Cooling Channel

This is the repository that contains all work from Summer 2025 onwards involving the development of a G4Beamline simulation for the tolerance study and error analysis of the post-merge part of 6D cooling channel devised as the baseline by the International Muon Collider Collaboration. The aim is to develop design suggestions.
The progress over Summer 2025 for this project is logged daily at: https://tinyurl.com/incis-summer-progress.

## Table of Contents

- [10 TeV Muon Collider and Tolerance Studies](#tolerancestudies)
- [IMCC Design](#rectilinear)
  - [IMCC Rectilinear Channel Introduction](#rectilinear-channel)
  - [IMCC Post-Merge (B) Code](#rectilinear-code)
- [Inci's Current Execution](#incis-rectilinear)
- [References](#references)

## 10 TeV Muon Collider and Tolerance Studies
For the purposes of effectively constructing a 10 TeV center-of-mass Muon Collider, it is crucial to have a cooling section where the goal is to rapidly decrease muon beam emittance to reach the desired luminosity for the eventual $\mu^+$ and $\mu^-$ collision in the acceleration ring. 

We can reduce the beam emittance without violating Liouville's theorem by applying non-conservative forces through collisions with electrons in the low-Z (LH) wedge absorber, a process known as ionization cooling. The International Muon Collider Collaboration (IMCC) has proposed the rectilinear channel to facilitate ionization cooling, which includes solenoids, RF cavities, wedge absorbers, and pipes. However, the specifications we optimize for in our simulations for the solenoids and RF cavities may not be built exactly as we intended. This is why we deliberately introduce deviations to the specs of components one by one to probe the emittance and transmission changes--which is called tolerance studies.

Simulations of both the MAP and the newer IMCC design were made using G4Beamline, a particle tracking simulation program based on the Monte Carlo toolkit GEANT4. Further calculations of transverse and longitudinal emittance, transmission (i.e. what % of particles survive) were done through ECALC9F, file-based version of the post-processing utility ECALC9, which analyses the phase space characteristics of the beam.

## IMCC Design
### IMCC Rectilinear Channel Introduction

In 6D cooling via the IMCC Rectilinear Channel, solenoids are used as focusing magnets. Momentum dispersion is introduced by dipole magnets, and phase space area reduction happens in low-Z (e.g., Liquid Hydrogen) wedge absorbers through ionization. Radiofrequency (RF) cavities reaccelerate the beam to compensate for energy losses in the absorber. In G4Beamline, the dipole magnets are not physically simulated but instead inserted as a field. Fringe fields are also included in the simulation.

### IMCC Post-Merge (B) Code

The newest code for the IMCC Post-Merge can be found in https://github.com/MuonCollider-WG4/rectilinear/tree/main/new_lattice_with_larger_gaps/post_merge. Here, every stage of the 10 stages that make up the post-merge (B) rectilinear channel includes a particle distribution (beam_stage#.beam) that is inserted into that stage's g4beamline file (cooling_stage#.g4bl), and the resulting output will be in for009 format and as for009.dat. This output can be analyzed for the transmission, longitudinal and transverse emittance, etc. values through ECALC9f, which is why ecalc9f.dat and ecalc9f.inp files are also included in each folder. 

However, when one needs to connect all 10 stages to simulate what a physically accurate version of the post-merge rectilinear channel looks like, the authors of the IMCC paper have included a separate file, extreg9.inp, which guides how one should manipulate the output particle distribution (for009.dat) from each stage to get the results discussed in the IMCC paper https://arxiv.org/pdf/2409.02613. More specifically, the 5th column of the "for009.dat" file shows the region number, and you can find "extreg9.inp" in every cooling stage folder. The number in the 3rd row in "extreg9.inp" means the region where the authors have taken out the beam and then used it for the input for the next stage. So, the parameter "ncells" in the g4bl input file doesn't tell you the actual number of cooling cells that are used in one cooling stage, and in fact, the number in "extreg9.inp" does.

## Inci's Current Execution

With the IMCC way of modeling and executing the post-merge rectilinear channel model in g4bl in mind, this GitHub is organized as follows. The folder IMCCrectilinear_postmerge is meant to go through each post-merge stage of the IMCC rectilinear channel one by one (allstages.py), where the output of each space is organized according to the extreg9.inp as described above, with the Python script convertZ.py; no modifications to IMCC files are made. 

The folder RFtoleranceStudy_postmerge is where the IMCC files are actually modified according to the tolerance study methodology also utilized in the IMCC rectilinear channel paper: 1) Generate random errors from a truncated Gaussian distribution with mean being the nominal value of a characteristic (e.g. RF gradient, RF phase, etc. whatever specifications are being tested for tolerance study) and standard deviation being some value between 1% to 10% of the average mean across all stages. 2) Sample 10 or more times. In the IMCC paper, only one stage seems to be tested for these characteristics. Here, tolerance studies are conducted for all 10 stages where the process going from one stage to another is the same IMCCrectilinear_postmerge (i.e. via extreg9.inp as in https://arxiv.org/pdf/2409.02613). So far, only the RF gradient and the RF phase have undergone a tolerance study. There are two folders inside RFtoleranceStudy_postmerge: 1) postmerge_erroranl, which aims to replicate Figure 10(a) and 10(b) in https://arxiv.org/pdf/2409.02613 for all 10 stages, and 2) postmerge_evolutionanl, which plots the evolution of 6D emittance, transmission, longitudinal, and transverse emittance across all 10 stages as a result of RF gradient and phase tolerance studies. Within each folder, the same process occurs, they just produce different plots: tolRFallstages.py loops over tolRFsinglestage.py 10 times while using convertStagePDistribution for the input/output manipulation between each stage in accordance with IMCC and plots the relevant plot (either evolutionanl or erroranl plots). tolRFsinglestage.py takes g4bl files for a stage and inserts RF cavity gradient and phase values according to the Gaussian sampling (the insertion function is written in insertrfforG4BL.py) to each existing RF cavity for that stage.

## References
Stratakis, Diktys, and Robert B. Palmer. “Rectilinear six-dimensional ionization cooling channel for a muon collider: A theoretical and Numerical Study.” Physical Review Special Topics - Accelerators and Beams, vol. 18, no. 3, 6 Mar. 2015, https://doi.org/10.1103/physrevstab.18.031003. 
Zhu, Ruihu, et al. “Design method, performance evaluation, and tolerance analysis of the rectilinear cooling channel for a Muon Collider.” Physical Review Accelerators and Beams, vol. 28, no. 4, 24 Apr. 2025, https://doi.org/10.1103/physrevaccelbeams.28.041003.
Wiedemann, Helmut. Particle Accelerator Physics. Springer International Publishing, 2015. 
Pasternak, J. “6D Cooling for a Muon Collider.” UK Muon Collider and nuStorm - 1st Collaboration Meeting, indico.stfc.ac.uk/event/194/contributions/1443/attachments/367/605/6D_Cooling07082020.pdf.  
Yonehara, Katsuya. “MiniCourse: Accelerator Design for a multi-TeV Muon Collider”, March-June 2025.
“Sketching out a Muon Collider.” CERN Courier, 8 May 2020, cerncourier.com/a/sketching-out-a-muon-collider/.  
