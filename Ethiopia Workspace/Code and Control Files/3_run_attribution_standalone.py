#%% About
'''
This runs the R program provided by the University of Murdoch to estimate
attribution of the AHLE.

The attribution relies on expert opinions which are recorded in CSV files.
There is a separate expert opinion file for each species or group:
    Small ruminants (sheep and goats)
    Cattle
    Poultry

There are also differences in the production systems and age classes for
each species which require differences in the code to prepare AHLE outputs
for the attribution function.

This code separates the AHLE output by species and processes each one individually.
It then calls the attribution function separately, once for each species or group,
before concatenating the results into a single file for export.
'''
#%% Packages and functions

import os                        # Operating system functions
import subprocess                # For running command prompt or other programs
import inspect                   # For inspecting objects
import io
import time
import datetime as dt            # Date and time functions
import numpy as np
import pandas as pd
import pickle                    # To save objects to disk

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

# To print df.info() with header for readability, and optionally write data info to text file
def datainfo(
      INPUT_DF
      ,OUTFOLDER=None     # String (opt): folder to output {dataname}_info.txt. If None, no file will be created.
   ):
   funcname = inspect.currentframe().f_code.co_name
   dataname = [x for x in globals() if globals()[x] is INPUT_DF][0]
   rowcount = INPUT_DF.shape[0]
   colcount = INPUT_DF.shape[1]
   idxcols = str(list(INPUT_DF.index.names))
   header = f"Data name: {dataname :>26s}\nRows:      {rowcount :>26,}\nColumns:   {colcount :>26,}\nIndex:     {idxcols :>26s}\n"
   divider = ('-'*26) + ('-'*11) + '\n'
   bigdivider = ('='*26) + ('='*11) + '\n'
   print(bigdivider + header + divider)
   INPUT_DF.info()
   print(divider + f"End:       {dataname:>26s}\n" + bigdivider)

   if OUTFOLDER:     # If something has been passed to OUTFOLDER parameter
      filename = f"{dataname}_info"
      print(f"\n<{funcname}> Creating file {OUTFOLDER}\{filename}.txt")
      datetimestamp = 'Created on ' + time.strftime('%Y-%m-%d %X', time.gmtime()) + ' UTC' + '\n'
      buffer = io.StringIO()
      INPUT_DF.info(buf=buffer, max_cols=colcount)
      filecontents = header + divider + datetimestamp + buffer.getvalue()
      tofile = os.path.join(OUTFOLDER, f"{filename}.txt")
      with open(tofile, 'w', encoding='utf-8') as f: f.write(filecontents)
      print(f"<{funcname}> ...done.")
   return None

# To clean up column names in a dataframe
def cleancolnames(INPUT_DF):
   # Comments inside the statement create errors. Putting all comments at the top.
   # Convert to lowercase
   # Strip leading and trailing spaces, then replace spaces with underscore
   # Replace slashes, parenthesis, and brackets with underscore
   # Replace some special characters with underscore
   # Replace other special characters with words
   INPUT_DF.columns = INPUT_DF.columns.str.lower() \
      .str.strip().str.replace(' ' ,'_' ,regex=False) \
      .str.replace('/' ,'_' ,regex=False).str.replace('\\' ,'_' ,regex=False) \
      .str.replace('(' ,'_' ,regex=False).str.replace(')' ,'_' ,regex=False) \
      .str.replace('[' ,'_' ,regex=False).str.replace(']' ,'_' ,regex=False) \
      .str.replace('{' ,'_' ,regex=False).str.replace('}' ,'_' ,regex=False) \
      .str.replace('!' ,'_' ,regex=False).str.replace('?' ,'_' ,regex=False) \
      .str.replace('-' ,'_' ,regex=False).str.replace('+' ,'_' ,regex=False) \
      .str.replace('^' ,'_' ,regex=False).str.replace('*' ,'_' ,regex=False) \
      .str.replace('.' ,'_' ,regex=False).str.replace(',' ,'_' ,regex=False) \
      .str.replace('|' ,'_' ,regex=False).str.replace('#' ,'_' ,regex=False) \
      .str.replace('>' ,'_gt_' ,regex=False) \
      .str.replace('<' ,'_lt_' ,regex=False) \
      .str.replace('=' ,'_eq_' ,regex=False) \
      .str.replace('@' ,'_at_' ,regex=False) \
      .str.replace('$' ,'_dol_' ,regex=False) \
      .str.replace('%' ,'_pct_' ,regex=False) \
      .str.replace('&' ,'_and_' ,regex=False)
   return None

#%% Define folder paths

CURRENT_FOLDER = os.getcwd()
PARENT_FOLDER = os.path.dirname(CURRENT_FOLDER)
GRANDPARENT_FOLDER = os.path.dirname(PARENT_FOLDER)

# Folder for shared code with Liverpool
ETHIOPIA_CODE_FOLDER = CURRENT_FOLDER
ETHIOPIA_OUTPUT_FOLDER = os.path.join(PARENT_FOLDER ,'Program outputs')
ETHIOPIA_DATA_FOLDER = os.path.join(PARENT_FOLDER ,'Data')

DASH_DATA_FOLDER = os.path.join(GRANDPARENT_FOLDER, 'AHLE Dashboard' ,'Dash App' ,'data')

