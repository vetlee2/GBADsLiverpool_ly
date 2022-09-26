#%% About

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
