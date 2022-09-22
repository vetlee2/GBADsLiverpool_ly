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
    '1'

    # Arg 2: Folder location for saving output files
    ,ETHIOPIA_OUTPUT_FOLDER

    # Arg 3: full path to scenario control file
    ,os.path.join(ETHIOPIA_CODE_FOLDER ,'AHLE scenario parameters.xlsx')

    # Arg 4: only run the first N scenarios from the control file
    # -1: use all scenarios
    ,'-1'
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
    ,'-1'
]

timerstart()
run_cmd([r_executable ,r_script] + r_args ,SHOW_MAXLINES=99)
timerstop()

#%% Combine scenario result files

# =============================================================================
#### Merge scenarios
# =============================================================================
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

# -----------------------------------------------------------------------------
# Small ruminants
# -----------------------------------------------------------------------------
ahle_sheep_clm = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_CLM_S'
   ,label_species='Sheep'
   ,label_prodsys='Crop livestock mixed'
)
datainfo(ahle_sheep_clm)

ahle_sheep_past = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_Past_S'
   ,label_species='Sheep'
   ,label_prodsys='Pastoral'
)
datainfo(ahle_sheep_past)

ahle_goat_clm = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_CLM_G'
   ,label_species='Goat'
   ,label_prodsys='Crop livestock mixed'
)
datainfo(ahle_goat_clm)

ahle_goat_past = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_Past_G'
   ,label_species='Goat'
   ,label_prodsys='Pastoral'
)
datainfo(ahle_goat_past)

# -----------------------------------------------------------------------------
# Cattle
# -----------------------------------------------------------------------------
# These have a different naming pattern
ahle_cattle_clm = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_cattle_trial'
   ,input_file_suffixes=['CLM_current' ,'CLM_mortality_zero']
   ,label_species='Cattle'
   ,label_prodsys='Crop livestock mixed'
)
# Adjust column names to match small ruminants
ahle_cattle_clm.columns = ahle_cattle_clm.columns.str.replace('_clm' ,'')   # Remove _clm from names
ahle_cattle_clm.columns = ahle_cattle_clm.columns.str.replace('_mortality_zero' ,'_all_mortality_zero')
datainfo(ahle_cattle_clm)

ahle_cattle_past = combine_ahle_scenarios(
   input_folder=ETHIOPIA_OUTPUT_FOLDER
   ,input_file_prefix='ahle_cattle_trial'
   ,input_file_suffixes=['past_current' ,'past_mortality_zero']
   ,label_species='Cattle'
   ,label_prodsys='Pastoral'
)
# Adjust column names to match small ruminants
ahle_cattle_past.columns = ahle_cattle_past.columns.str.replace('_past' ,'')  # Remove _past from names
ahle_cattle_past.columns = ahle_cattle_past.columns.str.replace('_mortality_zero' ,'_all_mortality_zero')
datainfo(ahle_cattle_past)

