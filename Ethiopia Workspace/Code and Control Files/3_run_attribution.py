#%% About
'''
This runs the R program provided by the University of Murdoch to add attribution
for AHLE.

The attribution relies on expert opinions which are recorded in CSV files.
There is a separate expert opinion file for each species or group:
    Small ruminants (sheep and goats)
    Cattle
    Poultry

There are also differences in the production systems and age classes for
each species which require differences in the code to prepare AHLE outputs
for the attribution function.

So, I will separate the AHLE data by species and process each one individually.
I will call the attribution function separately, once for each species or group,
before concatenating the results into a single file for export.
'''
#%% Setup

# =============================================================================
#### Rscript executable
# =============================================================================
# On Lotka
# r_executable = 'C:\\Program Files\\R\\R-4.2.0\\bin\\x64\\Rscript.exe'

# On Local
r_executable = 'C:\\Program Files\\R\\R-4.2.1\\bin\\x64\\Rscript.exe'

#%% Run Attribution using example inputs

# r_script = os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function.R')    # Full path to the R program you want to run
#
# # Arguments to R function, as list of strings.
# # ORDER MATTERS! SEE HOW THIS LIST IS PARSED INSIDE R SCRIPT.
# r_args = [
#     os.path.join(ETHIOPIA_CODE_FOLDER ,'Attribution function input - example AHLE.csv')                # String: full path to AHLE estimates file (csv)
#     ,os.path.join(ETHIOPIA_CODE_FOLDER ,'attribution_experts_smallruminants.csv')               # String: full path to expert opinion attribution file (csv)
#     ,os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary.csv')    # String: full path to output file (csv)
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
ahle_combo_withahle = pd.read_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry_ahle.pkl.gz'))
datainfo(ahle_combo_withahle)

