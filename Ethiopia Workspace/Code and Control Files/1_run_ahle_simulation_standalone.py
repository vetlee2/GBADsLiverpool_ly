#%% About
'''
The University of Liverpool (UoL) has provided R code to run the simulation
compartmental model to estimate the production values and costs for different
species.

This program runs the UoL R code using the subprocess library.
Any R libraries required must be installed first, which I have done through RGui.
- Run RGui as administrator
- In console run: install.packages('package_name')

This code does not need to be run if UoL has already run the simulations.
'''
#%% Packages and functions

import os                        # Operating system functions
import subprocess                # For running command prompt or other programs
import inspect                   # For inspecting objects
import datetime as dt            # Date and time functions

# Run a command on the command line using subprocess package
# Example usage: run_cmd(['dir' ,'c:\\users'] ,SHELL=True ,SHOW_MAXLINES=10)
# To run an R program:
   # r_executable = 'C:\\Program Files\\R\\R-4.0.3\\bin\\x64\\Rscript'    # Full path to the Rscript executable
   # r_script = os.path.join(CURRENT_FOLDER ,'test_script.r')             # Full path to the R program you want to run
   # r_args = ['3']                                                       # List of arguments to pass to script, if any
   # run_cmd([r_executable ,r_script] + r_args)
def run_cmd(
      CMD                 # String or List of strings: the command to run. IMPORTANT: use double backslashes (\\) so they are not interpreted as escape characters.
      ,SHELL=False        # True: submit CMD to command prompt (for builtin commands: dir, del, mkdir, etc.). False (default): run another program. First argument in CMD must be an executable.
      ,SHOW_MAXLINES=99
   ):
   funcname = inspect.currentframe().f_code.co_name

   print(f'\n<{funcname}> Running command:\n    {" ".join(CMD)}')
   cmd_status = subprocess.run(CMD, capture_output=True, shell=SHELL)

   stderr_list = []
   stdout_list = []
   if cmd_status.stderr:
      stderr_txt  = cmd_status.stderr.decode()
      stderr_list = stderr_txt.strip().splitlines()
      print(f'\n<{funcname}> stderr messages:')
      for line in stderr_list:
         print(f'    {line}')
   if cmd_status.stdout:
      stdout_txt  = cmd_status.stdout.decode()
      stdout_list = stdout_txt.strip().splitlines()
   if SHOW_MAXLINES:
      print(f'\n<{funcname}> stdout messages (max={SHOW_MAXLINES}):')
      for line in stdout_list[:SHOW_MAXLINES]:
         print(f'    {line}')
   print(f'<{funcname}> Ended with returncode = {cmd_status.returncode}')

   return None    # If you want to use something that is returned, add it here. Assign it when you call the function e.g. returned_object = run_cmd().

# To time a piece of code
def timerstart(LABEL=None):      # String (opt): add a label to the printed timer messages
   global _timerstart ,_timerstart_label
   funcname = inspect.currentframe().f_code.co_name
   _timerstart_label = LABEL
   _timerstart = dt.datetime.now()
   if _timerstart_label:
      print(f"\n<{funcname}> {_timerstart_label} {_timerstart :%I:%M:%S %p} \n")
   else:
      print(f"\n<{funcname}> {_timerstart :%I:%M:%S %p} \n")
   return None

def timerstop():
   global _timerstop
   funcname = inspect.currentframe().f_code.co_name
   if '_timerstart' in globals():
      _timerstop = dt.datetime.now()
      elapsed = _timerstop - _timerstart
      hours = (elapsed.days * 24) + (elapsed.seconds // 3600)
      minutes = (elapsed.seconds % 3600) // 60
      seconds = (elapsed.seconds % 60) + (elapsed.microseconds / 1000000)
      print(f"\n<{funcname}> {_timerstop :%I:%M:%S %p}")
      if _timerstart_label:
         print(f"<{funcname}> {_timerstart_label} Elapsed {hours}h: {minutes}m: {seconds :.1f}s \n")
      else:
         print(f"<{funcname}> Elapsed {hours}h: {minutes}m: {seconds :.1f}s \n")
   else:
      print(f"<{funcname}> Error: no start time defined. Call timerstart() first.")
   return None

#%% Define folder paths

CURRENT_FOLDER = os.getcwd()
PARENT_FOLDER = os.path.dirname(CURRENT_FOLDER)

# Folder for shared code with Liverpool
ETHIOPIA_CODE_FOLDER = CURRENT_FOLDER
ETHIOPIA_OUTPUT_FOLDER = os.path.join(PARENT_FOLDER ,'Program outputs')
ETHIOPIA_DATA_FOLDER = os.path.join(PARENT_FOLDER ,'Data')

# Full path to rscript.exe
r_executable = 'C:\\Program Files\\R\\R-4.2.1\\bin\\x64\\Rscript.exe'

#%% Run AHLE simulation - Small ruminants

# =============================================================================
#### Using Gemma's original AHLE function
# =============================================================================
# Full path to the R program you want to run
r_script = os.path.join(PARENT_FOLDER ,'Run AHLE with control table_SMALLRUMINANTS.R')

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
    # Arg 1: Number of simulation runs
    '10'

    # Arg 2: Folder location for saving output files
    ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle SMALL RUMINANTS')

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters SMALLRUMINANTS.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    # 9/28: Gemma removed the code that performed this task
    # ,'-1'
]
timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=999)
timerstop()

# =============================================================================
#### Using Stephen's updated AHLE function
# =============================================================================
# This file defines the function
r_script = os.path.join(CURRENT_FOLDER ,'ahle_sr.R')
run_cmd([r_executable ,r_script] ,SHOW_MAXLINES=999)

# Now call the function and pass arguments

#%% Run AHLE simulation - Cattle

# Full path to the R program you want to run
r_script = os.path.join(PARENT_FOLDER ,'Run AHLE with control table_CATTLE.R')

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
    # Arg 1: Number of simulation runs
    '10'

    # Arg 2: Folder location for saving output files
    ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle CATTLE' ,'2017')

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'2017_AHLE scenario parameters CATTLE_20230209.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    ,'-1'
]
timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=999)
timerstop()

#%% Run AHLE simulation - Poultry

# Full path to the R program you want to run
r_script = os.path.join(PARENT_FOLDER ,'Run AHLE with control table _ POULTRY.R')

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
    # Arg 1: Number of simulation runs
    '10'

    # Arg 2: Folder location for saving output files
    ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle POULTRY')

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters POULTRY.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    ,'-1'
]
timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=999)
timerstop()
