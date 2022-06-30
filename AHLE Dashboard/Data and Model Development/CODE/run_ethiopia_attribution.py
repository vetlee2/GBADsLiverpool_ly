#%% About
'''
The University of Murdoch has provided R code to attribute the animal health loss envelope
for Ethiopia to 3 components: infectious, non-infectious, and external causes.

This program runs R code using the subprocess library.
Any R libraries required must be installed first, which I have done through RGui.
- Run RGui as administrator
- In console run: install.packages('package_name')
'''

#%% Preliminaries

r_executable = 'C:\\Program Files\\R\\R-4.2.0\\bin\\x64\\Rscript.exe'    # Full path to the Rscript executable

#%% First test
'''
This requires the input files for the program (AHLE.xlsx and data.xlsx) to be in the same directory.
'''

r_script = os.path.join(CURRENT_FOLDER ,'Attribution_20220610 JREDIT.R')    # Full path to the R program you want to run

timerstart()
run_cmd([r_executable ,r_script])
timerstop()