# Full path to rscript.exe
r_executable = 'C:\\Program Files\\R\\R-4.2.1\\bin\\x64\\Rscript.exe'

#%% Data prep

# =============================================================================
#### Read currency conversion data
# =============================================================================
# Note: this is created in 2_process_simulation_results_standalone.py
exchg_data_tomerge = pd.read_pickle(os.path.join(ETHIOPIA_DATA_FOLDER ,'wb_exchg_data_processed.pkl.gz'))

#%% Run Attribution using example inputs

# r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function.R')    # Full path to the R program you want to run
#
# # Arguments to R function, as list of strings.
# # ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
# r_args = [
#     os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function input - example AHLE.csv')                # String: full path to AHLE estimates file (csv)
#     ,os.path.join(ETHIOPIA_CODE_FOLDER ,'attribution_experts_smallruminants.csv')               # String: full path to expert opinion attribution file (csv)
#     ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_example.csv')    # String: full path to output file (csv)
# ]
#
# timerstart()
# run_cmd([r_executable ,r_script] + r_args)
# timerstop()

#%% Read data and restructure
'''
Restructuring is the same for all species.
'''
# =============================================================================
#### Read data
# =============================================================================
ahle_combo_scensmry_withahle_sub = pd.read_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry_ahle.pkl.gz'))
datainfo(ahle_combo_scensmry_withahle_sub)

#!!! Until I can incorporate yearly data into this, apply a top-level filter for a single year
ahle_combo_scensmry_withahle_sub = ahle_combo_scensmry_withahle_sub.query("year == 2021")

# =============================================================================
#### Fill in missing components
# =============================================================================
#!!! Come back to this
'''
With the exception of adults for small ruminants, the expert attribution files
use combined-sex groups for all species and age groups.

Combined-sex AHLE components will be missing for some species and ages depending
on the scenarios run in the simulation model.  While these cannot be calculated
exactly outside of the simulation model, I will fill in values here based on
the scenarios that are present.
'''
# # Split age and sex groups into their own columns
# ahle_combo_scensmry_withahle_sub[['age_group' ,'sex']] = \
#     ahle_combo_scensmry_withahle_sub['agesex_scenario'].str.split(' ' ,expand=True)

# # For each species, production system, and age group, fill in the Combined sex result based on the Male and Female results
# for SPECIES in ahle_combo_scensmry_withahle_sub['species'].unique():
#     _species = (ahle_combo_scensmry_withahle_sub['species'] == SPECIES)
#     for PRODSYS in ahle_combo_scensmry_withahle_sub.loc[_species ,'production_system'].unique():
#         _prodsys = (ahle_combo_scensmry_withahle_sub['production_system'] == PRODSYS)
#         for AGEGRP in ['Adult' ,'Juvenile' ,'Neonatal']:
#             _agegrp = (ahle_combo_scensmry_withahle_sub['age_group'] == AGEGRP)
#             print(f'> {SPECIES=} {PRODSYS=} {AGEGRP=}')
#             print(ahle_combo_scensmry_withahle_sub.loc[_species & _prodsys & _agegrp ,'ahle_total_mean'])

# Recalculate AHLE due to production loss
'''
ahle_dueto_productionloss_mean = ahle_total_mean - ahle_dueto_mortality_mean - ahle_dueto_healthcost_mean
'''

# =============================================================================
#### Restructure for Attribution function
# =============================================================================
ahle_combo_forattr_means = ahle_combo_scensmry_withahle_sub.melt(
   id_vars=['species' ,'production_system' ,'agesex_scenario']
   ,value_vars=['ahle_dueto_mortality_mean' ,'ahle_dueto_healthcost_mean' ,'ahle_dueto_productionloss_mean']
   ,var_name='ahle_component'
   ,value_name='mean'
)
ahle_combo_forattr_stdev = ahle_combo_scensmry_withahle_sub.melt(
   id_vars=['species' ,'production_system' ,'agesex_scenario']
   ,value_vars=['ahle_dueto_mortality_stdev' ,'ahle_dueto_healthcost_stdev' ,'ahle_dueto_productionloss_stdev']
   ,var_name='ahle_component'
   ,value_name='stdev'
)

# Rename AHLE components to match expert opinion file (data.csv)
simplify_ahle_comps = {
   "ahle_dueto_mortality_mean":"Mortality"
   ,"ahle_dueto_healthcost_mean":"Health cost"
   ,"ahle_dueto_productionloss_mean":"Production loss"

   ,"ahle_dueto_mortality_stdev":"Mortality"
   ,"ahle_dueto_healthcost_stdev":"Health cost"
   ,"ahle_dueto_productionloss_stdev":"Production loss"
}
ahle_combo_forattr_means['ahle_component'] = ahle_combo_forattr_means['ahle_component'].replace(simplify_ahle_comps)
ahle_combo_forattr_stdev['ahle_component'] = ahle_combo_forattr_stdev['ahle_component'].replace(simplify_ahle_comps)

# Merge means and standard deviations
ahle_combo_forattr_1 = pd.merge(
   left=ahle_combo_forattr_means
   ,right=ahle_combo_forattr_stdev
   ,on=['species' ,'production_system' ,'agesex_scenario' ,'ahle_component']
   ,how='outer'
)
del ahle_combo_forattr_means ,ahle_combo_forattr_stdev

