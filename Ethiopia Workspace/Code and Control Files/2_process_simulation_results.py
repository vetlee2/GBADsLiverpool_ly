#%% About
'''
'''
#%% Setup

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

            ,'all_mort_25_imp'
            ,'mort_25_imp_AF'
            ,'mort_25_imp_AM'
            ,'mort_25_imp_J'
            ,'mort_25_imp_N'

            ,'all_mort_50_imp'
            ,'mort_50_imp_AF'
            ,'mort_50_imp_AM'
            ,'mort_50_imp_J'
            ,'mort_50_imp_N'

            ,'all_mort_75_imp'
            ,'mort_75_imp_AF'
            ,'mort_75_imp_AM'
            ,'mort_75_imp_J'
            ,'mort_75_imp_N'

            ,'Current_growth_25_imp_All'
            ,'Current_growth_25_imp_AF'
            ,'Current_growth_25_imp_AM'
            ,'Current_growth_25_imp_JF'
            ,'Current_growth_25_imp_JM'
            ,'Current_growth_25_imp_NF'
            ,'Current_growth_25_imp_NM'

            ,'Current_growth_50_imp_All'
            ,'Current_growth_50_imp_AF'
            ,'Current_growth_50_imp_AM'
            ,'Current_growth_50_imp_JF'
            ,'Current_growth_50_imp_JM'
            ,'Current_growth_50_imp_NF'
            ,'Current_growth_50_imp_NM'

            ,'Current_growth_75_imp_All'
            ,'Current_growth_75_imp_AF'
            ,'Current_growth_75_imp_AM'
            ,'Current_growth_75_imp_JF'
            ,'Current_growth_75_imp_JM'
            ,'Current_growth_75_imp_NF'
            ,'Current_growth_75_imp_NM'

            ,'Current_growth_100_imp_All'
            ,'Current_growth_100_imp_AF'
            ,'Current_growth_100_imp_AM'
            ,'Current_growth_100_imp_JF'
            ,'Current_growth_100_imp_JM'
            ,'Current_growth_100_imp_NF'
            ,'Current_growth_100_imp_NM'

            ,'Current_repro_25_imp'
            ,'Current_repro_50_imp'
            ,'Current_repro_75_imp'
            ,'Current_repro_100_imp'
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

check_ahle_combo = ahle_combo.copy()

_group_overall = (check_ahle_combo['group'].str.upper() == 'OVERALL')
_sex_combined = (check_ahle_combo['sex'].str.upper() == 'COMBINED')
_item_grossmargin = (check_ahle_combo['item'].str.upper() == 'GROSS MARGIN')

check_grossmargin_overall = check_ahle_combo.loc[_group_overall].loc[_item_grossmargin]
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
print('\n> Checking the change in Gross Margin for ideal overall vs. individual ideal scenarios')
print(check_grossmargin_overall[['species' ,'production_system' ,'gmchange_ideal_check']])

print('\n> Checking mortality as proportion of total AHLE')
print(check_grossmargin_overall[['species' ,'production_system' ,'gmchange_dueto_mortality_prpn']])

# =============================================================================
#### Sum of agesex groups compared to system total for each item
# =============================================================================
#!!! The overall sum Gross Margin produced here is not equal to the overall
# Gross Margin coming out of the AHLE simulation!
# I have checked the simulation code, and the elements of gross margin - production
# value and total expenditure - are equal to the sum of the individual agesex groups
# by definition. So, I believe the discrepancy is because we have only done a single
# run of the simulation, and some elements are far from their means by random chance.
# Check this again after running the simulation with several samples.

# Sum individual agesex groups for each item
check_agesex_sums = pd.DataFrame(check_ahle_combo.loc[~ _sex_combined]\
    .groupby(['species' ,'production_system' ,'item'] ,observed=True)['mean_current'].sum())
check_agesex_sums.columns = ['mean_current_sumagesex']

# Merge group total for each item
check_agesex_sums = pd.merge(
    left=check_agesex_sums
    ,right=check_ahle_combo.loc[_group_overall ,['species' ,'production_system' ,'item' ,'mean_current']]
    ,on=['species' ,'production_system' ,'item']
    ,how='left'
)
check_agesex_sums = check_agesex_sums.rename(columns={'mean_current':'mean_current_overall'})

