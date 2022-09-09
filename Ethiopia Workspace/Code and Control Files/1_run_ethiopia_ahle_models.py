#%% About
'''
The University of Liverpool has provided R code to run the simulation compartmental model
for Sheep in the Crop Livestock Mixed (CLM) production system.

This program runs R code using the subprocess library.
Any R libraries required must be installed first, which I have done through RGui.
- Run RGui as administrator
- In console run: install.packages('package_name')

Update: the same R code now runs the compartmental model for both species and production systems
'''

#%% Setup

# =============================================================================
#### Rscript executable
# =============================================================================
# On Lotka
# r_executable = 'C:\\Program Files\\R\\R-4.2.0\\bin\\x64\\Rscript.exe'

# On Local
r_executable = 'C:\\Program Files\\R\\R-4.2.1\\bin\\x64\\Rscript.exe'

# =============================================================================
#### Prepare currency conversion data
# =============================================================================
# Read conversion data
exchg_data = pd.read_csv(os.path.join(ETHIOPIA_DATA_FOLDER ,'worldbank_inflation_exchangerate_gdp_2010_2021' ,'20475199-8fa4-4249-baec-98b6635f68e3_Data.csv'))
cleancolnames(exchg_data)
datainfo(exchg_data)

exchg_data_tomerge = exchg_data.query("country_name == 'Ethiopia'").query("time == 2019")
exchg_data_tomerge = exchg_data_tomerge.rename(columns={'official_exchange_rate__lcu_per_us_dol___period_average___pa_nus_fcrf_':'exchg_rate_lcuperusdol'})
exchg_data_tomerge['exchg_rate_lcuperusdol'] = exchg_data_tomerge['exchg_rate_lcuperusdol'].astype('float64')                     # Convert a single column. Can replace original or make new column.
exchg_data_tomerge = exchg_data_tomerge[['country_name' ,'exchg_rate_lcuperusdol']]

#%% Run AHLE with manual scenarios
'''
Using the code actively co-developed with Liverpool.

Pass nruns as argument

N runs | Run time
10       12s
100      30s

Bonus: this prints plots to Rplots.pdf. I cannot find any line in the code which specifies this file.
'''

# r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE function with manual scenarios.R')    # Full path to the R program you want to run

# # Arguments to R function, as list of strings.
# # ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
# r_args = [
#     '10'                         # Arg 1: Number of simulation runs
#     ,ETHIOPIA_OUTPUT_FOLDER     # Arg 2: Folder location for saving output files
# ]

# timerstart()
# run_cmd([r_executable ,r_script] + r_args)
# timerstop()

#%% Process AHLE with manual scenarios

# # =============================================================================
# #### Combine
# # =============================================================================
# # -----------------------------------------------------------------------------
# # Merge scenarios
# # -----------------------------------------------------------------------------
# def combine_ahle_scenarios(
#       input_folder
#       ,input_file_prefix   # String
#       ,label_species       # String: add column 'species' with this label
#       ,label_prodsys       # String: add column 'production_system' with this label
#       ,input_file_suffixes=['current' ,'ideal' ,'mortality_zero']    # List of strings
#       ):
#    dfcombined = pd.DataFrame()   # Initialize merged data

#    for i ,suffix in enumerate(input_file_suffixes):
#       # Read file
#       df = pd.read_csv(os.path.join(input_folder ,f'{input_file_prefix}_{suffix}.csv'))

#       # Add column suffixes
#       df = df.add_suffix(f'_{suffix}')
#       df = df.rename(columns={f'Item_{suffix}':'Item' ,f'Group_{suffix}':'Group'})

#       # Add to merged data
#       if i == 0:
#          dfcombined = df.copy()
#       else:
#          dfcombined = pd.merge(left=dfcombined ,right=df, on=['Item' ,'Group'] ,how='outer')

#    # Add label columns
#    dfcombined['species'] = f'{label_species}'
#    dfcombined['production_system'] = f'{label_prodsys}'

#    # Reorder columns
#    cols_first = ['species' ,'production_system']
#    cols_other = [i for i in list(dfcombined) if i not in cols_first]
#    dfcombined = dfcombined.reindex(columns=cols_first + cols_other)

#    # Cleanup column names
#    cleancolnames(dfcombined)

#    return dfcombined

# ahle_combo_sheep_clm = combine_ahle_scenarios(
#    input_folder=ETHIOPIA_OUTPUT_FOLDER
#    ,input_file_prefix='ahle_sheep_clm_summary'
#    ,label_species='Sheep'
#    ,label_prodsys='Crop livestock mixed'
# )
# ahle_combo_sheep_past = combine_ahle_scenarios(
#    input_folder=ETHIOPIA_OUTPUT_FOLDER
#    ,input_file_prefix='ahle_sheep_past_summary'
#    ,label_species='Sheep'
#    ,label_prodsys='Pastoral'
# )
# ahle_combo_goat_clm = combine_ahle_scenarios(
#    input_folder=ETHIOPIA_OUTPUT_FOLDER
#    ,input_file_prefix='ahle_goat_clm_summary'
#    ,label_species='Goat'
#    ,label_prodsys='Crop livestock mixed'
# )
# ahle_combo_goat_past = combine_ahle_scenarios(
#    input_folder=ETHIOPIA_OUTPUT_FOLDER
#    ,input_file_prefix='ahle_goat_past_summary'
#    ,label_species='Goat'
#    ,label_prodsys='Pastoral'
# )

