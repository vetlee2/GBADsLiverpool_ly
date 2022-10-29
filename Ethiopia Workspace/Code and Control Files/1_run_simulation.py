#%% About
'''
The University of Liverpool (UoL) has provided R code to run the simulation
compartmental model to estimate the production values and costs for different
species.

This program runs the UoL R code using the subprocess library.
Any R libraries required must be installed first, which I have done through RGui.
- Run RGui as administrator
- In console run: install.packages('package_name')

This code does not need to be run. If UoL has run it, I can retrieve the updated
output files from ETHIOPIA_OUTPUT_FOLDER.
'''

#%% Setup

# =============================================================================
#### Rscript executable
# =============================================================================
# On Lotka
# r_executable = 'C:\\Program Files\\R\\R-4.2.0\\bin\\x64\\Rscript.exe'

# On Local
r_executable = 'C:\\Program Files\\R\\R-4.2.1\\bin\\x64\\Rscript.exe'

#%% Run AHLE simulation
'''
OLD RUN TIMES

N runs | Run time
10       32s
100      1m 53s
1000     14m 40s
'''
# =============================================================================
#### Small ruminants
# =============================================================================
# Full path to the R program you want to run
r_script = os.path.join(PARENT_FOLDER ,'Run AHLE with control table _ Gemma edits for individuals .R')

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
    # Arg 1: Number of simulation runs
    '2'

    # Arg 2: Folder location for saving output files
    ,ETHIOPIA_OUTPUT_FOLDER

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    # 9/28: Gemma removed the code that performed this task
    # ,'-1'
]

timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=99)
timerstop()

# =============================================================================
#### Cattle
# =============================================================================
# Full path to the R program you want to run
r_script = os.path.join(PARENT_FOLDER ,'Run AHLE with control table _ Gemma edits for individuals _CATTLE.R')

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
    # Arg 1: Number of simulation runs
    '1'

    # Arg 2: Folder location for saving output files
    ,ETHIOPIA_OUTPUT_FOLDER

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters CATTLE.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    # 9/28: Gemma removed the code that performed this task
    # ,'-1'
]

timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=99)
timerstop()

# =============================================================================
#### Poultry
# =============================================================================
# Full path to the R program you want to run
r_script = os.path.join(PARENT_FOLDER ,'Run AHLE with control table _ POULTRY.R')

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
    # Arg 1: Number of simulation runs
    '100'

    # Arg 2: Folder location for saving output files
    ,ETHIOPIA_OUTPUT_FOLDER

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters POULTRY.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    ,'-1'
]

timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=99)
timerstop()