# =============================================================================
#### Restructure for Attribution function
# =============================================================================
ahle_combo_forattr_means = ahle_combo_withahle.melt(
   id_vars=['species' ,'production_system' ,'agesex_scenario']
   ,value_vars=['ahle_dueto_mortality_mean' ,'ahle_dueto_healthcost_mean' ,'ahle_dueto_productionloss_mean']
   ,var_name='ahle_component'
   ,value_name='mean'
)
ahle_combo_forattr_stdev = ahle_combo_withahle.melt(
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
print(f"> Dropping {_droprows.sum() :,} rows.")
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

#%% Prep for Attribution - Small Ruminants
'''
For sheep and goats, expert attribution file uses non-sex-specific Juvenile and Neonatal groups.
'''
# =============================================================================
#### Subset data to correct species
# =============================================================================
_row_selection = (ahle_combo_forattr_1['species'].str.upper().isin(['SHEEP' ,'GOAT']))
print(f"> Selected {_row_selection.sum() :,} rows.")
ahle_combo_forattr_smallrum = ahle_combo_forattr_1.loc[_row_selection].reset_index(drop=True)

# =============================================================================
#### Create aggregate groups
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
ahle_combo_forattr_smallrum = pd.concat(
    [ahle_combo_forattr_smallrum ,ahle_combo_forattr_smallrum_aggjuv ,ahle_combo_forattr_smallrum_aggneo]
	,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
	,join='outer'        # 'outer': keep all index values from all data frames
	,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_forattr_smallrum_aggjuv ,ahle_combo_forattr_smallrum_aggneo

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
colnames = {
   "species":"Species"
   ,"production_system":"Production system"
   ,"agesex_scenario":"Age class"
   ,"ahle_component":"AHLE"
   ,"mean":"mean"
   ,"stdev":"sd"
}
ahle_combo_forattr_smallrum = ahle_combo_forattr_smallrum.rename(columns=colnames)

# Write CSV
ahle_combo_forattr_smallrum.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_smallrum.csv') ,index=False)

#%% Prep for Attribution - Cattle
'''
For cattle, expert attribution file:
    - Uses non-sex-specific groups for all ages
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
ahle_combo_forattr_cattle = pd.concat(
    [ahle_combo_forattr_cattle ,ahle_combo_forattr_cattle_aggjuv ,ahle_combo_forattr_cattle_aggneo ,ahle_combo_forattr_cattle_aggadt]
	,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
	,join='outer'        # 'outer': keep all index values from all data frames
	,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_forattr_cattle_aggjuv ,ahle_combo_forattr_cattle_aggneo ,ahle_combo_forattr_cattle_aggadt

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
colnames = {
   "species":"Species"
   ,"production_system":"Production system"
   ,"agesex_scenario":"Age class"
   ,"ahle_component":"AHLE"
   ,"mean":"mean"
   ,"stdev":"sd"
}
ahle_combo_forattr_cattle = ahle_combo_forattr_cattle.rename(columns=colnames)

# Write CSV
ahle_combo_forattr_cattle.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_forattr_cattle.csv') ,index=False)

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

#%% === Revisit ===
'''
Plan: instead of taking health cost from ahle_combo_forattr_1, take it from
ahle_combo_forattr_cattle and ahle_combo_forattr_smallrum because those are
summed to the correct level.
'''
#%% Process attribution results

# =============================================================================
#### Import and combine
# =============================================================================
attribution_summary_smallruminants = pd.read_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_smallruminants.csv'))
attribution_summary_smallruminants['species'] = 'All small ruminants'

attribution_summary_cattle = pd.read_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'attribution_summary_cattle.csv'))
attribution_summary_cattle['species'] = 'Cattle'

ahle_combo_withattr = pd.concat(
    [attribution_summary_smallruminants ,attribution_summary_cattle]
    ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
    ,join='outer'        # 'outer': keep all index values from all data frames
    ,ignore_index=True   # True: do not keep index values on concatenation axis
    )
cleancolnames(ahle_combo_withattr)
datainfo(ahle_combo_withattr)

# =============================================================================
#### Add placeholder for health cost attribution
# =============================================================================
# Get health cost AHLE rows
_row_selection = (ahle_combo_forattr_1['ahle_component'].str.upper() == 'HEALTH COST')
print(f"> Selected {_row_selection.sum() :,} rows.")
healthcost_attr = ahle_combo_forattr_1.loc[_row_selection].reset_index(drop=True).copy()







# Add variance for summing
healthcost_attr['sqrd_sd'] = healthcost_attr['sd']**2

# Sum to same level as ahle_combo_withattr
healthcost_attr = healthcost_attr.pivot_table(
   index=['production_system' ,'age_class' ,'ahle']
   ,values=['mean' ,'sqrd_sd']
   ,aggfunc='sum'
).reset_index()

# Add placeholder attribution categories
# healthcost_attr_category_list = ['Treatment' ,'Prevention' ,'Professional time' ,'Other']
healthcost_attr_category_list = ['Infectious' ,'Non-infectious' ,'External']
healthcost_attr_category_df = pd.DataFrame({'cause':healthcost_attr_category_list
                                           ,'ahle':'Health cost'}
                                          )
healthcost_attr = pd.merge(left=healthcost_attr ,right=healthcost_attr_category_df ,on='ahle' ,how='outer')

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
# diseases_ext = pd.DataFrame({
#     "cause":'External'
#     ,"disease":['Cause 1' ,'Cause 2' ,'Cause 3' ,'Cause 4' ,'Cause 5']
#     })
# diseases_inf = pd.DataFrame({
#     "cause":'Infectious'
#     ,"disease":['Pathogen 1' ,'Pathogen 2' ,'Pathogen 3' ,'Pathogen 4' ,'Pathogen 5']
#     })
# diseases_non = pd.DataFrame({
#     "cause":'Non-infectious'
#     ,"disease":['Non-inf 1' ,'Non-inf 2' ,'Non-inf 3' ,'Non-inf 4' ,'Non-inf 5']
#     })
# diseases = pd.concat(
#     [diseases_ext ,diseases_inf ,diseases_non]
#     ,axis=0
#     ,join='outer'        # 'outer': keep all index values from all data frames
#     ,ignore_index=True   # True: do not keep index values on concatenation axis
# )

# # Merge
# ahle_combo_withattr = pd.merge(
#     left=ahle_combo_withattr
#     ,right=diseases
#     ,on='cause'
#     ,how='outer'
#     )
# ahle_combo_withattr['median'] = ahle_combo_withattr['median'] / 5
# ahle_combo_withattr['mean'] = ahle_combo_withattr['mean'] / 5
# ahle_combo_withattr['sd'] = np.sqrt(ahle_combo_withattr['sd']**2 / 25)
# ahle_combo_withattr['lower95'] = ahle_combo_withattr['mean'] - (1.96 * ahle_combo_withattr['sd'])
# ahle_combo_withattr['upper95'] = ahle_combo_withattr['mean'] + (1.96 * ahle_combo_withattr['sd'])

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
rename_cols = {
    "ahle":"ahle_component"
    ,"age_class":"group"
}
ahle_combo_withattr = ahle_combo_withattr.rename(columns=rename_cols)

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
cols_first = ['production_system' ,'group' ,'age_group' ,'sex' ,'ahle_component' ,'cause']
cols_other = [i for i in list(ahle_combo_withattr) if i not in cols_first]
ahle_combo_withattr = ahle_combo_withattr.reindex(columns=cols_first + cols_other)
datainfo(ahle_combo_withattr)

# Write CSV
ahle_combo_withattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_withattr.csv') ,index=False)
# ahle_combo_withattr.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_withattr_extra.csv') ,index=False)