# # -----------------------------------------------------------------------------
# # Stack species and production systems
# # -----------------------------------------------------------------------------
# ahle_combo = pd.concat(
#    [ahle_combo_sheep_clm ,ahle_combo_sheep_past ,ahle_combo_goat_clm ,ahle_combo_goat_past]      # List of dataframes to concatenate
#    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#    ,join='outer'        # 'outer': keep all index values from all data frames
#    ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # Split age and sex groups into their own columns
# ahle_combo[['age_group' ,'sex']] = ahle_combo['group'].str.split(' ' ,expand=True)
# recode_sex = {'Combined':'Overall' ,None:'Overall'}
# ahle_combo['sex'] = ahle_combo['sex'].replace(recode_sex)

# # =============================================================================
# #### Add group summaries
# # =============================================================================
# '''
# This is to provide complete filtering options in the dashboard.
# Currently only creating means for these groups, not standard deviations, as we
# are only displaying means in the dashboard.

# Standard deviations are used in the Attribution function, but that is limited
# to a few groups whose means and standard deviations are calculated in the base
# AHLE function.
# '''
# mean_cols = [i for i in list(ahle_combo) if 'mean' in i]
# sd_cols = [i for i in list(ahle_combo) if 'stdev' in i]

# # Create Overall sex for Adults
# ahle_combo_adultoverall = ahle_combo.query("age_group.str.upper() == 'ADULT'").pivot_table(
#    index=['species' ,'production_system' ,'item' ,'age_group']
#    ,values=mean_cols
#    ,aggfunc='sum'
# ).reset_index()
# ahle_combo_adultoverall['group'] = 'Adult Combined'
# ahle_combo_adultoverall['sex'] = 'Overall'

# ahle_combo = pd.concat(
#    [ahle_combo ,ahle_combo_adultoverall]
#    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#    ,join='outer'        # 'outer': keep all index values from all data frames
#    ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # Create Male and Female sexes for Overall age group
# ahle_combo_overallmale = ahle_combo.query("sex.str.upper() == 'MALE'").pivot_table(
#    index=['species' ,'production_system' ,'item' ,'sex']
#    ,values=mean_cols
#    ,aggfunc='sum'
# ).reset_index()
# ahle_combo_overallmale['group'] = 'Overall Male'
# ahle_combo_overallmale['age_group'] = 'Overall'

# ahle_combo_overallfemale = ahle_combo.query("sex.str.upper() == 'FEMALE'").pivot_table(
#    index=['species' ,'production_system' ,'item' ,'sex']
#    ,values=mean_cols
#    ,aggfunc='sum'
# ).reset_index()
# ahle_combo_overallfemale['group'] = 'Overall Female'
# ahle_combo_overallfemale['age_group'] = 'Overall'

# ahle_combo = pd.concat(
#    [ahle_combo ,ahle_combo_overallmale ,ahle_combo_overallfemale]
#    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#    ,join='outer'        # 'outer': keep all index values from all data frames
#    ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # Create summaries over all production systems
# ahle_combo_allprod = ahle_combo.pivot_table(
#    index=['species' ,'item' ,'group' ,'age_group' ,'sex']
#    ,values=mean_cols
#    ,aggfunc='sum'
# ).reset_index()
# ahle_combo_allprod['production_system'] = 'Overall'

# ahle_combo = pd.concat(
#    [ahle_combo ,ahle_combo_allprod]
#    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#    ,join='outer'        # 'outer': keep all index values from all data frames
#    ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # Create summaries over all species
# ahle_combo_allspec = ahle_combo.pivot_table(
#    index=['production_system' ,'item' ,'group' ,'age_group' ,'sex']
#    ,values=mean_cols
#    ,aggfunc='sum'
# ).reset_index()
# ahle_combo_allspec['species'] = 'All small ruminants'

# ahle_combo = pd.concat(
#    [ahle_combo ,ahle_combo_allspec]
#    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#    ,join='outer'        # 'outer': keep all index values from all data frames
#    ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # =============================================================================
# #### Export first summary
# # =============================================================================
# # Reorder columns
# cols_first = ['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex']
# cols_other = [i for i in list(ahle_combo) if i not in cols_first]
# ahle_combo = ahle_combo.reindex(columns=cols_first + cols_other)

# # Sort
# ahle_combo = ahle_combo.sort_values(
#    by=cols_first
#    ,ignore_index=True      # Otherwise will keep original index numbers
# )

# # Export
# ahle_combo.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.csv') ,index=False)

# # =============================================================================
# #### Restructure and calculate AHLE components
# # =============================================================================
# # Transpose
# # For AHLE calcs, we want each item in a column.
# # Only need items 'gross margin' and 'health cost'
# ahle_combo_p = ahle_combo.query("item.str.upper().isin(['GROSS MARGIN' ,'HEALTH COST'])").pivot(
#    index=['species' ,'production_system' ,'group' ,'age_group' ,'sex']
#    ,columns='item'
#    ,values=mean_cols + sd_cols   # Need means and standard deviations for later calculations
# ).reset_index()                  # Pivoting will change columns to indexes. Change them back.
# ahle_combo_p = colnames_from_index(ahle_combo_p)   # Change multi-index to column names
# cleancolnames(ahle_combo_p)
# ahle_combo_p = ahle_combo_p.rename(
#    columns={'species_':'species' ,'production_system_':'production_system' ,'group_':'group' ,'age_group_':'age_group' ,'sex_':'sex'}
# )
# datainfo(ahle_combo_p)