# -----------------------------------------------------------------------------
# Stack species and production systems
# -----------------------------------------------------------------------------
concat_list = [
    ahle_sheep_clm
    ,ahle_sheep_past
    ,ahle_goat_clm
    ,ahle_goat_past
    ,ahle_cattle_clm
    ,ahle_cattle_past
]
ahle_combo = pd.concat(
   concat_list      # List of dataframes to concatenate
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# Split age and sex groups into their own columns
ahle_combo[['age_group' ,'sex']] = ahle_combo['group'].str.split(' ' ,expand=True)
ahle_combo.loc[ahle_combo['group'].str.upper() == 'OVERALL' ,'sex'] = 'Combined'

# Special handling for Oxen
ahle_combo.loc[ahle_combo['group'].str.upper() == 'OXEN' ,'age_group'] = 'Oxen'
ahle_combo.loc[ahle_combo['group'].str.upper() == 'OXEN' ,'sex'] = 'Male'

# Reorder columns
cols_first = ['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex']
cols_other = [i for i in list(ahle_combo) if i not in cols_first]
ahle_combo = ahle_combo.reindex(columns=cols_first + cols_other)

datainfo(ahle_combo)

# =============================================================================
#### Export
# =============================================================================
ahle_combo.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_stacked.csv') ,index=False)

#%% Checks on raw simulation output

ahle_combo_tocheck = ahle_combo.copy()

_group_overall = (ahle_combo_tocheck['group'].str.upper() == 'OVERALL')
_sex_combined = (ahle_combo_tocheck['sex'].str.upper() == 'COMBINED')
_item_grossmargin = (ahle_combo_tocheck['item'].str.upper() == 'GROSS MARGIN')

check_grossmargin_overall = ahle_combo_tocheck.loc[_group_overall].loc[_item_grossmargin]
check_grossmargin_overall.eval(
    #### Change in Gross Margin overall vs. individual ideal scenarios
    '''
    gmchange_ideal_overall = mean_ideal - mean_current

    gmchange_ideal_af = mean_ideal_af - mean_current
    gmchange_ideal_am = mean_ideal_am - mean_current
    gmchange_ideal_jf = mean_ideal_jf - mean_current
    gmchange_ideal_jm = mean_ideal_jm - mean_current
    gmchange_ideal_nf = mean_ideal_nf - mean_current
    gmchange_ideal_nm = mean_ideal_nm - mean_current
    gmchange_ideal_sumind = gmchange_ideal_af + gmchange_ideal_am \
        + gmchange_ideal_jf + gmchange_ideal_jm \
            + gmchange_ideal_nf + gmchange_ideal_nm

    gmchange_ideal_check = gmchange_ideal_sumind / gmchange_ideal_overall
    '''

    #### Mortality as proportion of total AHLE
    '''
    gmchange_dueto_mortality = mean_all_mortality_zero - mean_current
    gmchange_dueto_production = gmchange_ideal_overall - gmchange_dueto_mortality
    gmchange_dueto_mortality_prpn = gmchange_dueto_mortality / gmchange_ideal_overall
    '''
    ,inplace=True
)
print('Checking the change in Gross Margin for ideal overall vs. individual ideal scenarios')
print(check_grossmargin_overall[['species' ,'production_system' ,'gmchange_ideal_check']])

print('Checking mortality as proportion of total AHLE')
print(check_grossmargin_overall[['species' ,'production_system' ,'gmchange_dueto_mortality_prpn']])

# =============================================================================
#### Sum of agesex groups compared to system total for each item
# =============================================================================
#!!! The overall sum Gross Margin produced here is not equal to the overall
# Gross Margin coming out of the AHLE simulation!
# I have checked the simulation code and the elements of gross margin, production
# value and total expenditure, are equal to the sum of the individual agesex groups
# by definition. So, I believe the discrepancy is because we have only done a single
# run of the simulation, and some elements are far from their means by random chance.
# Check this again after running the simulation with several samples.

# Sum individual agesex groups for each item
check_agesex_sums = pd.DataFrame(ahle_combo_tocheck.loc[~ _sex_combined]\
    .groupby(['species' ,'production_system' ,'item'] ,observed=True)['mean_current'].sum())
check_agesex_sums.columns = ['mean_current_sumagesex']

# Merge group total for each item
check_agesex_sums = pd.merge(
    left=check_agesex_sums
    ,right=ahle_combo_tocheck.loc[_group_overall ,['species' ,'production_system' ,'item' ,'mean_current']]
    ,on=['species' ,'production_system' ,'item']
    ,how='left'
)

check_agesex_sums.eval(
    '''
    check_ratio = mean_current_sumagesex / mean_current
    '''
    ,inplace=True
)

#%% Add group summaries
'''
Creating aggregate groups for filtering in the dashboard
'''
# =============================================================================
#### Drop aggregate groups
# =============================================================================
# For consistency, drop any aggregate groups already in data
_agg_rows = (ahle_combo['age_group'].str.upper() == 'OVERALL') \
    | (ahle_combo['sex'].str.upper() == 'COMBINED')
ahle_combo_noagg = ahle_combo.loc[~ _agg_rows]

# Get distinct values for ages and sexes without aggregates
age_group_values = list(ahle_combo_noagg['age_group'].unique())
sex_values = list(ahle_combo_noagg['sex'].unique())

# =============================================================================
#### Build aggregate groups
# =============================================================================
# Only using MEAN and VARIANCE of each item, as the other statistics cannot
# be summed.
mean_cols = [i for i in list(ahle_combo) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo) if 'stdev' in i]

keepcols = ['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex'] \
    + mean_cols + sd_cols

ahle_combo_withagg = ahle_combo_noagg[keepcols].copy()
datainfo(ahle_combo_withagg)