# Add variance column for summing
ahle_combo_forattr_1['variance'] = ahle_combo_forattr_1['stdev']**2

# =============================================================================
#### Drop unneeded rows
# =============================================================================
'''
Regardless of species, attribution function does not need aggregate production
system or age class.
'''
_droprows = (ahle_combo_forattr_1['production_system'].str.upper() == 'OVERALL') \
    | (ahle_combo_forattr_1['agesex_scenario'].str.upper() == 'OVERALL')
print(f"> Dropping {_droprows.sum() :,} rows where production system or agesex are 'Overall'.")
ahle_combo_forattr_1 = ahle_combo_forattr_1.drop(ahle_combo_forattr_1.loc[_droprows].index).reset_index(drop=True)

# =============================================================================
#### Adjust Mortality AHLE
# =============================================================================
'''
Mortality AHLE results are non-sex-specific for Juveniles and Neonates. This is
due to the way scenarios are defined, and is true for all species.
'''
# Keep only one sex
_droprows = (ahle_combo_forattr_1['ahle_component'] == 'Mortality') \
    & (ahle_combo_forattr_1['agesex_scenario'].isin(['Juvenile Male' ,'Neonatal Male']))
print(f"> Dropping {_droprows.sum() :,} rows.")
ahle_combo_forattr_1 = ahle_combo_forattr_1.drop(ahle_combo_forattr_1.loc[_droprows].index).reset_index(drop=True)

# Change group label
relabel_mort = {
    "Juvenile Female": "Juvenile Combined"
    ,"Neonatal Female": "Neonatal Combined"
    }
_mortrows = (ahle_combo_forattr_1['ahle_component'] == 'Mortality')
ahle_combo_forattr_1.loc[_mortrows] = ahle_combo_forattr_1.loc[_mortrows].replace(relabel_mort)

# Drop duplicates
# Different processing for different species may have produced duplicates
ahle_combo_forattr_1 = ahle_combo_forattr_1.drop_duplicates(
 	subset=['species' ,'production_system' ,'agesex_scenario' ,'ahle_component']
 	,keep='first'                   # String: which occurrence to keep, 'first' or 'last'
)

#%% Prep for Attribution - Small Ruminants
'''
For sheep and goats, the expert attribution file uses non-sex-specific Juvenile
and Neonatal groups, while the compartmental model produces sex-specific scenarios.
'''
# =============================================================================
#### Subset data to correct species
# =============================================================================
_row_selection = (ahle_combo_forattr_1['species'].str.upper().isin(['SHEEP' ,'GOAT']))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_smallrum = ahle_combo_forattr_1.loc[_row_selection].reset_index(drop=True)

# =============================================================================
#### Create aggregate groups
#!!! Note: I am using the SUM here even though AHLE estimates don't exactly sum
# over agesex scenarios. This is because there is no way to exactly estimate the
# AHLE for a scenario that hasn't been run through the simulation model.
# =============================================================================
# -----------------------------------------------------------------------------
# Combine sexes for Juveniles and Neonates
# Does not apply to Mortality
# -----------------------------------------------------------------------------
# Juveniles
_agg_juv = (ahle_combo_forattr_smallrum['agesex_scenario'].str.contains('Juvenile')) \
    & (ahle_combo_forattr_smallrum['ahle_component'] != 'Mortality')
ahle_combo_forattr_smallrum_aggjuv = ahle_combo_forattr_smallrum.loc[_agg_juv].pivot_table(
	index=['species' ,'production_system' ,'ahle_component']
	,values=['mean' ,'variance']
	,aggfunc='sum'
)
ahle_combo_forattr_smallrum_aggjuv = ahle_combo_forattr_smallrum_aggjuv.reset_index()         # Pivoting will change columns to indexes. Change them back.
ahle_combo_forattr_smallrum_aggjuv['agesex_scenario'] = 'Juvenile Combined'
ahle_combo_forattr_smallrum_aggjuv['stdev'] = np.sqrt(ahle_combo_forattr_smallrum_aggjuv['variance'])

# Neonates
_agg_neo = (ahle_combo_forattr_smallrum['agesex_scenario'].str.contains('Neonatal')) \
    & (ahle_combo_forattr_smallrum['ahle_component'] != 'Mortality')
ahle_combo_forattr_smallrum_aggneo = ahle_combo_forattr_smallrum.loc[_agg_neo].pivot_table(
	index=['species' ,'production_system' ,'ahle_component']
	,values=['mean' ,'variance']
	,aggfunc='sum'
)
ahle_combo_forattr_smallrum_aggneo = ahle_combo_forattr_smallrum_aggneo.reset_index()         # Pivoting will change columns to indexes. Change them back.
ahle_combo_forattr_smallrum_aggneo['agesex_scenario'] = 'Neonatal Combined'
ahle_combo_forattr_smallrum_aggneo['stdev'] = np.sqrt(ahle_combo_forattr_smallrum_aggneo['variance'])