# # Calcs
# '''
# Calculating mean and standard deviation for each AHLE component.
# Relying on the following properties of sums of random variables:
#    mean(aX + bY) = a*mean(X) + b*mean(Y), regardless of correlation
#    var(aX + bY) = a^2*var(X) + b^2*var(Y), assuming X and Y are uncorrelated
# '''
# # Means are simple arithmetic
# ahle_combo_p.eval(
#     '''
#     ahle_due_to_mortality_mean = mean_mortality_zero_gross_margin - mean_current_gross_margin
#     ahle_due_to_healthcost_mean = mean_current_health_cost
#     ahle_due_to_productionloss_mean = (mean_ideal_gross_margin - mean_current_gross_margin) \
#       - ahle_due_to_mortality_mean - ahle_due_to_healthcost_mean
#     '''
#     ,inplace=True
# )

# # Standard deviations require summing variances
# ahle_combo_p['ahle_due_to_mortality_stdev'] = np.sqrt(ahle_combo_p['stdev_mortality_zero_gross_margin']**2 + ahle_combo_p['stdev_current_gross_margin']**2)
# ahle_combo_p['ahle_due_to_healthcost_stdev'] = ahle_combo_p['stdev_current_health_cost']
# ahle_combo_p['ahle_due_to_productionloss_stdev'] = np.sqrt(
#    ahle_combo_p['stdev_ideal_gross_margin']**2 + ahle_combo_p['stdev_current_gross_margin']**2 \
#       + ahle_combo_p['stdev_mortality_zero_gross_margin']**2 + ahle_combo_p['stdev_current_gross_margin']**2 \
#          + ahle_combo_p['stdev_current_health_cost']**2
#    )

# # Plot means and std. deviations
# plt.bar(
#    ahle_combo_p['group']
#    ,height=ahle_combo_p['ahle_due_to_mortality_mean']
#    ,yerr=ahle_combo_p['ahle_due_to_mortality_stdev']
# )

# # =============================================================================
# #### Export second summary
# # =============================================================================
# datainfo(ahle_combo_p)
# ahle_combo_p.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.csv') ,index=False)

#%% Run AHLE with control file scenarios
'''
N runs | Run time
10       32s
100      1m 53s
1000     14m 40s
'''
r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE function with control file scenarios.R')    # Full path to the R program you want to run

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
   '1000'                         # Arg 1: Number of simulation runs.
   ,ETHIOPIA_OUTPUT_FOLDER     # Arg 2: Folder location for saving output files
   ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters.xlsx')    # Arg 3: full path to scenario control file
]

timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=99)
timerstop()

#%% Process AHLE with control file scenarios

# =============================================================================
#### Combine
# =============================================================================
# -----------------------------------------------------------------------------
# Merge scenarios
# -----------------------------------------------------------------------------
def combine_ahle_scenarios(
      input_folder
      ,input_file_prefix   # String
      ,label_species       # String: add column 'species' with this label
      ,label_prodsys       # String: add column 'production_system' with this label
      ,input_file_suffixes=[        # List of strings
         'Current'
         ,'Ideal'
         ,'ideal_AF'
         ,'ideal_AM'
         ,'ideal_JF'
         ,'ideal_JM'
         ,'ideal_NF'
         ,'ideal_NM'
         ,'all_mortality_zero'
         ,'mortality_zero_AF'
         ,'mortality_zero_AM'
         ,'mortality_zero_J'
         ,'mortality_zero_N'
         ]
      ):
   dfcombined = pd.DataFrame()   # Initialize merged data

   for i ,suffix in enumerate(input_file_suffixes):
      # Read file
      df = pd.read_csv(os.path.join(input_folder ,f'{input_file_prefix}_{suffix}.csv'))

      # Add column suffixes
      df = df.add_suffix(f'_{suffix}')
      df = df.rename(columns={f'Item_{suffix}':'Item' ,f'Group_{suffix}':'Group'})

      # Add to merged data
      if i == 0:
         dfcombined = df.copy()
      else:
         dfcombined = pd.merge(left=dfcombined ,right=df, on=['Item' ,'Group'] ,how='outer')

   # Add label columns
   dfcombined['species'] = f'{label_species}'
   dfcombined['production_system'] = f'{label_prodsys}'

   # Reorder columns
   cols_first = ['species' ,'production_system']
   cols_other = [i for i in list(dfcombined) if i not in cols_first]
   dfcombined = dfcombined.reindex(columns=cols_first + cols_other)

   # Cleanup column names
   cleancolnames(dfcombined)

   return dfcombined

ahle_combo_sheep_clm = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_CLM_S'
   ,label_species='Sheep'
   ,label_prodsys='Crop livestock mixed'
)
datainfo(ahle_combo_sheep_clm)
ahle_combo_sheep_past = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_Past_S'
   ,label_species='Sheep'
   ,label_prodsys='Pastoral'
)
datainfo(ahle_combo_sheep_past)
ahle_combo_goat_clm = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_CLM_G'
   ,label_species='Goat'
   ,label_prodsys='Crop livestock mixed'
)
datainfo(ahle_combo_goat_clm)
ahle_combo_goat_past = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_Past_G'
   ,label_species='Goat'
   ,label_prodsys='Pastoral'
)
datainfo(ahle_combo_goat_past)