# -----------------------------------------------------------------------------
# Create variance columns
# -----------------------------------------------------------------------------
# Relying on the following properties of sums of random variables:
#    mean(aX + bY) = a*mean(X) + b*mean(Y), regardless of correlation
#    var(aX + bY) = a^2*var(X) + b^2*var(Y), assuming X and Y are uncorrelated
var_cols = ['sqrd_' + COLNAME for COLNAME in sd_cols]
for i ,VARCOL in enumerate(var_cols):
   SDCOL = sd_cols[i]
   ahle_combo_withagg[VARCOL] = ahle_combo_withagg[SDCOL]**2

# -----------------------------------------------------------------------------
# Create Overall species, production system sum
# -----------------------------------------------------------------------------
#!!! Must be first sum to avoid double-counting!
ahle_combo_withagg_sumall = ahle_combo_withagg.pivot_table(
    index=['species' ,'production_system' ,'item']
    ,values=mean_cols + var_cols
    ,aggfunc='sum'
).reset_index()
ahle_combo_withagg_sumall['group'] = 'Overall'
ahle_combo_withagg_sumall['age_group'] = 'Overall'
ahle_combo_withagg_sumall['sex'] = 'Overall'

ahle_combo_withagg = pd.concat(
    [ahle_combo_withagg ,ahle_combo_withagg_sumall]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_withagg_sumall

# -----------------------------------------------------------------------------
# Create Overall sex for each age group
# -----------------------------------------------------------------------------
for AGE_GRP in age_group_values:
    ahle_combo_withagg_sumsexes = ahle_combo_withagg.query(f"age_group == '{AGE_GRP}'").pivot_table(
        index=['species' ,'production_system' ,'item' ,'age_group']
        ,values=mean_cols + var_cols
        ,aggfunc='sum'
    ).reset_index()
    ahle_combo_withagg_sumsexes['group'] = f'{AGE_GRP} Combined'
    ahle_combo_withagg_sumsexes['sex'] = 'Overall'

    # Stack
    ahle_combo_withagg = pd.concat(
        [ahle_combo_withagg ,ahle_combo_withagg_sumsexes]
        ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
        ,join='outer'        # 'outer': keep all index values from all data frames
        ,ignore_index=True   # True: do not keep index values on concatenation axis
    )
del ahle_combo_withagg_sumsexes

# -----------------------------------------------------------------------------
# Create Overall age group for each sex
# -----------------------------------------------------------------------------
for SEX_GRP in sex_values:
    ahle_combo_withagg_sumages = ahle_combo_withagg.query(f"sex == '{SEX_GRP}'").pivot_table(
        index=['species' ,'production_system' ,'item' ,'sex']
        ,values=mean_cols + var_cols
        ,aggfunc='sum'
    ).reset_index()
    ahle_combo_withagg_sumages['group'] = f'Overall {SEX_GRP}'
    ahle_combo_withagg_sumages['age_group'] = 'Overall'

    # Stack
    ahle_combo_withagg = pd.concat(
        [ahle_combo_withagg ,ahle_combo_withagg_sumages]
        ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
        ,join='outer'        # 'outer': keep all index values from all data frames
        ,ignore_index=True   # True: do not keep index values on concatenation axis
    )
del ahle_combo_withagg_sumages

# -----------------------------------------------------------------------------
# Create overall production system
# -----------------------------------------------------------------------------
ahle_combo_withagg_sumprod = ahle_combo_withagg.pivot_table(
   index=['species' ,'item' ,'group' ,'age_group' ,'sex']
   ,values=mean_cols + var_cols
   ,aggfunc='sum'
).reset_index()
ahle_combo_withagg_sumprod['production_system'] = 'Overall'

ahle_combo_withagg = pd.concat(
   [ahle_combo_withagg ,ahle_combo_withagg_sumprod]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_withagg_sumprod

# -----------------------------------------------------------------------------
# Create overall species
# -----------------------------------------------------------------------------
ahle_combo_withagg_sumspec = ahle_combo_withagg.query("species.str.upper().isin(['SHEEP' ,'GOAT'])").pivot_table(
   index=['production_system' ,'item' ,'group' ,'age_group' ,'sex']
   ,values=mean_cols + var_cols
   ,aggfunc='sum'
).reset_index()
ahle_combo_withagg_sumspec['species'] = 'All small ruminants'

ahle_combo_withagg = pd.concat(
   [ahle_combo_withagg ,ahle_combo_withagg_sumspec]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_withagg_sumspec

# -----------------------------------------------------------------------------
# Calculate standard deviations
# -----------------------------------------------------------------------------
# Will overwrite standard deviations for the handful of groups that have them,
# but that's OK.
for i ,VARCOL in enumerate(var_cols):
   SDCOL = sd_cols[i]
   ahle_combo_withagg[SDCOL] = np.sqrt(ahle_combo_withagg[VARCOL])

datainfo(ahle_combo_withagg)

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo_withagg['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo_withagg = pd.merge(
    left=ahle_combo_withagg
    ,right=exchg_data_tomerge
    ,on='country_name'
    ,how='left'
    )
del ahle_combo_withagg['country_name']

# Add columns in USD for appropriate items
currency_items_containing = ['cost' ,'value' ,'margin' ,'expenditure']
currency_items = []
for STR in currency_items_containing:
   currency_items = currency_items + [item for item in ahle_combo_withagg['item'].unique() if STR.upper() in item.upper()]

for MEANCOL in mean_cols:
   MEANCOL_USD = MEANCOL + '_usd'
   ahle_combo_withagg.loc[ahle_combo_withagg['item'].isin(currency_items) ,MEANCOL_USD] = \
      ahle_combo_withagg[MEANCOL] / ahle_combo_withagg['exchg_rate_lcuperusdol']

# For standard deviations, convert to variances then scale by the squared exchange rate
# VAR(aX) = a^2 * VAR(X).  a = 1/exchange rate.
for SDCOL in sd_cols:
   SDCOL_USD = SDCOL + '_usd'
   ahle_combo_withagg.loc[ahle_combo_withagg['item'].isin(currency_items) ,SDCOL_USD] = \
      np.sqrt(ahle_combo_withagg[SDCOL]**2 / ahle_combo_withagg['exchg_rate_lcuperusdol']**2)

datainfo(ahle_combo_withagg)

# =============================================================================
#### Cleanup and Export
# =============================================================================
keepcols = [
    'species',
    'production_system',
    'item',
    'group',
    'age_group',
    'sex',

    'mean_current',
    'mean_ideal',
    'mean_all_mortality_zero',
    'stdev_current',
    'stdev_ideal',
    'stdev_all_mortality_zero',

    'mean_current_usd',
    'mean_ideal_usd',
    'mean_all_mortality_zero_usd',
    'stdev_current_usd',
    'stdev_ideal_usd',
    'stdev_all_mortality_zero_usd',
]

ahle_combo_summary = ahle_combo_withagg[keepcols].copy()
ahle_combo_summary = ahle_combo_summary.rename(
    columns={'mean_all_mortality_zero':'mean_mortality_zero' ,'stdev_all_mortality_zero':'stdev_mortality_zero'})

datainfo(ahle_combo_summary)

ahle_combo_summary.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.csv') ,index=False)

#%% Calculate AHLE for each scenario
'''
Since overall gross margin is calculated in the base simulation code, and due to
uncertainties I have about my aggregation code, this uses the basic ahle_combo
data instead of ahle_combo_withagg.
'''
# =============================================================================
#### Restructure
# =============================================================================
# For AHLE calcs, we want each item in a column
# Only need items 'gross margin' and 'health cost'
# Only need the system total: 'Overall' group
# Need means and standard deviations for later calculations
mean_cols = [i for i in list(ahle_combo_withagg) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo_withagg) if 'stdev' in i]

_rows_for_ahle = (ahle_combo_withagg['item'].str.upper().isin(['GROSS MARGIN' ,'HEALTH COST'])) \
    & (ahle_combo_withagg['group'].str.upper() == 'OVERALL')

ahle_combo_withagg_p = ahle_combo_withagg.loc[_rows_for_ahle].pivot(
    index=['species' ,'production_system' ,'group' ,'age_group' ,'sex']
    ,columns='item'
    ,values=mean_cols + sd_cols
).reset_index()
ahle_combo_withagg_p = colnames_from_index(ahle_combo_withagg_p)   # Change multi-index to column names
cleancolnames(ahle_combo_withagg_p)

# Remove underscores added when collapsing column index
ahle_combo_withagg_p = ahle_combo_withagg_p.rename(
    columns={
        'species_':'species'
        ,'production_system_':'production_system'
        ,'group_':'group'
        ,'age_group_':'age_group'
        ,'sex_':'sex'
    }
)

datainfo(ahle_combo_withagg_p)

# =============================================================================
#### Calculate AHLE
# =============================================================================
'''
Calculating mean and standard deviation for each AHLE component.
Relying on the following properties of sums of random variables:
    mean(aX + bY) = a*mean(X) + b*mean(Y), regardless of correlation
    var(aX + bY) = a^2*var(X) + b^2*var(Y), assuming X and Y are uncorrelated
'''
ahle_combo_withahle = ahle_combo_withagg_p.copy()

ahle_combo_withahle.eval(
    '''
    ahle_total_mean = mean_ideal_gross_margin - mean_current_gross_margin

    ahle_dueto_mortality_mean = mean_all_mortality_zero_gross_margin - mean_current_gross_margin
    ahle_dueto_healthcost_mean = mean_current_health_cost
    ahle_dueto_productionloss_mean = ahle_total_mean - ahle_dueto_mortality_mean - ahle_dueto_healthcost_mean

    ahle_justfor_af_mean = mean_ideal_af_gross_margin - mean_current_gross_margin
    ahle_justfor_am_mean = mean_ideal_am_gross_margin - mean_current_gross_margin
    ahle_justfor_jf_mean = mean_ideal_jf_gross_margin - mean_current_gross_margin
    ahle_justfor_jm_mean = mean_ideal_jm_gross_margin - mean_current_gross_margin
    ahle_justfor_nf_mean = mean_ideal_nf_gross_margin - mean_current_gross_margin
    ahle_justfor_nm_mean = mean_ideal_nm_gross_margin - mean_current_gross_margin
    '''
    # Repeat for USD
    '''
    ahle_total_usd_mean = mean_ideal_usd_gross_margin - mean_current_usd_gross_margin

    ahle_dueto_mortality_usd_mean = mean_all_mortality_zero_usd_gross_margin - mean_current_usd_gross_margin
    ahle_dueto_healthcost_usd_mean = mean_current_usd_health_cost
    ahle_dueto_productionloss_usd_mean = ahle_total_usd_mean - ahle_dueto_mortality_usd_mean - ahle_dueto_healthcost_usd_mean

    ahle_justfor_af_usd_mean = mean_ideal_af_usd_gross_margin - mean_current_usd_gross_margin
    ahle_justfor_am_usd_mean = mean_ideal_am_usd_gross_margin - mean_current_usd_gross_margin
    ahle_justfor_jf_usd_mean = mean_ideal_jf_usd_gross_margin - mean_current_usd_gross_margin
    ahle_justfor_jm_usd_mean = mean_ideal_jm_usd_gross_margin - mean_current_usd_gross_margin
    ahle_justfor_nf_usd_mean = mean_ideal_nf_usd_gross_margin - mean_current_usd_gross_margin
    ahle_justfor_nm_usd_mean = mean_ideal_nm_usd_gross_margin - mean_current_usd_gross_margin
    '''
    ,inplace=True
)

# Standard deviations require summing variances and taking square root
# Must be done outside eval()
ahle_combo_withahle['ahle_total_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])

ahle_combo_withahle['ahle_dueto_mortality_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_all_mortality_zero_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])
ahle_combo_withahle['ahle_dueto_healthcost_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_current_health_cost'])
ahle_combo_withahle['ahle_dueto_productionloss_stdev'] = np.sqrt(ahle_combo_withahle['ahle_total_stdev']**2 + ahle_combo_withahle['ahle_dueto_mortality_stdev']**2 + ahle_combo_withahle['ahle_dueto_healthcost_stdev']**2)

ahle_combo_withahle['ahle_justfor_af_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_af_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])
ahle_combo_withahle['ahle_justfor_am_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_am_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])
ahle_combo_withahle['ahle_justfor_jf_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_jf_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])
ahle_combo_withahle['ahle_justfor_jm_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_jm_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])
ahle_combo_withahle['ahle_justfor_nf_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_nf_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])
ahle_combo_withahle['ahle_justfor_nm_stdev'] = np.sqrt(ahle_combo_withahle['sqrd_stdev_ideal_nm_gross_margin'] + ahle_combo_withahle['sqrd_stdev_current_gross_margin'])

# Repeat for USD
ahle_combo_withahle['ahle_total_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)

ahle_combo_withahle['ahle_dueto_mortality_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_all_mortality_zero_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)
ahle_combo_withahle['ahle_dueto_healthcost_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_current_usd_health_cost']**2)
ahle_combo_withahle['ahle_dueto_productionloss_usd_stdev'] = np.sqrt(ahle_combo_withahle['ahle_total_usd_stdev']**2 + ahle_combo_withahle['ahle_dueto_mortality_usd_stdev']**2 + ahle_combo_withahle['ahle_dueto_healthcost_usd_stdev']**2)

ahle_combo_withahle['ahle_justfor_af_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_af_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)
ahle_combo_withahle['ahle_justfor_am_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_am_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)
ahle_combo_withahle['ahle_justfor_jf_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_jf_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)
ahle_combo_withahle['ahle_justfor_jm_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_jm_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)
ahle_combo_withahle['ahle_justfor_nf_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_nf_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)
ahle_combo_withahle['ahle_justfor_nm_usd_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_nm_usd_gross_margin']**2 + ahle_combo_withahle['stdev_current_usd_gross_margin']**2)

# =============================================================================
#### Cleanup and export
# =============================================================================
ahle_cols = [i for i in list(ahle_combo_withahle) if 'ahle' in i]
keepcols = ['species' ,'production_system'] + ahle_cols

ahle_combo_withahle = ahle_combo_withahle[keepcols]
datainfo(ahle_combo_withahle)

ahle_combo_withahle.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.csv') ,index=False)

#%% === Break ===
'''
I'm revisiting everything below this line
'''

#%% Create scenario summary view
'''
This produces a summary data set with a different structure than before. This uses
only the total system value for each item (dropping the age/sex-specific values).
It then creates a row for each scenario. Scenarios set either specific age/sex
groups to ideal conditions or all age/sex groups simultaneously. In all cases, the
total system values are reported.

For example, the ideal_AF scenario sets Adult Females to ideal conditions while
leaving other age/sex groups at their current conditions; the resulting values are
the total system values of gross margin, health cost, etc., when Adult Females are at
their ideal.
'''
# =============================================================================
#### Create a row for each age*sex and the overall scenario
# =============================================================================
scenario_basetable = pd.DataFrame({
   'agesex_scenario':[
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
ahle_combo_scensmry = pd.merge(
   left=scenario_basetable
   ,right=ahle_combo_raw.query("group.str.upper() == 'OVERALL'")    # Keep only Total System results (group = "Overall")
   ,on='group'
   ,how='outer'
   )

# Rename agesex_scenario and drop plain group
# Note: in ahle_combo_scensmry, the 'group' column designates the SCENARIO being
# represented. This is different from the meaning of 'group' in the raw simulation
# output.
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns='group').rename(columns={'agesex_scenario':'group'})

# Split age and sex groups into their own columns
ahle_combo_scensmry[['age_group' ,'sex']] = ahle_combo_scensmry['group'].str.split(' ' ,expand=True)
ahle_combo_scensmry['group'] = ahle_combo_scensmry['group'].replace({'Overall Overall':'Overall'})

# =============================================================================
#### Assign results from correct scenario to each group
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
ahle_combo_scensmry[['mean_mortality_zero_touse' ,'stdev_mortality_zero_touse' ,'mean_ideal_touse' ,'stdev_ideal_touse']] = ahle_combo_scensmry.apply(create_means_touse ,axis=1)      # Apply to each row of the dataframe (axis=1)
datainfo(ahle_combo_scensmry)

# Create subset of columns for checking
mean_cols = [i for i in list(ahle_combo_scensmry) if 'mean' in i]
keep_cols = [
   'species'
   ,'production_system'
   ,'item'
   ,'group'
   ,'age_group'
   ,'sex'
   ] + mean_cols
ahle_combo_scensmry_tocheck = ahle_combo_scensmry[keep_cols].copy()

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
ahle_combo_scensmry = ahle_combo_scensmry[keep_cols].copy()
ahle_combo_scensmry = ahle_combo_scensmry.rename(columns={
   'mean_mortality_zero_touse':'mean_mortality_zero'
   ,'stdev_mortality_zero_touse':'stdev_mortality_zero'
   ,'mean_ideal_touse':'mean_ideal'
   ,'stdev_ideal_touse':'stdev_ideal'
   })
datainfo(ahle_combo_scensmry)

# =============================================================================
#### Add group summaries
# =============================================================================
#!!! Model output items for individual age/sex scenarios don't sum!
# For now, using MAX
# Only the AHLE (gross margin DIFFERENCE between ideal and current) is expected to sum
#!!! Revisit this. The structure isn't right. Don't need all output items for each scenario.
#!!! Only need items 'gross margin' and 'health cost' to calculate AHLE. Then, only need to sum AHLE.

ahle_combo = ahle_combo_scensmry.copy()

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
# #!!! Must be first sum to avoid double-counting!
# # Update: this already exists on data
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
#### Export
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
# ahle_combo.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.csv') ,index=False)

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