# Concatenate with original
ahle_combo_forattr_smallrum_base = ahle_combo_forattr_smallrum.loc[~ _agg_juv].loc[~ _agg_neo]  # Drop rows to avoid duplicates
ahle_combo_forattr_smallrum = pd.concat(
    [ahle_combo_forattr_smallrum_base ,ahle_combo_forattr_smallrum_aggjuv ,ahle_combo_forattr_smallrum_aggneo]
	,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
	,join='outer'        # 'outer': keep all index values from all data frames
	,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_forattr_smallrum_base ,ahle_combo_forattr_smallrum_aggjuv ,ahle_combo_forattr_smallrum_aggneo

# Fill in missing standard deviations with zero
ahle_combo_forattr_smallrum['stdev'] = ahle_combo_forattr_smallrum['stdev'].replace(np.nan ,0)

# Drop variance column
ahle_combo_forattr_smallrum = ahle_combo_forattr_smallrum.drop(columns=['variance'])

# =============================================================================
#### Filter groups and rename
# =============================================================================
# -----------------------------------------------------------------------------
# Agesex groups
# -----------------------------------------------------------------------------
groups_for_attribution = {
   'Adult Female':'Adult female'
   ,'Adult Male':'Adult male'
   ,'Juvenile Combined':'Juvenile'
   ,'Neonatal Combined':'Neonate'
}
groups_for_attribution_upper = [i.upper() for i in list(groups_for_attribution)]

# Filter agesex groups
_row_selection = (ahle_combo_forattr_smallrum['agesex_scenario'].str.upper().isin(groups_for_attribution_upper))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_smallrum = ahle_combo_forattr_smallrum.loc[_row_selection].reset_index(drop=True)

# Rename groups to match attribution code
ahle_combo_forattr_smallrum['agesex_scenario'] = ahle_combo_forattr_smallrum['agesex_scenario'].replace(groups_for_attribution)

# =============================================================================
#### Cleanup and export
# =============================================================================
# Rename columns to match attribution code
# This also specifies the ordering of the columns
colnames = {
   "species":"Species"
   ,"production_system":"Production system"
   ,"agesex_scenario":"Age class"
   ,"ahle_component":"AHLE"
   ,"mean":"mean"
   ,"stdev":"sd"
}
ahle_combo_forattr_smallrum = ahle_combo_forattr_smallrum[list(colnames)].rename(columns=colnames)

# Write CSV
ahle_combo_forattr_smallrum.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_smallrum.csv') ,index=False)

#%% Prep for Attribution - Cattle
'''
For cattle, expert attribution file:
    - Uses non-sex-specific groups for all ages, while the AHLE scenarios are sex-specific for all ages.
    - Has an additional group 'oxen'
    - Has different labels for groups:
        'Juvenile' maps to 'Neonate' in the AHLE file
        'Sub-adult' maps to 'Juvenile' in the AHLE file
'''
# =============================================================================
#### Subset data to correct species
# =============================================================================
_row_selection = (ahle_combo_forattr_1['species'].str.upper() == 'CATTLE')
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_cattle = ahle_combo_forattr_1.loc[_row_selection].reset_index(drop=True)

# =============================================================================
#### Create aggregate groups
#!!! Note: I am using the SUM here even though AHLE estimates don't exactly sum
# over agesex scenarios. This is because there is no way to exactly estimate the
# AHLE for a scenario that hasn't been run through the simulation model.
# =============================================================================
# -----------------------------------------------------------------------------
# Combine sexes for Juveniles, Neonates, and Adults
# -----------------------------------------------------------------------------
# Juveniles
# Does not apply to mortality
_agg_juv = (ahle_combo_forattr_cattle['agesex_scenario'].str.contains('Juvenile')) \
    & (ahle_combo_forattr_cattle['ahle_component'] != 'Mortality')
ahle_combo_forattr_cattle_aggjuv = ahle_combo_forattr_cattle.loc[_agg_juv].pivot_table(
	index=['species' ,'production_system' ,'ahle_component']
	,values=['mean' ,'variance']
	,aggfunc='sum'
)
ahle_combo_forattr_cattle_aggjuv = ahle_combo_forattr_cattle_aggjuv.reset_index()         # Pivoting will change columns to indexes. Change them back.
ahle_combo_forattr_cattle_aggjuv['agesex_scenario'] = 'Juvenile Combined'
ahle_combo_forattr_cattle_aggjuv['stdev'] = np.sqrt(ahle_combo_forattr_cattle_aggjuv['variance'])

# Neonates
# Does not apply to mortality
_agg_neo = (ahle_combo_forattr_cattle['agesex_scenario'].str.contains('Neonatal')) \
    & (ahle_combo_forattr_cattle['ahle_component'] != 'Mortality')
ahle_combo_forattr_cattle_aggneo = ahle_combo_forattr_cattle.loc[_agg_neo].pivot_table(
	index=['species' ,'production_system' ,'ahle_component']
	,values=['mean' ,'variance']
	,aggfunc='sum'
)
ahle_combo_forattr_cattle_aggneo = ahle_combo_forattr_cattle_aggneo.reset_index()         # Pivoting will change columns to indexes. Change them back.
ahle_combo_forattr_cattle_aggneo['agesex_scenario'] = 'Neonatal Combined'
ahle_combo_forattr_cattle_aggneo['stdev'] = np.sqrt(ahle_combo_forattr_cattle_aggneo['variance'])

# Adults
# Including mortality
_agg_adt = (ahle_combo_forattr_cattle['agesex_scenario'].str.contains('Adult'))
ahle_combo_forattr_cattle_aggadt = ahle_combo_forattr_cattle.loc[_agg_adt].pivot_table(
	index=['species' ,'production_system' ,'ahle_component']
	,values=['mean' ,'variance']
	,aggfunc='sum'
)
ahle_combo_forattr_cattle_aggadt = ahle_combo_forattr_cattle_aggadt.reset_index()         # Pivoting will change columns to indexes. Change them back.
ahle_combo_forattr_cattle_aggadt['agesex_scenario'] = 'Adult Combined'
ahle_combo_forattr_cattle_aggadt['stdev'] = np.sqrt(ahle_combo_forattr_cattle_aggadt['variance'])

# Concatenate with original
ahle_combo_forattr_cattle_base = ahle_combo_forattr_cattle.loc[~ _agg_juv].loc[~ _agg_neo].loc[~ _agg_adt]
ahle_combo_forattr_cattle = pd.concat(
    [ahle_combo_forattr_cattle_base ,ahle_combo_forattr_cattle_aggjuv ,ahle_combo_forattr_cattle_aggneo ,ahle_combo_forattr_cattle_aggadt]
	,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
	,join='outer'        # 'outer': keep all index values from all data frames
	,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_forattr_cattle_base ,ahle_combo_forattr_cattle_aggjuv ,ahle_combo_forattr_cattle_aggneo ,ahle_combo_forattr_cattle_aggadt

# Fill in missing standard deviations with zero
ahle_combo_forattr_cattle['stdev'] = ahle_combo_forattr_cattle['stdev'].replace(np.nan ,0)

# Drop variance column
ahle_combo_forattr_cattle = ahle_combo_forattr_cattle.drop(columns=['variance'])

# =============================================================================
#### Filter groups and rename
# =============================================================================
# -----------------------------------------------------------------------------
# Agesex groups
# -----------------------------------------------------------------------------
groups_for_attribution = {
   'Adult Combined':'Adult'
   ,'Juvenile Combined':'Sub-adult'
   ,'Neonatal Combined':'Juvenile'
   ,'Oxen':'Oxen'
}
groups_for_attribution_upper = [i.upper() for i in list(groups_for_attribution)]

# Filter
_row_selection = (ahle_combo_forattr_cattle['agesex_scenario'].str.upper().isin(groups_for_attribution_upper))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_cattle = ahle_combo_forattr_cattle.loc[_row_selection].reset_index(drop=True)

# Rename to match attribution code
ahle_combo_forattr_cattle['agesex_scenario'] = ahle_combo_forattr_cattle['agesex_scenario'].replace(groups_for_attribution)

# -----------------------------------------------------------------------------
# Production systems
# -----------------------------------------------------------------------------
prodsys_for_attribution = {
    'Crop livestock mixed':'Crop livestock mixed'
    ,'Pastoral':'Pastoral'
    ,'Periurban dairy':'Dairy'
}
prodsys_for_attribution_upper = [i.upper() for i in list(prodsys_for_attribution)]

# Filter
_row_selection = (ahle_combo_forattr_cattle['production_system'].str.upper().isin(prodsys_for_attribution_upper))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_cattle = ahle_combo_forattr_cattle.loc[_row_selection].reset_index(drop=True)

# Rename to match attribution code
ahle_combo_forattr_cattle['production_system'] = ahle_combo_forattr_cattle['production_system'].replace(prodsys_for_attribution)

# =============================================================================
#### Cleanup and export
# =============================================================================
# Rename columns to match attribution code
# This also specifies the ordering of the columns
colnames = {
   "species":"Species"
   ,"production_system":"Production system"
   ,"agesex_scenario":"Age class"
   ,"ahle_component":"AHLE"
   ,"mean":"mean"
   ,"stdev":"sd"
}
ahle_combo_forattr_cattle = ahle_combo_forattr_cattle[list(colnames)].rename(columns=colnames)

# Write CSV
ahle_combo_forattr_cattle.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_cattle.csv') ,index=False)

#%% Prep for Attribution - Poultry
'''
For poultry, expert attribution file:
    - Uses non-sex-specific groups for all ages. This matches the AHLE scenarios.
    - Has different labels for groups:
        'Chick' maps to 'Neonate' in the AHLE file
'''
# =============================================================================
#### Subset data to correct species
# =============================================================================
_row_selection = (ahle_combo_forattr_1['species'].str.upper().isin(['POULTRY HYBRID' ,'POULTRY INDIGENOUS']))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_poultry = ahle_combo_forattr_1.loc[_row_selection].reset_index(drop=True)

# =============================================================================
#### Create aggregate groups
# =============================================================================
# -----------------------------------------------------------------------------
# Combine subspecies (hybrid and indegenous)
# -----------------------------------------------------------------------------
ahle_combo_forattr_poultry = ahle_combo_forattr_poultry.pivot_table(
	index=['production_system' ,'agesex_scenario' ,'ahle_component']
	,values=['mean' ,'variance']
	,aggfunc='sum'
)
ahle_combo_forattr_poultry = ahle_combo_forattr_poultry.reset_index()         # Pivoting will change columns to indexes. Change them back.
ahle_combo_forattr_poultry['species'] = 'All Poultry'
ahle_combo_forattr_poultry['stdev'] = np.sqrt(ahle_combo_forattr_poultry['variance'])

# Drop variance column
ahle_combo_forattr_poultry = ahle_combo_forattr_poultry.drop(columns=['variance'])

# =============================================================================
#### Filter groups and rename
# =============================================================================
# -----------------------------------------------------------------------------
# Agesex groups
# -----------------------------------------------------------------------------
groups_for_attribution = {
   'Adult Combined':'Adult'
   ,'Juvenile Combined':'Juvenile'
   ,'Neonatal Combined':'Chick'
}
groups_for_attribution_upper = [i.upper() for i in list(groups_for_attribution)]

# Filter agesex groups
_row_selection = (ahle_combo_forattr_poultry['agesex_scenario'].str.upper().isin(groups_for_attribution_upper))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_poultry = ahle_combo_forattr_poultry.loc[_row_selection].reset_index(drop=True)

# Rename groups to match attribution code
ahle_combo_forattr_poultry['agesex_scenario'] = ahle_combo_forattr_poultry['agesex_scenario'].replace(groups_for_attribution)

# =============================================================================
#### Cleanup and export
# =============================================================================
# Rename columns to match attribution code
# This also specifies the ordering of the columns
colnames = {
   "species":"Species"
   ,"production_system":"Production system"
   ,"agesex_scenario":"Age class"
   ,"ahle_component":"AHLE"
   ,"mean":"mean"
   ,"stdev":"sd"
}
ahle_combo_forattr_poultry = ahle_combo_forattr_poultry[list(colnames)].rename(columns=colnames)

# Write CSV
ahle_combo_forattr_poultry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_poultry.csv') ,index=False)

#%% Run Attribution

r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function.R')    # Full path to the R program you want to run

# =============================================================================
#### Small ruminants
# =============================================================================
# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
   os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_smallrum.csv')  # String: full path to AHLE estimates file (csv)
   ,os.path.join(ETHIOPIA_CODE_FOLDER ,'attribution_experts_smallruminants.csv')    # String: full path to expert opinion attribution file (csv)
   ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_smallruminants.csv')    # String: full path to output file (csv)
]
timerstart()
run_cmd([r_executable ,r_script] + r_args)
timerstop()

# =============================================================================
#### Cattle
# =============================================================================
# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
   os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_cattle.csv')  # String: full path to AHLE estimates file (csv)
   ,os.path.join(ETHIOPIA_CODE_FOLDER ,'attribution_experts_cattle.csv')    # String: full path to expert opinion attribution file (csv)
   ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_cattle.csv')    # String: full path to output file (csv)
]
timerstart()
run_cmd([r_executable ,r_script] + r_args)
timerstop()