# -----------------------------------------------------------------------------
# Stack species and production systems
# -----------------------------------------------------------------------------
ahle_combo_raw = pd.concat(
   [ahle_combo_sheep_clm ,ahle_combo_sheep_past ,ahle_combo_goat_clm ,ahle_combo_goat_past]      # List of dataframes to concatenate
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)
datainfo(ahle_combo_raw)

# =============================================================================
#### Export stacked data
# =============================================================================
# Export
ahle_combo_raw.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_stacked.csv') ,index=False)

# =============================================================================
#### Create rows to filter scenarios
# =============================================================================
# Create a row for each age*sex group by duplication
# Keep only Total System results
group_basetable = pd.DataFrame({
   'agesex_group':[
      'Neonatal Female'
      ,'Neonatal Male'
      # ,'Neonatal Overall'

      ,'Juvenile Female'
      ,'Juvenile Male'
      # ,'Juvenile Overall'

      ,'Adult Female'
      ,'Adult Male'
      # ,'Adult Overall'

      # ,'Overall Female'
      # ,'Overall Male'

      ,'Overall Overall'
      ]
   ,'group':'Overall'
   })
ahle_combo_expanded = pd.merge(
   left=group_basetable
   ,right=ahle_combo_raw.query("group.str.upper() == 'OVERALL'")
   ,on='group'
   ,how='outer'
   )

# Rename agesex_group and drop plain group
ahle_combo_expanded = ahle_combo_expanded.drop(columns='group').rename(columns={'agesex_group':'group'})

# Split age and sex groups into their own columns
ahle_combo_expanded[['age_group' ,'sex']] = ahle_combo_expanded['group'].str.split(' ' ,expand=True)
ahle_combo_expanded['group'] = ahle_combo_expanded['group'].replace({'Overall Overall':'Overall'})

# =============================================================================
#### Assign correct scenario to each group
# =============================================================================
def create_means_touse(INPUT_ROW):
   if INPUT_ROW['group'].upper() == 'OVERALL':
      OUTPUT_MORTZERO_MEAN = INPUT_ROW['mean_all_mortality_zero']
      OUTPUT_MORTZERO_SD = INPUT_ROW['stdev_all_mortality_zero']
      OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal']
      OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal']
   elif INPUT_ROW['age_group'].upper() == 'NEONATAL':
      OUTPUT_MORTZERO_MEAN = INPUT_ROW['mean_mortality_zero_n']      # Mortality zero scenario is not sexed for neonatal
      OUTPUT_MORTZERO_SD = INPUT_ROW['stdev_mortality_zero_n']
      if INPUT_ROW['sex'].upper() == 'FEMALE':
         OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal_nf']
         OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal_nf']
      elif INPUT_ROW['sex'].upper() == 'MALE':
         OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal_nm']
         OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal_nm']
      else:
         OUTPUT_IDEAL_MEAN = None
         OUTPUT_IDEAL_SD = None
   elif INPUT_ROW['age_group'].upper() == 'JUVENILE':
      OUTPUT_MORTZERO_MEAN = INPUT_ROW['mean_mortality_zero_j']      # Mortality zero scenario is not sexed for juvenile
      OUTPUT_MORTZERO_SD = INPUT_ROW['stdev_mortality_zero_j']
      if INPUT_ROW['sex'].upper() == 'FEMALE':
         OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal_jf']
         OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal_jf']
      elif INPUT_ROW['sex'].upper() == 'MALE':
         OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal_jm']
         OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal_jm']
      else:
         OUTPUT_IDEAL_MEAN = None
         OUTPUT_IDEAL_SD = None
   elif INPUT_ROW['age_group'].upper() == 'ADULT':
      if INPUT_ROW['sex'].upper() == 'FEMALE':
         OUTPUT_MORTZERO_MEAN = INPUT_ROW['mean_mortality_zero_af']
         OUTPUT_MORTZERO_SD = INPUT_ROW['stdev_mortality_zero_af']
         OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal_af']
         OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal_af']
      elif INPUT_ROW['sex'].upper() == 'MALE':
         OUTPUT_MORTZERO_MEAN = INPUT_ROW['mean_mortality_zero_am']
         OUTPUT_MORTZERO_SD = INPUT_ROW['stdev_mortality_zero_am']
         OUTPUT_IDEAL_MEAN = INPUT_ROW['mean_ideal_am']
         OUTPUT_IDEAL_SD = INPUT_ROW['stdev_ideal_am']
      else:
         OUTPUT_MORTZERO_MEAN = None
         OUTPUT_MORTZERO_SD = None
         OUTPUT_IDEAL_MEAN = None
         OUTPUT_IDEAL_SD = None
   else:
      OUTPUT_MORTZERO_MEAN = None
      OUTPUT_MORTZERO_SD = None
      OUTPUT_IDEAL_MEAN = None
      OUTPUT_IDEAL_SD = None
   return pd.Series([OUTPUT_MORTZERO_MEAN ,OUTPUT_MORTZERO_SD ,OUTPUT_IDEAL_MEAN ,OUTPUT_IDEAL_SD])
ahle_combo_expanded[['mean_mortality_zero_touse' ,'stdev_mortality_zero_touse' ,'mean_ideal_touse' ,'stdev_ideal_touse']] = ahle_combo_expanded.apply(create_means_touse ,axis=1)      # Apply to each row of the dataframe (axis=1)
datainfo(ahle_combo_expanded)

# Create subset of columns for checking
mean_cols = [i for i in list(ahle_combo_expanded) if 'mean' in i]
keep_cols = [
   'species'
   ,'production_system'
   ,'item'
   ,'group'
   ,'age_group'
   ,'sex'
   ] + mean_cols
