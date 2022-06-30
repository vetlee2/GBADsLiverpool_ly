#%% About
'''
The University of Liverpool has provided R code to run the simulation compartmental model
for Sheep in the Crop Livestock Mixed (CLM) production system.

This program runs R code using the subprocess library.
Any R libraries required must be installed first, which I have done through RGui.
- Run RGui as administrator
- In console run: install.packages('package_name')

We expect to have other models for:
   - Sheep in the Pastoral production system
   - Goats in both the CLM and Pastoral production systems
These other models are expected to be very similar.
'''

#%% Preliminaries

r_executable = 'C:\\Program Files\\R\\R-4.2.0\\bin\\x64\\Rscript.exe'    # Full path to the Rscript executable

#%% Test basic R script

r_script = os.path.join(CURRENT_FOLDER ,'test_script.R')    # Full path to the R program you want to run
r_args = ['arg_1' ,'arg_2']     # Arguments to R function, as list of strings
run_cmd([r_executable ,r_script] + r_args)

#%% First test
'''
Run without arguments
Changed lines 208 and 1637 to nruns <- 100
Run time: 6 sec
Bonus: this prints plots to Rplots.pdf. I cannot find any line in the code which specifies this file.
'''

# Fixed several "object not found" errors e.g. "object 'AM' not found"
# These were all objects referenced before assignment, so I replaced them with
# similar objects that had been assigned, e.g. replaced 'AM' with 'AM_c'.
r_script = os.path.join(CURRENT_FOLDER ,'CropLivestock Mixed  sheepAHLE model JREDIT.R')    # Full path to the R program you want to run

timerstart()
run_cmd([r_executable ,r_script])
timerstop()

#%% Second test
'''
Pass nruns as argument

N runs | Run time
100      6s
1000     27s
10000    6m 22s
'''

# r_script = os.path.join(CURRENT_FOLDER ,'CropLivestock Mixed  sheepAHLE model JREDIT.R')    # Full path to the R program you want to run
# r_script = os.path.join(CURRENT_FOLDER ,'CropLivestock Mixed  sheepAHLE model JREDIT Functionized.R')    # Full path to the R program you want to run
r_script = os.path.join(CURRENT_FOLDER ,'CropLivestock Mixed  sheepAHLE model JR 20220629.R')    # Full path to the R program you want to run
r_args = [     # Arguments to R function, as list of strings. ORDER MATTERS. SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
   '100'             # Number of simulation runs
   ,EXPDATA_FOLDER   # Location for saving outputs
]

timerstart()
run_cmd([r_executable ,r_script] + r_args)
timerstop()