# =============================================================================
#### Poultry
# =============================================================================
# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
   os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_poultry.csv')  # String: full path to AHLE estimates file (csv)
   ,os.path.join(ETHIOPIA_CODE_FOLDER ,'attribution_experts_chickens.csv')    # String: full path to expert opinion attribution file (csv)
   ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_poultry.csv')    # String: full path to output file (csv)
]
timerstart()
run_cmd([r_executable ,r_script] + r_args)
timerstop()

#%% Process attribution results

# =============================================================================
#### Import and combine attribution results
# =============================================================================
attribution_summary_smallruminants = pd.read_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_smallruminants.csv'))
attribution_summary_smallruminants['species'] = 'All Small Ruminants'

attribution_summary_cattle = pd.read_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_cattle.csv'))
attribution_summary_cattle['species'] = 'Cattle'

attribution_summary_poultry = pd.read_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_poultry.csv'))
attribution_summary_poultry['species'] = 'All Poultry'

ahle_combo_withattr = pd.concat(
    [attribution_summary_smallruminants ,attribution_summary_cattle ,attribution_summary_poultry]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
    )
cleancolnames(ahle_combo_withattr)
datainfo(ahle_combo_withattr)

# =============================================================================
#### Add health cost placeholder
# =============================================================================
# -----------------------------------------------------------------------------
# Define placeholder attribution categories
# -----------------------------------------------------------------------------
# healthcost_category_list = ['Treatment' ,'Prevention' ,'Professional time' ,'Other']
healthcost_category_list = ['Infectious' ,'Non-infectious' ,'External']
healthcost_category_df = pd.DataFrame({'cause':healthcost_category_list
                                       ,'ahle':'Health cost'}
                                      )