ahle_combo_expanded_tocheck = ahle_combo_expanded[keep_cols].copy()

# Keep only reconciled scenario columns
# Keep only sex-specific rows as combined sex groups must be calculated for most
# age groups anyway.
keep_cols = [
   'species'
   ,'production_system'
   ,'item'
   ,'group'
   ,'age_group'
   ,'sex'
   ,'mean_current' ,'stdev_current'
   ,'mean_mortality_zero_touse' ,'stdev_mortality_zero_touse'
   ,'mean_ideal_touse' ,'stdev_ideal_touse'
   ]
ahle_combo = ahle_combo_expanded[keep_cols].copy()
ahle_combo = ahle_combo.rename(columns={
   'mean_mortality_zero_touse':'mean_mortality_zero'
   ,'stdev_mortality_zero_touse':'stdev_mortality_zero'
   ,'mean_ideal_touse':'mean_ideal'
   ,'stdev_ideal_touse':'stdev_ideal'
   })
datainfo(ahle_combo)

# =============================================================================
#### Add group summaries
# =============================================================================
mean_cols = [i for i in list(ahle_combo) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo) if 'stdev' in i]

# -----------------------------------------------------------------------------
# Create variance columns
# -----------------------------------------------------------------------------
var_cols = ['sqrd_' + COLNAME for COLNAME in sd_cols]
for i ,VARCOL in enumerate(var_cols):
   SDCOL = sd_cols[i]
   ahle_combo[VARCOL] = ahle_combo[SDCOL]**2

# # -----------------------------------------------------------------------------
# # Create Overall sum
# # -----------------------------------------------------------------------------
# # Update: this already exists on data
# #!!! Must happen first to avoid double-counting!
# ahle_combo_sumall = ahle_combo.pivot_table(
#     index=['species' ,'production_system' ,'item']
#     ,values=mean_cols + var_cols
#     ,aggfunc='sum'
# ).reset_index()
# ahle_combo_sumall['group'] = 'Overall'
# ahle_combo_sumall['age_group'] = 'Overall'
# ahle_combo_sumall['sex'] = 'Overall'

# ahle_combo = pd.concat(
#     [ahle_combo ,ahle_combo_sumall]
#     ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#     ,join='outer'        # 'outer': keep all index values from all data frames
#     ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# -----------------------------------------------------------------------------
# Create Overall sex for each age group
# -----------------------------------------------------------------------------
#!!! Results for individual age/sex scenarios don't sum!
# For now, using MAX
# For Adults
ahle_combo_sumsexes_adult = ahle_combo.query("age_group.str.upper() == 'ADULT'").pivot_table(
    index=['species' ,'production_system' ,'item' ,'age_group']
    ,values=mean_cols + var_cols
    ,aggfunc='max'
).reset_index()
ahle_combo_sumsexes_adult['group'] = 'Adult Combined'
ahle_combo_sumsexes_adult['sex'] = 'Overall'

# For Neonatal
ahle_combo_sumsexes_neonatal = ahle_combo.query("age_group.str.upper() == 'NEONATAL'").pivot_table(
    index=['species' ,'production_system' ,'item' ,'age_group']
    ,values=mean_cols + var_cols
    ,aggfunc='max'
).reset_index()
ahle_combo_sumsexes_neonatal['group'] = 'Neonatal Combined'
ahle_combo_sumsexes_neonatal['sex'] = 'Overall'

# For Juvenile
ahle_combo_sumsexes_juvenile = ahle_combo.query("age_group.str.upper() == 'JUVENILE'").pivot_table(
    index=['species' ,'production_system' ,'item' ,'age_group']
    ,values=mean_cols + var_cols
    ,aggfunc='max'
).reset_index()
ahle_combo_sumsexes_juvenile['group'] = 'Juvenile Combined'
ahle_combo_sumsexes_juvenile['sex'] = 'Overall'