check_agesex_sums.eval(
    '''
    check_ratio = mean_current_sumagesex / mean_current_overall
    '''
    ,inplace=True
)
print('\n> Checking the sum of individual age/sex compared to the overall for each item')
print('Maximum ratio')
print(check_agesex_sums.groupby(['species' ,'production_system'])['check_ratio'].max())
print('Minimum ratio')
print(check_agesex_sums.groupby(['species' ,'production_system'])['check_ratio'].min())

#%% Restructure scenarios
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

Plan to minimize changes needed in Dash:
    Columns will retain names of system total scenarios, e.g:
        mean_ideal, mean_mortality_zero, mean_all_mort_25_imp, mean_current_repro_25_imp, mean_current_growth_25_imp_all
        mean_ideal_usd, mean_mortality_zero_usd, etc.
    Rows will be added to signify the scope of each scenario, e.g.:
        Where Group == 'Overall', entry is result of system total scenario
        Where Group == 'AF', entry is result of AF-specific scenario
'''
# =============================================================================
#### Create a row for each age*sex scenario and the overall scenarios
# =============================================================================
scenario_basetable = pd.DataFrame({
   'agesex_scenario':[
      'Neonatal Female'
      ,'Neonatal Male'

      ,'Juvenile Female'
      ,'Juvenile Male'

      ,'Adult Female'
      ,'Adult Male'

      ,'Overall'
      ]
   ,'group':'Overall'
   })
ahle_combo_scensmry = pd.merge(
   left=scenario_basetable
   ,right=ahle_combo.query("group.str.upper() == 'OVERALL'")    # Keep only Total System results (group = "Overall")
   ,on='group'
   ,how='outer'
   )

# =============================================================================
#### Assign results from correct scenario column to each row
# =============================================================================
'''
Note that current scenario column applies to every row.
'''
def fill_column_where(
        DATAFRAME           # Dataframe
        ,LOC                # Dataframe mask e.g. _loc = (df['col'] == 'Value')
        ,COLUMN_TOFILL      # String
        ,COLUMN_TOUSE       # String
    ):
    dfmod = DATAFRAME.copy()
    dfmod.loc[LOC ,COLUMN_TOFILL] = dfmod.loc[LOC ,COLUMN_TOUSE]
    return dfmod

# -----------------------------------------------------------------------------
# Adult Female
# -----------------------------------------------------------------------------
_scen_af = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'ADULT FEMALE')
print(f"> Selected {_scen_af.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_ideal' ,'mean_ideal_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_ideal' ,'stdev_ideal_af')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mortality_zero' ,'mean_mortality_zero_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mortality_zero' ,'stdev_mortality_zero_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_af')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_af')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_af')

# Reproduction scenario already applies to adult females
# 'mean_current_repro_25_imp'
# 'mean_current_repro_50_imp'
# 'mean_current_repro_75_imp'
# 'mean_current_repro_100_imp'

# Drop columns for group specific scenario
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_af' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# -----------------------------------------------------------------------------
# Adult Male
# -----------------------------------------------------------------------------
_scen_am = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'ADULT MALE')
print(f"> Selected {_scen_am.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_ideal' ,'mean_ideal_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_ideal' ,'stdev_ideal_am')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mortality_zero' ,'mean_mortality_zero_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mortality_zero' ,'stdev_mortality_zero_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_am')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_am')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_am')

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_100_imp'] = np.nan

# Drop columns for group specific scenario
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_am' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# -----------------------------------------------------------------------------
# Juvenile Female
# -----------------------------------------------------------------------------
_scen_jf = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'JUVENILE FEMALE')
print(f"> Selected {_scen_jf.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_ideal' ,'mean_ideal_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_ideal' ,'stdev_ideal_jf')

# For juveniles, mortality scenarios are not sex specific
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mortality_zero' ,'mean_mortality_zero_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mortality_zero' ,'stdev_mortality_zero_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_j')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_jf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_jf')

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_100_imp'] = np.nan

# Drop columns for group specific scenario
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_jf' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# -----------------------------------------------------------------------------
# Juvenile Male
# -----------------------------------------------------------------------------
_scen_jm = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'JUVENILE MALE')
print(f"> Selected {_scen_jm.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_ideal' ,'mean_ideal_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_ideal' ,'stdev_ideal_jm')

# For juveniles, mortality scenarios are not sex specific
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mortality_zero' ,'mean_mortality_zero_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mortality_zero' ,'stdev_mortality_zero_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_j')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_j')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_jm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_jm')

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_100_imp'] = np.nan

# Drop columns for group specific scenario
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_jm' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# Further: drop columns for juveniles that are not sex-specific
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_j' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# -----------------------------------------------------------------------------
# Neonatal Female
# -----------------------------------------------------------------------------
_scen_nf = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'NEONATAL FEMALE')
print(f"> Selected {_scen_nf.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_ideal' ,'mean_ideal_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_ideal' ,'stdev_ideal_nf')

# For neonates, mortality scenarios are not sex specific
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mortality_zero' ,'mean_mortality_zero_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mortality_zero' ,'stdev_mortality_zero_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_n')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_nf')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_nf')

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_100_imp'] = np.nan

# Drop columns for group specific scenario
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_nf' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# -----------------------------------------------------------------------------
# Neonatal Male
# -----------------------------------------------------------------------------
_scen_nm = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'NEONATAL MALE')
print(f"> Selected {_scen_nm.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_ideal' ,'mean_ideal_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_ideal' ,'stdev_ideal_nm')

# For neonates, mortality scenarios are not sex specific
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mortality_zero' ,'mean_mortality_zero_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mortality_zero' ,'stdev_mortality_zero_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_n')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_n')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_nm')
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_nm')

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_100_imp'] = np.nan

# Drop columns for group specific scenario
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_nm' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# Further: drop columns for neonates that are not sex-specific
_scen_cols = [i for i in list(ahle_combo_scensmry) if '_n' in i]
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=_scen_cols)

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo_scensmry['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo_scensmry = pd.merge(
    left=ahle_combo_scensmry
    ,right=exchg_data_tomerge
    ,on='country_name'
    ,how='left'
    )
del ahle_combo_scensmry['country_name']

# Add columns in USD for appropriate items
currency_items_containing = ['cost' ,'value' ,'margin' ,'expenditure']
currency_items = []
for STR in currency_items_containing:
   currency_items = currency_items + [item for item in ahle_combo_scensmry['item'].unique() if STR.upper() in item.upper()]

mean_cols = [i for i in list(ahle_combo_scensmry) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo_scensmry) if 'stdev' in i]

for MEANCOL in mean_cols:
   MEANCOL_USD = MEANCOL + '_usd'
   ahle_combo_scensmry.loc[ahle_combo_scensmry['item'].isin(currency_items) ,MEANCOL_USD] = \
      ahle_combo_scensmry[MEANCOL] / ahle_combo_scensmry['exchg_rate_lcuperusdol']

# For standard deviations, convert to variances then scale by the squared exchange rate
# VAR(aX) = a^2 * VAR(X).  a = 1/exchange rate.
for SDCOL in sd_cols:
   SDCOL_USD = SDCOL + '_usd'
   ahle_combo_scensmry.loc[ahle_combo_scensmry['item'].isin(currency_items) ,SDCOL_USD] = \
      np.sqrt(ahle_combo_scensmry[SDCOL]**2 / ahle_combo_scensmry['exchg_rate_lcuperusdol']**2)

# =============================================================================
#### Cleanup and export
# =============================================================================
# Drop columns with unused distributional attributes
drop_distr_containing = ['min_' ,'q1_' ,'median_' ,'q3_' ,'max_']
drop_distr_cols = []
for STR in drop_distr_containing:
   drop_distr_cols = drop_distr_cols + [item for item in list(ahle_combo_scensmry) if STR.upper() in item.upper()]

# Drop columns with original age/sex groups (this file uses only the Overall group)
dropcols = ['group' ,'age_group' ,'sex'] + drop_distr_cols
ahle_combo_scensmry = ahle_combo_scensmry.drop(columns=dropcols)

# Rename columns to match previous file
ahle_combo_scensmry = ahle_combo_scensmry.rename(
    columns={
        'mean_all_mortality_zero':'mean_mortality_zero'
        ,'stdev_all_mortality_zero':'stdev_mortality_zero'

        ,'mean_all_mortality_zero_usd':'mean_mortality_zero_usd'
        ,'stdev_all_mortality_zero_usd':'stdev_mortality_zero_usd'
        }
    )

datainfo(ahle_combo_scensmry)

ahle_combo_scensmry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry.csv') ,index=False)
ahle_combo_scensmry.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry.pkl.gz'))

#%% === BREAK ===
'''
Old code below this line.
'''
#%% Add group summaries
'''
Creating aggregate groups for filtering in the dashboard
'''
mean_cols = [i for i in list(ahle_combo) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo) if 'stdev' in i]

# =============================================================================
#### Drop aggregate groups
# =============================================================================
# Some items only exist for Overall group in original file. Get all existing Overall records.
ahle_combo_overall = ahle_combo.loc[ahle_combo['group'].str.upper() == 'OVERALL'].copy()

# Rename sex to agree with newer convention
ahle_combo_overall['sex'] = 'Overall'

# Create version without any aggregate groups
_agg_rows = (ahle_combo['age_group'].str.upper() == 'OVERALL') \
    | (ahle_combo['sex'].str.upper() == 'COMBINED')
ahle_combo_indiv = ahle_combo.loc[~ _agg_rows].copy()

# Get distinct values for ages and sexes without aggregates
age_group_values = list(ahle_combo_indiv['age_group'].unique())
sex_values = list(ahle_combo_indiv['sex'].unique())

# =============================================================================
#### Add placeholder items
# =============================================================================
# # Get all combinations of key variables without item
# item_placeholder = ahle_combo_indiv[['species' ,'production_system' ,'group' ,'age_group' ,'sex']].drop_duplicates()
# item_placeholder['item'] = 'Cost of Infrastructure'

# # Stack placeholder item(s) with individual data
# ahle_combo_withplaceholders = pd.concat(
#     [ahle_combo_indiv ,item_placeholder]
#     ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
#     ,join='outer'        # 'outer': keep all index values from all data frames
#     ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # Placeholder items get mean and SD zero
# for COL in [mean_cols + sd_cols]:
#     ahle_combo_withplaceholders[COL] = ahle_combo_withplaceholders[COL].replace(np.nan ,0)

# =============================================================================
#### Build aggregate groups
# =============================================================================
# Only using MEAN and VARIANCE of each item, as the other statistics cannot
# be summed.
keepcols = ['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex'] \
    + mean_cols + sd_cols

ahle_combo_withagg = ahle_combo_indiv[keepcols].copy()
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

# Oxen are a special age group which is only male. Drop "combined" sex.
_oxen_combined = (ahle_combo_withagg['group'].str.upper() == 'OXEN COMBINED')
ahle_combo_withagg = ahle_combo_withagg.drop(ahle_combo_withagg.loc[_oxen_combined].index).reset_index(drop=True)

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
# Add back original Overall and de-dup
# -----------------------------------------------------------------------------
# Concatenate original Overall group data
ahle_combo_withagg = pd.concat(
   [ahle_combo_withagg ,ahle_combo_overall]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# De-Dup, keeping new Overall group if it exists
ahle_combo_withagg = ahle_combo_withagg.drop_duplicates(
   subset=['species' ,'production_system' ,'item' ,'group']       # List (opt): only consider these columns when identifying duplicates. If None, consider all columns.
   ,keep='first'                   # String: which occurrence to keep, 'first' or 'last'
)

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
   del ahle_combo_withagg[VARCOL]

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
# -----------------------------------------------------------------------------
# Remove rows added by Github
# -----------------------------------------------------------------------------
# Hoping this is due to a one-time file merge issue
_git_rows = (ahle_combo_withagg['item'].str.contains('>>>')) \
    | (ahle_combo_withagg['item'].str.contains('<<<')) \
        | (ahle_combo_withagg['item'].str.contains('==='))

ahle_combo_withagg = ahle_combo_withagg.loc[~ _git_rows]

# -----------------------------------------------------------------------------
# Subset and rename columns
# -----------------------------------------------------------------------------
# In this file, keeping only scenarios that apply to all groups
keepcols = [
    'species'
    ,'production_system'
    ,'item'
    ,'group'
    ,'age_group'
    ,'sex'

    # In Birr
    ,'mean_current'
    ,'stdev_current'
    ,'mean_ideal'
    ,'stdev_ideal'

    ,'mean_all_mort_25_imp'
    ,'mean_all_mort_50_imp'
    ,'mean_all_mort_75_imp'
    ,'mean_all_mortality_zero'
    ,'stdev_all_mortality_zero'

    ,'mean_current_repro_25_imp'
    ,'mean_current_repro_50_imp'
    ,'mean_current_repro_75_imp'
    ,'mean_current_repro_100_imp'

    ,'mean_current_growth_25_imp_all'
    ,'mean_current_growth_50_imp_all'
    ,'mean_current_growth_75_imp_all'
    ,'mean_current_growth_100_imp_all'

    # In USD
    ,'mean_current_usd'
    ,'stdev_current_usd'
    ,'mean_ideal_usd'
    ,'stdev_ideal_usd'

    ,'mean_all_mort_25_imp_usd'
    ,'mean_all_mort_50_imp_usd'
    ,'mean_all_mort_75_imp_usd'
    ,'mean_all_mortality_zero_usd'
    ,'stdev_all_mortality_zero_usd'

    ,'mean_current_repro_25_imp_usd'
    ,'mean_current_repro_50_imp_usd'
    ,'mean_current_repro_75_imp_usd'
    ,'mean_current_repro_100_imp_usd'

    ,'mean_current_growth_25_imp_all_usd'
    ,'mean_current_growth_50_imp_all_usd'
    ,'mean_current_growth_75_imp_all_usd'
    ,'mean_current_growth_100_imp_all_usd'
]

ahle_combo_withagg_smry = ahle_combo_withagg[keepcols].copy()
ahle_combo_withagg_smry = ahle_combo_withagg_smry.rename(
    columns={
        'mean_all_mortality_zero':'mean_mortality_zero'
        ,'stdev_all_mortality_zero':'stdev_mortality_zero'
        ,'mean_all_mortality_zero_usd':'mean_mortality_zero_usd'
        ,'stdev_all_mortality_zero_usd':'stdev_mortality_zero_usd'
        }
    )

datainfo(ahle_combo_withagg_smry)

ahle_combo_withagg_smry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.csv') ,index=False)
ahle_combo_withagg_smry.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.pkl.gz'))

#%% Calculate AHLE for each scenario

# =============================================================================
#### Restructure
# =============================================================================
# For AHLE calcs, we want each item in a column
# Only need items 'gross margin' and 'health cost'
# Only need the system total: 'Overall' group
# Need means and standard deviations for later calculations
mean_cols = [i for i in list(ahle_combo_withagg) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo_withagg) if 'stdev' in i]

_items_for_ahle = (ahle_combo_withagg['item'].str.upper().isin(['GROSS MARGIN' ,'HEALTH COST']))

ahle_combo_withagg_p = ahle_combo_withagg.loc[_items_for_ahle].pivot(
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
    # Scenarios that change all age/sex groups
    '''
    ahle_total_mean = mean_ideal_gross_margin - mean_current_gross_margin
    ahle_dueto_mortality_mean = mean_all_mortality_zero_gross_margin - mean_current_gross_margin
    ahle_dueto_healthcost_mean = mean_current_health_cost
    ahle_dueto_productionloss_mean = ahle_total_mean - ahle_dueto_mortality_mean - ahle_dueto_healthcost_mean

    ahle_when_repro_imp25_mean = mean_current_repro_25_imp_gross_margin - mean_current_gross_margin
    ahle_when_repro_imp50_mean = mean_current_repro_50_imp_gross_margin - mean_current_gross_margin
    ahle_when_repro_imp75_mean = mean_current_repro_75_imp_gross_margin - mean_current_gross_margin
    ahle_when_repro_imp100_mean = mean_current_repro_100_imp_gross_margin - mean_current_gross_margin

    ahle_when_af_ideal_mean = mean_ideal_af_gross_margin - mean_current_gross_margin
    ahle_when_am_ideal_mean = mean_ideal_am_gross_margin - mean_current_gross_margin
    ahle_when_jf_ideal_mean = mean_ideal_jf_gross_margin - mean_current_gross_margin
    ahle_when_jm_ideal_mean = mean_ideal_jm_gross_margin - mean_current_gross_margin
    ahle_when_nf_ideal_mean = mean_ideal_nf_gross_margin - mean_current_gross_margin
    ahle_when_nm_ideal_mean = mean_ideal_nm_gross_margin - mean_current_gross_margin

    ahle_when_af_mort_imp25_mean = mean_mort_25_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_mort_imp25_mean = mean_mort_25_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_j_mort_imp25_mean = mean_mort_25_imp_j_gross_margin - mean_current_gross_margin
    ahle_when_n_mort_imp25_mean = mean_mort_25_imp_n_gross_margin - mean_current_gross_margin

    ahle_when_af_mort_imp50_mean = mean_mort_50_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_mort_imp50_mean = mean_mort_50_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_j_mort_imp50_mean = mean_mort_50_imp_j_gross_margin - mean_current_gross_margin
    ahle_when_n_mort_imp50_mean = mean_mort_50_imp_n_gross_margin - mean_current_gross_margin

    ahle_when_af_mort_imp75_mean = mean_mort_75_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_mort_imp75_mean = mean_mort_75_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_j_mort_imp75_mean = mean_mort_75_imp_j_gross_margin - mean_current_gross_margin
    ahle_when_n_mort_imp75_mean = mean_mort_75_imp_n_gross_margin - mean_current_gross_margin

    ahle_when_af_mort_imp100_mean = mean_mortality_zero_af_gross_margin - mean_current_gross_margin
    ahle_when_am_mort_imp100_mean = mean_mortality_zero_am_gross_margin - mean_current_gross_margin
    ahle_when_j_mort_imp100_mean = mean_mortality_zero_j_gross_margin - mean_current_gross_margin
    ahle_when_n_mort_imp100_mean = mean_mortality_zero_n_gross_margin - mean_current_gross_margin

    ahle_when_all_growth_imp25_mean = mean_current_growth_25_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_af_growth_imp25_mean = mean_current_growth_25_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_growth_imp25_mean = mean_current_growth_25_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_jf_growth_imp25_mean = mean_current_growth_25_imp_jf_gross_margin - mean_current_gross_margin
    ahle_when_jm_growth_imp25_mean = mean_current_growth_25_imp_jm_gross_margin - mean_current_gross_margin
    ahle_when_nf_growth_imp25_mean = mean_current_growth_25_imp_nf_gross_margin - mean_current_gross_margin
    ahle_when_nm_growth_imp25_mean = mean_current_growth_25_imp_nm_gross_margin - mean_current_gross_margin

    ahle_when_all_growth_imp50_mean = mean_current_growth_50_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_af_growth_imp50_mean = mean_current_growth_50_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_growth_imp50_mean = mean_current_growth_50_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_jf_growth_imp50_mean = mean_current_growth_50_imp_jf_gross_margin - mean_current_gross_margin
    ahle_when_jm_growth_imp50_mean = mean_current_growth_50_imp_jm_gross_margin - mean_current_gross_margin
    ahle_when_nf_growth_imp50_mean = mean_current_growth_50_imp_nf_gross_margin - mean_current_gross_margin
    ahle_when_nm_growth_imp50_mean = mean_current_growth_50_imp_nm_gross_margin - mean_current_gross_margin

    ahle_when_all_growth_imp75_mean = mean_current_growth_75_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_af_growth_imp75_mean = mean_current_growth_75_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_growth_imp75_mean = mean_current_growth_75_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_jf_growth_imp75_mean = mean_current_growth_75_imp_jf_gross_margin - mean_current_gross_margin
    ahle_when_jm_growth_imp75_mean = mean_current_growth_75_imp_jm_gross_margin - mean_current_gross_margin
    ahle_when_nf_growth_imp75_mean = mean_current_growth_75_imp_nf_gross_margin - mean_current_gross_margin
    ahle_when_nm_growth_imp75_mean = mean_current_growth_75_imp_nm_gross_margin - mean_current_gross_margin

    ahle_when_all_growth_imp100_mean = mean_current_growth_100_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_af_growth_imp100_mean = mean_current_growth_100_imp_af_gross_margin - mean_current_gross_margin
    ahle_when_am_growth_imp100_mean = mean_current_growth_100_imp_am_gross_margin - mean_current_gross_margin
    ahle_when_jf_growth_imp100_mean = mean_current_growth_100_imp_jf_gross_margin - mean_current_gross_margin
    ahle_when_jm_growth_imp100_mean = mean_current_growth_100_imp_jm_gross_margin - mean_current_gross_margin
    ahle_when_nf_growth_imp100_mean = mean_current_growth_100_imp_nf_gross_margin - mean_current_gross_margin
    ahle_when_nm_growth_imp100_mean = mean_current_growth_100_imp_nm_gross_margin - mean_current_gross_margin
    '''
    ,inplace=True
)

# Standard deviations require summing variances and taking square root
# Must be done outside eval()
ahle_combo_withahle['ahle_total_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_gross_margin']**2 + ahle_combo_withahle['stdev_current_gross_margin']**2)

ahle_combo_withahle['ahle_dueto_mortality_stdev'] = np.sqrt(ahle_combo_withahle['stdev_all_mortality_zero_gross_margin']**2 + ahle_combo_withahle['stdev_current_gross_margin']**2)
ahle_combo_withahle['ahle_dueto_healthcost_stdev'] = np.sqrt(ahle_combo_withahle['stdev_current_health_cost']**2)
ahle_combo_withahle['ahle_dueto_productionloss_stdev'] = np.sqrt(ahle_combo_withahle['ahle_total_stdev']**2 + ahle_combo_withahle['ahle_dueto_mortality_stdev']**2 + ahle_combo_withahle['ahle_dueto_healthcost_stdev']**2)

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo_withahle['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo_withahle = pd.merge(
    left=ahle_combo_withahle
    ,right=exchg_data_tomerge
    ,on='country_name'
    ,how='left'
    )
del ahle_combo_withahle['country_name']

# Add columns in USD
mean_cols_ahle = [i for i in list(ahle_combo_withahle) if 'mean' in i and 'ahle' in i]
for MEANCOL in mean_cols_ahle:
    MEANCOL_USD = MEANCOL + '_usd'
    ahle_combo_withahle[MEANCOL_USD] = ahle_combo_withahle[MEANCOL] / ahle_combo_withahle['exchg_rate_lcuperusdol']

# For standard deviations, convert to variances then scale by the squared exchange rate
# VAR(aX) = a^2 * VAR(X).  a = 1/exchange rate.
sd_cols_ahle = [i for i in list(ahle_combo_withahle) if 'stdev' in i and 'ahle' in i]
for SDCOL in sd_cols_ahle:
    SDCOL_USD = SDCOL + '_usd'
    ahle_combo_withahle[SDCOL_USD] = np.sqrt(ahle_combo_withahle[SDCOL]**2 / ahle_combo_withahle['exchg_rate_lcuperusdol']**2)

# =============================================================================
#### Cleanup and export
# =============================================================================
datainfo(ahle_combo_withahle)
ahle_combo_withahle.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_intermediate_calcs.pkl.gz'))

# Keep only key columns and AHLE calcs
_cols_for_summary = [i for i in list(ahle_combo_withahle) if 'ahle' in i]
_keepcols = ['species' ,'production_system' ,'group'] + _cols_for_summary

# For this summary, keep only system total AHLE
_groups_for_summary = (ahle_combo_withahle['group'].str.upper() == 'OVERALL')

ahle_combo_withahle_smry = ahle_combo_withahle.loc[_groups_for_summary][_keepcols]
datainfo(ahle_combo_withahle_smry)

ahle_combo_withahle_smry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.csv') ,index=False)
ahle_combo_withahle_smry.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.pkl.gz'))

#%% Checks on calculated AHLE

ahle_combo_withahle_smry_checks = ahle_combo_withahle_smry.copy()

# Sum of individual age/sex AHLE compared to overall AHLE
ahle_combo_withahle_smry_checks.eval(
    '''
    sum_ahle_individual = ahle_when_af_ideal_mean + ahle_when_am_ideal_mean \
        + ahle_when_jf_ideal_mean + ahle_when_jm_ideal_mean \
        + ahle_when_nf_ideal_mean + ahle_when_nm_ideal_mean

    sum_ahle_individual_vs_overall = sum_ahle_individual / ahle_total_mean
    '''
    ,inplace=True
)
print('\n> Checking the sum AHLE for individual ideal scenarios against the overall')
print(ahle_combo_withahle_smry_checks[['species' ,'production_system' ,'sum_ahle_individual_vs_overall']])