# -----------------------------------------------------------------------------
# Small Ruminants
# -----------------------------------------------------------------------------
# Get health cost AHLE rows
_row_selection = (ahle_combo_forattr_smallrum['AHLE'].str.upper() == 'HEALTH COST')
print(f"> Selected {_row_selection.sum() :,} rows.")
healthcost_smallrum = ahle_combo_forattr_smallrum.loc[_row_selection].reset_index(drop=True).copy()
cleancolnames(healthcost_smallrum)

# Sum sheep and goats
healthcost_smallrum['sqrd_sd'] = healthcost_smallrum['sd']**2       # Calculate variance for summing
healthcost_smallrum = healthcost_smallrum.pivot_table(
   index=['production_system' ,'age_class' ,'ahle']
   ,values=['mean' ,'sqrd_sd']
   ,aggfunc='sum'
).reset_index()
healthcost_smallrum['species'] = 'All Small Ruminants'

# Add placeholder attribution categories
healthcost_smallrum = pd.merge(left=healthcost_smallrum ,right=healthcost_category_df ,on='ahle' ,how='outer')

# Allocate health cost AHLE equally to categories
healthcost_smallrum['mean'] = healthcost_smallrum['mean'] / len(healthcost_category_list)               # Mean(1/3 X) = 1/3 Mean(X)
healthcost_smallrum['sqrd_sd'] = healthcost_smallrum['sqrd_sd'] / (len(healthcost_category_list)**2)      # Var(1/3 X) = 1/9 Var(X)