# Stack
ahle_combo = pd.concat(
    [ahle_combo ,ahle_combo_sumsexes_adult ,ahle_combo_sumsexes_neonatal ,ahle_combo_sumsexes_juvenile]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# -----------------------------------------------------------------------------
# Create Overall age group for each sex
# -----------------------------------------------------------------------------
# For Males
ahle_combo_sumages_male = ahle_combo.query("sex.str.upper() == 'MALE'").pivot_table(
    index=['species' ,'production_system' ,'item' ,'sex']
    ,values=mean_cols + var_cols
    ,aggfunc='max'
).reset_index()
ahle_combo_sumages_male['group'] = 'Overall Male'
ahle_combo_sumages_male['age_group'] = 'Overall'

# For Females
ahle_combo_sumages_female = ahle_combo.query("sex.str.upper() == 'FEMALE'").pivot_table(
    index=['species' ,'production_system' ,'item' ,'sex']
    ,values=mean_cols + var_cols
    ,aggfunc='max'
).reset_index()
ahle_combo_sumages_female['group'] = 'Overall Female'
ahle_combo_sumages_female['age_group'] = 'Overall'

# Stack
ahle_combo = pd.concat(
    [ahle_combo ,ahle_combo_sumages_male ,ahle_combo_sumages_female]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# -----------------------------------------------------------------------------
# Create overall production system
# -----------------------------------------------------------------------------
ahle_combo_sumprod = ahle_combo.pivot_table(
   index=['species' ,'item' ,'group' ,'age_group' ,'sex']
   ,values=mean_cols + var_cols
   ,aggfunc='sum'
).reset_index()
ahle_combo_sumprod['production_system'] = 'Overall'

ahle_combo = pd.concat(
   [ahle_combo ,ahle_combo_sumprod]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# -----------------------------------------------------------------------------
# Create overall species
# -----------------------------------------------------------------------------
ahle_combo_sumspec = ahle_combo.pivot_table(
   index=['production_system' ,'item' ,'group' ,'age_group' ,'sex']
   ,values=mean_cols + var_cols
   ,aggfunc='sum'
).reset_index()
ahle_combo_sumspec['species'] = 'All small ruminants'

ahle_combo = pd.concat(
   [ahle_combo ,ahle_combo_sumspec]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# -----------------------------------------------------------------------------
# Calculate standard deviations
# -----------------------------------------------------------------------------
# Will overwrite standard deviations for the handful of groups that have them,
# but that's OK.
for i ,VARCOL in enumerate(var_cols):
   SDCOL = sd_cols[i]
   ahle_combo[SDCOL] = np.sqrt(ahle_combo[VARCOL])
   ahle_combo = ahle_combo.drop(columns=VARCOL)

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo = pd.merge(
    left=ahle_combo
    ,right=exchg_data_tomerge
    ,on='country_name'
    ,how='left'
    )
del ahle_combo['country_name']

# Add columns in USD for appropriate items
currency_items_containing = ['cost' ,'value' ,'margin' ,'expenditure']
currency_items = []
for STR in currency_items_containing:
   currency_items = currency_items + [item for item in ahle_combo['item'].unique() if STR.upper() in item.upper()]

for MEANCOL in mean_cols:
   MEANCOL_USD = MEANCOL + '_usd'
   ahle_combo.loc[ahle_combo['item'].isin(currency_items) ,MEANCOL_USD] = \
      ahle_combo[MEANCOL] / ahle_combo['exchg_rate_lcuperusdol']

# For standard deviations, convert to variances then scale by the squared exchange rate
# VAR(aX) = a^2 * VAR(X).  a = 1/exchange rate.
for SDCOL in sd_cols:
   SDCOL_USD = SDCOL + '_usd'
   ahle_combo.loc[ahle_combo['item'].isin(currency_items) ,SDCOL_USD] = \
      np.sqrt(ahle_combo[SDCOL]**2 / ahle_combo['exchg_rate_lcuperusdol']**2)

# =============================================================================
#### Export summary
# =============================================================================
# Reorder columns
cols_first = ['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex']
cols_other = [i for i in list(ahle_combo) if i not in cols_first]
ahle_combo = ahle_combo.reindex(columns=cols_first + cols_other)

# Sort
ahle_combo = ahle_combo.sort_values(
   by=cols_first
   ,ignore_index=True      # Otherwise will keep original index numbers
)

datainfo(ahle_combo)

# Export
ahle_combo.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.csv') ,index=False)

#%% Calculate AHLE components

# =============================================================================
#### Restructure and calc
# =============================================================================
# Transpose
# For AHLE calcs, we want each item in a column.
# Only need items 'gross margin' and 'health cost'
ahle_combo_p = ahle_combo.query("item.str.upper().isin(['GROSS MARGIN' ,'HEALTH COST'])").pivot(
    index=['species' ,'production_system' ,'group' ,'age_group' ,'sex']
    ,columns='item'
    ,values=mean_cols + sd_cols   # Need means and standard deviations for later calculations
).reset_index()                  # Pivoting will change columns to indexes. Change them back.
ahle_combo_p = colnames_from_index(ahle_combo_p)   # Change multi-index to column names
cleancolnames(ahle_combo_p)
ahle_combo_p = ahle_combo_p.rename(
    columns={'species_':'species' ,'production_system_':'production_system' ,'group_':'group' ,'age_group_':'age_group' ,'sex_':'sex'}
)
datainfo(ahle_combo_p)

# -----------------------------------------------------------------------------
# Calcs
# -----------------------------------------------------------------------------
'''
Calculating mean and standard deviation for each AHLE component.
Relying on the following properties of sums of random variables:
    mean(aX + bY) = a*mean(X) + b*mean(Y), regardless of correlation
    var(aX + bY) = a^2*var(X) + b^2*var(Y), assuming X and Y are uncorrelated
'''
# Means are simple arithmetic
ahle_combo_p.eval(
    '''
    ahle_due_to_mortality_mean = mean_mortality_zero_gross_margin - mean_current_gross_margin
    ahle_due_to_healthcost_mean = mean_current_health_cost
    ahle_due_to_productionloss_mean = (mean_ideal_gross_margin - mean_current_gross_margin) \
      - ahle_due_to_mortality_mean - ahle_due_to_healthcost_mean
    '''
    ,inplace=True
)

# Standard deviations require summing variances
ahle_combo_p['ahle_due_to_mortality_stdev'] = np.sqrt(ahle_combo_p['stdev_mortality_zero_gross_margin']**2 + ahle_combo_p['stdev_current_gross_margin']**2)
ahle_combo_p['ahle_due_to_healthcost_stdev'] = ahle_combo_p['stdev_current_health_cost']
ahle_combo_p['ahle_due_to_productionloss_stdev'] = np.sqrt(
    ahle_combo_p['stdev_ideal_gross_margin']**2 + ahle_combo_p['stdev_current_gross_margin']**2 \
      + ahle_combo_p['stdev_mortality_zero_gross_margin']**2 + ahle_combo_p['stdev_current_gross_margin']**2 \
          + ahle_combo_p['stdev_current_health_cost']**2
    )

# Plot means and std. deviations
plt.bar(
    ahle_combo_p['group']
    ,height=ahle_combo_p['ahle_due_to_mortality_mean']
    ,yerr=ahle_combo_p['ahle_due_to_mortality_stdev']
)

# =============================================================================
#### Export summary2
# =============================================================================
datainfo(ahle_combo_p)
ahle_combo_p.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.csv') ,index=False)

#%% Run Attribution using example inputs

# r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function.R')    # Full path to the R program you want to run
#
# # Arguments to R function, as list of strings.
# # ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
# r_args = [
#     os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function input - example AHLE.csv')                # String: full path to AHLE estimates file (csv)
#     ,os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function input - expert opinions.csv')               # String: full path to expert opinion attribution file (csv)
#     ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary.csv')    # String: full path to output file (csv)
# ]
#
# timerstart()
# run_cmd([r_executable ,r_script] + r_args)
# timerstop()

#%% Prep for Attribution using latest AHLE inputs

# Restructure to use as input to Attribution function
ahle_combo_forattr_means = ahle_combo_p.melt(
   id_vars=['species' ,'production_system' ,'group']
   ,value_vars=['ahle_due_to_mortality_mean' ,'ahle_due_to_healthcost_mean' ,'ahle_due_to_productionloss_mean']
   ,var_name='ahle_component'
   ,value_name='mean'
)
ahle_combo_forattr_stdev = ahle_combo_p.melt(
   id_vars=['species' ,'production_system' ,'group']
   ,value_vars=['ahle_due_to_mortality_stdev' ,'ahle_due_to_healthcost_stdev' ,'ahle_due_to_productionloss_stdev']
   ,var_name='ahle_component'
   ,value_name='stdev'
)

# Rename AHLE components to match expert opinion file (data.csv)
simplify_ahle_comps = {
   "ahle_due_to_mortality_mean":"Mortality"
   ,"ahle_due_to_healthcost_mean":"Health cost"
   ,"ahle_due_to_productionloss_mean":"Production loss"
   ,"ahle_due_to_mortality_stdev":"Mortality"
   ,"ahle_due_to_healthcost_stdev":"Health cost"
   ,"ahle_due_to_productionloss_stdev":"Production loss"
}
ahle_combo_forattr_means['ahle_component'] = ahle_combo_forattr_means['ahle_component'].replace(simplify_ahle_comps)
ahle_combo_forattr_stdev['ahle_component'] = ahle_combo_forattr_stdev['ahle_component'].replace(simplify_ahle_comps)

# Merge means and standard deviations
ahle_combo_forattr = pd.merge(
   left=ahle_combo_forattr_means
   ,right=ahle_combo_forattr_stdev
   ,on=['species' ,'production_system' ,'group' ,'ahle_component']
   ,how='outer'
)

# Filter age/sex groups and rename to match attribution code
groups_for_attribution = {
   'Adult Female':'Adult female'
   ,'Adult Male':'Adult male'
   ,'Juvenile Combined':'Juvenile'
   ,'Neonatal Combined':'Neonate'
}
groups_for_attribution_upper = [i.upper() for i in list(groups_for_attribution)]

_row_selection = (ahle_combo_forattr['group'].str.upper().isin(groups_for_attribution_upper)) \
   & (ahle_combo_forattr['species'].str.upper().isin(['SHEEP' ,'GOAT'])) \
      & (ahle_combo_forattr['production_system'].str.upper().isin(['CROP LIVESTOCK MIXED' ,'PASTORAL']))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr = ahle_combo_forattr.loc[_row_selection].reset_index(drop=True)

# Rename groups to match attribution code
ahle_combo_forattr['group'] = ahle_combo_forattr['group'].replace(groups_for_attribution)

# Rename columns to names Attribution code looks for
colnames = {
   "species":"Species"
   ,"production_system":"Production system"
   ,"group":"Age class"
   ,"ahle_component":"AHLE"
   ,"mean":"mean"
   ,"stdev":"sd"
}
ahle_combo_forattr = ahle_combo_forattr.rename(columns=colnames)

# Write CSV
ahle_combo_forattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr.csv') ,index=False)

#%% Run Attribution using latest AHLE inputs

r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function.R')    # Full path to the R program you want to run

# Arguments to R function, as list of strings.
# ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
r_args = [
   os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr.csv')  # String: full path to AHLE estimates file (csv)
   ,os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function input - expert opinions.csv')               # String: full path to expert opinion attribution file (csv)
   ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary.csv')    # String: full path to output file (csv)
]

timerstart()
run_cmd([r_executable ,r_script] + r_args)
timerstop()

#%% Process attribution results

attribution_summary = pd.read_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary.csv'))
ahle_combo_withattr = attribution_summary.copy()
cleancolnames(ahle_combo_withattr)
datainfo(ahle_combo_withattr)

rename_cols = {
   "ahle":"ahle_component"
   ,"age_class":"group"
}
ahle_combo_withattr = ahle_combo_withattr.rename(columns=rename_cols)

# =============================================================================
#### Add placeholder for health cost attribution
# =============================================================================
# Get health cost AHLE rows
# _row_selection = (ahle_combo_forattr['AHLE'].str.upper() == 'HEALTH COST')
# print(f"> Selected {_row_selection.sum() :,} rows.")
# healthcost_attr = ahle_combo_forattr.loc[_row_selection].reset_index(drop=True).copy()
# cleancolnames(healthcost_attr)

# Update: using raw output from current scenario instead of those from age/sex scenario-specific
_row_selection = (ahle_combo_raw['item'].str.upper() == 'HEALTH COST')
print(f"> Selected {_row_selection.sum() :,} rows.")
healthcost_attr = ahle_combo_raw.loc[_row_selection].reset_index(drop=True).copy()
cleancolnames(healthcost_attr)

# Filter age/sex groups and rename to match attribution code
_row_selection = (healthcost_attr['group'].str.upper().isin(groups_for_attribution_upper))
print(f"> Selected {_row_selection.sum() :,} rows.")
healthcost_attr = healthcost_attr.loc[_row_selection].reset_index(drop=True)

# Rename groups to match attribution code
healthcost_attr['group'] = healthcost_attr['group'].replace(groups_for_attribution)

# Modify columns to match ahle_combo_withattr
rename_cols = {
   "item":"ahle_component"
   ,"mean_current":"mean"
}
healthcost_attr = healthcost_attr.rename(columns=rename_cols)

# Add variance for summing
healthcost_attr['sqrd_sd'] = healthcost_attr['stdev_current']**2

# Sum to same level as ahle_combo_withattr
healthcost_attr = healthcost_attr.pivot_table(
   index=['production_system' ,'group' ,'ahle_component']
   ,values=['mean' ,'sqrd_sd']
   ,aggfunc='sum'
).reset_index()

# Add placeholder attribution categories
# healthcost_attr_category_list = ['Treatment' ,'Prevention' ,'Professional time' ,'Other']
healthcost_attr_category_list = ['Infectious' ,'Non-infectious' ,'External']
healthcost_attr_category_df = pd.DataFrame({'cause':healthcost_attr_category_list
                                           ,'ahle_component':'Health Cost'}
                                          )
healthcost_attr = pd.merge(left=healthcost_attr ,right=healthcost_attr_category_df ,on='ahle_component' ,how='outer')

# Allocate health cost AHLE equally to categories
healthcost_attr['mean'] = healthcost_attr['mean'] / len(healthcost_attr_category_list)
healthcost_attr['sqrd_sd'] = healthcost_attr['sqrd_sd'] / len(healthcost_attr_category_list)

# Calc standard deviation and upper and lower 95% CI
healthcost_attr['sd'] = np.sqrt(healthcost_attr['sqrd_sd'])
del healthcost_attr['sqrd_sd']

healthcost_attr['lower95'] = healthcost_attr['mean'] - 1.96 * healthcost_attr['sd']
healthcost_attr['upper95'] = healthcost_attr['mean'] + 1.96 * healthcost_attr['sd']

# Add to attribution data
ahle_combo_withattr = pd.concat(
    [ahle_combo_withattr ,healthcost_attr]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# =============================================================================
#### Add placeholder for attribution to specific diseases
# =============================================================================
# # Create placeholders
diseases_ext = pd.DataFrame({
    "cause":'External'
    ,"disease":['Cause 1' ,'Cause 2' ,'Cause 3' ,'Cause 4' ,'Cause 5']
    })
diseases_inf = pd.DataFrame({
    "cause":'Infectious'
    ,"disease":['Pathogen 1' ,'Pathogen 2' ,'Pathogen 3' ,'Pathogen 4' ,'Pathogen 5']
    })
diseases_non = pd.DataFrame({
    "cause":'Non-infectious'
    ,"disease":['Non-inf 1' ,'Non-inf 2' ,'Non-inf 3' ,'Non-inf 4' ,'Non-inf 5']
    })
diseases = pd.concat(
    [diseases_ext ,diseases_inf ,diseases_non]
    ,axis=0
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# # Merge
ahle_combo_withattr = pd.merge(
    left=ahle_combo_withattr
    ,right=diseases
    ,on='cause'
    ,how='outer'
    )
ahle_combo_withattr['median'] = ahle_combo_withattr['median'] / 5
ahle_combo_withattr['mean'] = ahle_combo_withattr['mean'] / 5
ahle_combo_withattr['sd'] = np.sqrt(ahle_combo_withattr['sd']**2 / 25)
ahle_combo_withattr['lower95'] = ahle_combo_withattr['mean'] - (1.96 * ahle_combo_withattr['sd'])
ahle_combo_withattr['upper95'] = ahle_combo_withattr['mean'] + (1.96 * ahle_combo_withattr['sd'])

# =============================================================================
#### Calculate as percent of total
# =============================================================================
total_ahle = ahle_combo_withattr['mean'].sum()
ahle_combo_withattr['pct_of_total'] = (ahle_combo_withattr['mean'] / total_ahle) * 100

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
# Split age and sex groups into their own columns
ahle_combo_withattr[['age_group' ,'sex']] = ahle_combo_withattr['group'].str.split(' ' ,expand=True)
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

# Reorder columns
cols_first = ['production_system' ,'group' ,'age_group' ,'sex' ,'ahle_component' ,'cause' ,'disease']
cols_other = [i for i in list(ahle_combo_withattr) if i not in cols_first]
ahle_combo_withattr = ahle_combo_withattr.reindex(columns=cols_first + cols_other)
datainfo(ahle_combo_withattr)

# Write CSV
# ahle_combo_withattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_withattr.csv') ,index=False)
ahle_combo_withattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_withattr_extra.csv') ,index=False)