# Calc standard deviation and upper and lower 95% CI
healthcost_smallrum['sd'] = np.sqrt(healthcost_smallrum['sqrd_sd'])
del healthcost_smallrum['sqrd_sd']

healthcost_smallrum['lower95'] = healthcost_smallrum['mean'] - 1.96 * healthcost_smallrum['sd']
healthcost_smallrum['upper95'] = healthcost_smallrum['mean'] + 1.96 * healthcost_smallrum['sd']

# Add rows to attribution data
ahle_combo_withattr = pd.concat(
    [ahle_combo_withattr ,healthcost_smallrum]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# -----------------------------------------------------------------------------
# Cattle
# -----------------------------------------------------------------------------
# Get health cost AHLE rows
_row_selection = (ahle_combo_forattr_cattle['AHLE'].str.upper() == 'HEALTH COST')
print(f"> Selected {_row_selection.sum() :,} rows.")
healthcost_cattle = ahle_combo_forattr_cattle.loc[_row_selection].reset_index(drop=True).copy()
cleancolnames(healthcost_cattle)

# Add placeholder attribution categories
healthcost_cattle = pd.merge(left=healthcost_cattle ,right=healthcost_category_df ,on='ahle' ,how='outer')

# Allocate health cost AHLE equally to categories
healthcost_cattle['sqrd_sd'] = healthcost_cattle['sd']**2       # Calculate variance for summing
healthcost_cattle['mean'] = healthcost_cattle['mean'] / len(healthcost_category_list)               # Mean(1/3 X) = 1/3 Mean(X)
healthcost_cattle['sqrd_sd'] = healthcost_cattle['sqrd_sd'] / (len(healthcost_category_list)**2)    # Var(1/3 X) = 1/9 Var(X)

# Calc standard deviation and upper and lower 95% CI
healthcost_cattle['sd'] = np.sqrt(healthcost_cattle['sqrd_sd'])
del healthcost_cattle['sqrd_sd']

healthcost_cattle['lower95'] = healthcost_cattle['mean'] - 1.96 * healthcost_cattle['sd']
healthcost_cattle['upper95'] = healthcost_cattle['mean'] + 1.96 * healthcost_cattle['sd']

# Add rows to attribution data
ahle_combo_withattr = pd.concat(
    [ahle_combo_withattr ,healthcost_cattle]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# -----------------------------------------------------------------------------
# Poultry
# -----------------------------------------------------------------------------
# Get health cost AHLE rows
_row_selection = (ahle_combo_forattr_poultry['AHLE'].str.upper() == 'HEALTH COST')
print(f"> Selected {_row_selection.sum() :,} rows.")
healthcost_poultry = ahle_combo_forattr_poultry.loc[_row_selection].reset_index(drop=True).copy()
cleancolnames(healthcost_poultry)

# Add placeholder attribution categories
healthcost_poultry = pd.merge(left=healthcost_poultry ,right=healthcost_category_df ,on='ahle' ,how='outer')

# Allocate health cost AHLE equally to categories
healthcost_poultry['sqrd_sd'] = healthcost_poultry['sd']**2       # Calculate variance for summing
healthcost_poultry['mean'] = healthcost_poultry['mean'] / len(healthcost_category_list)               # Mean(1/3 X) = 1/3 Mean(X)
healthcost_poultry['sqrd_sd'] = healthcost_poultry['sqrd_sd'] / (len(healthcost_category_list)**2)    # Var(1/3 X) = 1/9 Var(X)

# Calc standard deviation and upper and lower 95% CI
healthcost_poultry['sd'] = np.sqrt(healthcost_poultry['sqrd_sd'])
del healthcost_poultry['sqrd_sd']

healthcost_poultry['lower95'] = healthcost_poultry['mean'] - 1.96 * healthcost_poultry['sd']
healthcost_poultry['upper95'] = healthcost_poultry['mean'] + 1.96 * healthcost_poultry['sd']

# Add rows to attribution data
ahle_combo_withattr = pd.concat(
    [ahle_combo_withattr ,healthcost_poultry]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# =============================================================================
#### Add disease-specific placeholder
# =============================================================================
# Create placeholder data frame
diseases_ext = pd.DataFrame({
    "cause":'External'
    ,"disease":['Cause A' ,'Cause B' ,'Cause C' ,'Cause D']
    ,"disease_proportion":[0.50 ,0.25 ,0.15 ,0.10]     # List: proportion of attribution going to each disease. Must add up to 1.
    }
)
diseases_inf = pd.DataFrame({
    "cause":'Infectious'
    ,"disease":['Pathogen A' ,'Pathogen B' ,'Pathogen C' ,'Pathogen D']
    ,"disease_proportion":[0.50 ,0.25 ,0.15 ,0.10]     # List: proportion of attribution going to each disease. Must add up to 1.
    }
)
diseases_non = pd.DataFrame({
    "cause":'Non-infectious'
    ,"disease":['Condition A' ,'Condition B' ,'Condition C' ,'Condition D']
    ,"disease_proportion":[0.50 ,0.25 ,0.15 ,0.10]     # List: proportion of attribution going to each disease. Must add up to 1.
    }
)
diseases = pd.concat(
    [diseases_ext ,diseases_inf ,diseases_non]
    ,axis=0
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# Merge
ahle_combo_withattr = pd.merge(
    left=ahle_combo_withattr
    ,right=diseases
    ,on='cause'
    ,how='outer'
    )

# Calculate placeholder values
ahle_combo_withattr['median'] = ahle_combo_withattr['median'] * ahle_combo_withattr['disease_proportion']
ahle_combo_withattr['mean'] = ahle_combo_withattr['mean'] * ahle_combo_withattr['disease_proportion']
ahle_combo_withattr['sd'] = np.sqrt(ahle_combo_withattr['sd']**2 * ahle_combo_withattr['disease_proportion']**2)
ahle_combo_withattr['lower95'] = ahle_combo_withattr['mean'] - (1.96 * ahle_combo_withattr['sd'])
ahle_combo_withattr['upper95'] = ahle_combo_withattr['mean'] + (1.96 * ahle_combo_withattr['sd'])

# =============================================================================
#### Calculate as percent of total
# =============================================================================
# REVISIT: this must be BY SPECIES if you want to use it
# total_ahle = ahle_combo_withattr['mean'].sum()
# ahle_combo_withattr['pct_of_total'] = (ahle_combo_withattr['mean'] / total_ahle) * 100

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo_withattr['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo_withattr = pd.merge(
    left=ahle_combo_withattr
    ,right=exchg_data_tomerge
    ,on='country_name'
    ,how='left'
    )
del ahle_combo_withattr['country_name']

# Add columns in USD
ahle_combo_withattr['mean_usd'] = ahle_combo_withattr['mean'] / ahle_combo_withattr['exchg_rate_lcuperusdol']
ahle_combo_withattr['median_usd'] = ahle_combo_withattr['median'] / ahle_combo_withattr['exchg_rate_lcuperusdol']
ahle_combo_withattr['lower95_usd'] = ahle_combo_withattr['lower95'] / ahle_combo_withattr['exchg_rate_lcuperusdol']
ahle_combo_withattr['upper95_usd'] = ahle_combo_withattr['upper95'] / ahle_combo_withattr['exchg_rate_lcuperusdol']

# For standard deviations, convert to variances then scale by the squared exchange rate
# VAR(aX) = a^2 * VAR(X).  a = 1/exchange rate.
ahle_combo_withattr['sd_usd'] = np.sqrt(ahle_combo_withattr['sd']**2 / ahle_combo_withattr['exchg_rate_lcuperusdol']**2)

# =============================================================================
#### Cleanup and export
# =============================================================================
# Rename columns to those Dash will look for
rename_cols = {
    "ahle":"ahle_component"
    ,"age_class":"group"
}
ahle_combo_withattr = ahle_combo_withattr.rename(columns=rename_cols)

# Split age and sex groups into their own columns
ahle_combo_withattr[['age_group' ,'sex']] = ahle_combo_withattr['group'].str.split(' ' ,expand=True)

# Recode columns to values Dash will look for
recode_sex = {
   None:'Overall'
   ,'female':'Female'
   ,'male':'Male'
}
ahle_combo_withattr['sex'] = ahle_combo_withattr['sex'].replace(recode_sex)

recode_age = {
   'Neonate':'Neonatal'
}
ahle_combo_withattr['age_group'] = ahle_combo_withattr['age_group'].replace(recode_age)

recode_prodsys = {
    "Dairy":"Periurban dairy"
}
ahle_combo_withattr['production_system'] = ahle_combo_withattr['production_system'].replace(recode_prodsys)

# Reorder columns
cols_first = ['species' ,'production_system' ,'group' ,'age_group' ,'sex' ,'ahle_component' ,'cause']
cols_other = [i for i in list(ahle_combo_withattr) if i not in cols_first]
ahle_combo_withattr = ahle_combo_withattr.reindex(columns=cols_first + cols_other)
ahle_combo_withattr = ahle_combo_withattr.sort_values(by=cols_first ,ignore_index=True)
datainfo(ahle_combo_withattr)

# -----------------------------------------------------------------------------
# Write CSV
# -----------------------------------------------------------------------------
# Without disease-specific attribution
# ahle_combo_withattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_withattr.csv') ,index=False)
# ahle_combo_withattr.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_withattr.csv') ,index=False)

# With disease-specific attribution
ahle_combo_withattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_withattr_disease.csv') ,index=False)
ahle_combo_withattr.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_withattr_disease.csv') ,index=False)
