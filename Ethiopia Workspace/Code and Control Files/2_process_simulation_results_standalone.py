#%% About
'''
This program combines the output files for all scenarios created by the AHLE
simulation model and adds calculations. The output is a CSV file to be used
in the dashboard.
'''
#%% Packages and functions

import os                        # Operating system functions
import inspect
import io
import time
import numpy as np
import pandas as pd
import pickle                             # To save objects to disk

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

# To print df.info() with header for readability, and optionally write data info to text file
def datainfo(
      INPUT_DF
      ,MAX_COLS=100
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
   INPUT_DF.info(max_cols=MAX_COLS)
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

# To turn column indexes into names. Will remove multi-indexing.
# Must assign the output to a dataframe e.g. df = colnames_from_index(df).
def colnames_from_index(INPUT_DF):
   cols = list(INPUT_DF)
   cols_new = []
   for item in cols:
      if type(item) == str:   # Columns that already have names will be strings. Use unchanged.
         cols_new.append(item)
      else:   # Columns that are indexed or multi-indexed will appear as tuples. Turn them into strings joined by underscores.
         cols_new.append('_'.join(str(i) for i in item))   # Convert each element of tuple to string before joining. Avoids error if an element is nan.

   # Write dataframe with new column names
   dfmod = INPUT_DF
   dfmod.columns = cols_new
   return dfmod

#%% Define folder paths

CURRENT_FOLDER = os.getcwd()
PARENT_FOLDER = os.path.dirname(CURRENT_FOLDER)
GRANDPARENT_FOLDER = os.path.dirname(PARENT_FOLDER)

# Folder for shared code with Liverpool
ETHIOPIA_CODE_FOLDER = CURRENT_FOLDER
ETHIOPIA_OUTPUT_FOLDER = os.path.join(PARENT_FOLDER ,'Program outputs')
ETHIOPIA_DATA_FOLDER = os.path.join(PARENT_FOLDER ,'Data')

DASH_DATA_FOLDER = os.path.join(GRANDPARENT_FOLDER, 'AHLE Dashboard' ,'Dash App' ,'data')

#%% Data prep

# =============================================================================
#### Prepare currency conversion data
# =============================================================================
# Read conversion data
exchg_data = pd.read_csv(os.path.join(ETHIOPIA_DATA_FOLDER ,'worldbank_inflation_exchangerate_gdp_2010_2021' ,'20475199-8fa4-4249-baec-98b6635f68e3_Data.csv'))
cleancolnames(exchg_data)
datainfo(exchg_data)

exchg_data_tomerge = exchg_data.query("country_name == 'Ethiopia'")
exchg_data_tomerge = exchg_data_tomerge.rename(columns={'official_exchange_rate__lcu_per_us_dol___period_average___pa_nus_fcrf_':'exchg_rate_lcuperusdol'})
exchg_data_tomerge['exchg_rate_lcuperusdol'] = exchg_data_tomerge['exchg_rate_lcuperusdol'].replace('..' ,np.nan).astype('float64')
exchg_data_tomerge = exchg_data_tomerge[['country_name' ,'time' ,'exchg_rate_lcuperusdol']]
datainfo(exchg_data_tomerge)

# Export
exchg_data_tomerge.to_pickle(os.path.join(ETHIOPIA_DATA_FOLDER ,'wb_exchg_data_processed.pkl.gz'))

#%% Combine scenario result files

def combine_ahle_scenarios(
        input_folder
        ,input_file_prefix      # String
        ,input_file_suffixes    # List of strings
        ,label_species          # String: add column 'species' with this label
        ,label_prodsys          # String: add column 'production_system' with this label
        ,label_year             # Numeric: add column 'year' with this value
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
   dfcombined['species'] = label_species
   dfcombined['production_system'] = label_prodsys
   dfcombined['year'] = label_year

   # Reorder columns
   cols_first = ['species' ,'production_system' ,'year']
   cols_other = [i for i in list(dfcombined) if i not in cols_first]
   dfcombined = dfcombined.reindex(columns=cols_first + cols_other)

   # Cleanup column names
   cleancolnames(dfcombined)

   return dfcombined

# =============================================================================
#### Small ruminants
# =============================================================================
'''
These scenarios have only been produced for a single year (2021).
'''
small_rum_suffixes=[
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

ahle_sheep_clm = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle SMALL RUMINANTS')
    ,input_file_prefix='ahle_CLM_S'
    ,input_file_suffixes=small_rum_suffixes
    ,label_species='Sheep'
    ,label_prodsys='Crop livestock mixed'
    ,label_year=2021
)
datainfo(ahle_sheep_clm)

ahle_sheep_past = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle SMALL RUMINANTS')
    ,input_file_prefix='ahle_Past_S'
    ,input_file_suffixes=small_rum_suffixes
    ,label_species='Sheep'
    ,label_prodsys='Pastoral'
    ,label_year=2021
)
datainfo(ahle_sheep_past)

ahle_goat_clm = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle SMALL RUMINANTS')
    ,input_file_prefix='ahle_CLM_G'
    ,input_file_suffixes=small_rum_suffixes
    ,label_species='Goat'
    ,label_prodsys='Crop livestock mixed'
    ,label_year=2021
)
datainfo(ahle_goat_clm)

ahle_goat_past = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle SMALL RUMINANTS')
    ,input_file_prefix='ahle_Past_G'
    ,input_file_suffixes=small_rum_suffixes
    ,label_species='Goat'
    ,label_prodsys='Pastoral'
    ,label_year=2021
)
datainfo(ahle_goat_past)

# Adjust column names
ahle_sheep_clm.columns = ahle_sheep_clm.columns.str.replace('_all_mortality_zero' ,'_mortality_zero')
ahle_sheep_past.columns = ahle_sheep_past.columns.str.replace('_all_mortality_zero' ,'_mortality_zero')
ahle_goat_clm.columns = ahle_goat_clm.columns.str.replace('_all_mortality_zero' ,'_mortality_zero')
ahle_goat_past.columns = ahle_goat_past.columns.str.replace('_all_mortality_zero' ,'_mortality_zero')

# =============================================================================
#### Cattle
# =============================================================================
'''
These scenarios have been run for 5 years (2017-2021), so this includes an
extra loop to import each year and append to a master cattle dataframe.
'''
cattle_suffixes = [
    'current'

    ,'ideal'
    ,'ideal_AF'
    ,'ideal_AM'
    ,'ideal_JF'
    ,'ideal_JM'
    ,'ideal_NF'
    ,'ideal_NM'
    ,'ideal_O'

    ,'mortality_zero'
    ,'mortality_zero_AF'
    ,'mortality_zero_AM'
    ,'mortality_zero_J'
    ,'mortality_zero_N'
    ,'mortality_zero_O'
]

ahle_cattle_aslist = []         # Initialize
for YEAR in range(2017 ,2022):
    # Import CLM
    ahle_cattle_clm = combine_ahle_scenarios(
        input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle CATTLE' ,f"{YEAR}")
        ,input_file_prefix='ahle_cattle_trial_CLM'
        ,input_file_suffixes=cattle_suffixes
        ,label_species='Cattle'
        ,label_prodsys='Crop livestock mixed'
        ,label_year=YEAR
    )
    datainfo(ahle_cattle_clm ,120)

	# Turn into list and append to master
    ahle_cattle_clm_aslist = ahle_cattle_clm.to_dict(orient='records')
    ahle_cattle_aslist.extend(ahle_cattle_clm_aslist)
    del ahle_cattle_clm_aslist

    # Import pastoral
    ahle_cattle_past = combine_ahle_scenarios(
        input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle CATTLE' ,f"{YEAR}")
        ,input_file_prefix='ahle_cattle_trial_past'
        ,input_file_suffixes=cattle_suffixes
        ,label_species='Cattle'
        ,label_prodsys='Pastoral'
        ,label_year=YEAR
    )
    datainfo(ahle_cattle_past ,120)

	# Turn into list and append to master
    ahle_cattle_past_aslist = ahle_cattle_past.to_dict(orient='records')
    ahle_cattle_aslist.extend(ahle_cattle_past_aslist)
    del ahle_cattle_past_aslist

    # Import periurban dairy
    ahle_cattle_peri = combine_ahle_scenarios(
        input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle CATTLE' ,f"{YEAR}")
        ,input_file_prefix='ahle_cattle_trial_periurban_dairy'
        ,input_file_suffixes=cattle_suffixes
        ,label_species='Cattle'
        ,label_prodsys='Periurban dairy'
        ,label_year=YEAR
    )
    datainfo(ahle_cattle_peri ,120)

	# Turn into list and append to master
    ahle_cattle_peri_aslist = ahle_cattle_peri.to_dict(orient='records')
    ahle_cattle_aslist.extend(ahle_cattle_peri_aslist)
    del ahle_cattle_peri_aslist

# Convert master list into data frame
ahle_cattle = pd.DataFrame.from_dict(ahle_cattle_aslist ,orient='columns')
del ahle_cattle_aslist
datainfo(ahle_cattle ,120)

# =============================================================================
#### Poultry
# =============================================================================
'''
These scenarios have only been produced for a single year (2021).
'''
poultry_suffixes = [
    'current'
    ,'ideal'
    ,'ideal_A'
    ,'ideal_J'
    ,'ideal_N'
    ,'mortality_zero'
    ,'mortality_zero_A'
    ,'mortality_zero_J'
    ,'mortality_zero_N'
]

ahle_poultry_smallholder = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle POULTRY')
    ,input_file_prefix='ahle_Smallholder_hybrid'
    ,input_file_suffixes=poultry_suffixes
    ,label_species='Poultry hybrid'
    ,label_prodsys='Small holder'
    ,label_year=2021
)
datainfo(ahle_poultry_smallholder)

ahle_poultry_villagehybrid = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle POULTRY')
    ,input_file_prefix='ahle_Village_hybrid'
    ,input_file_suffixes=poultry_suffixes
    ,label_species='Poultry hybrid'
    ,label_prodsys='Village'
    ,label_year=2021
)
datainfo(ahle_poultry_villagehybrid)

ahle_poultry_villageindig = combine_ahle_scenarios(
    input_folder=os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle POULTRY')
    ,input_file_prefix='ahle_Village_indigenous'
    ,input_file_suffixes=poultry_suffixes
    ,label_species='Poultry indigenous'
    ,label_prodsys='Village'
    ,label_year=2021
)
datainfo(ahle_poultry_villageindig)

# =============================================================================
#### Stack species and production systems
# =============================================================================
concat_list = [
    ahle_sheep_clm
    ,ahle_sheep_past
    ,ahle_goat_clm
    ,ahle_goat_past

    ,ahle_cattle

    ,ahle_poultry_smallholder
    ,ahle_poultry_villagehybrid
    ,ahle_poultry_villageindig
]
ahle_combo_cat = pd.concat(
   concat_list      # List of dataframes to concatenate
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)

# Reset dataframe with a copy due to warning about fragmented data
ahle_combo = ahle_combo_cat.copy()
del ahle_combo_cat

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
#### Add yearly placeholder rows
# =============================================================================
'''
Goal: add yearly placeholder values for any species, production system, item,
and group that does not have them.
'''
# Each numeric column gets inflated/deflated by a percentage
yearly_adjustment = 1.05    # Desired yearly change in values

# Get list of columns for which to add placeholders
vary_by_year = list(ahle_combo.select_dtypes(include='float'))

# Turn data into list
ahle_combo_plhdyear_aslist = ahle_combo.to_dict(orient='records')

base_year = 2021
create_years = list(range(2017 ,2022))
for YEAR in create_years:
    # Create dataset for this year
    single_year_df = ahle_combo.copy()
    single_year_df['year'] = YEAR

    # Adjust numeric columns
    adj_factor = yearly_adjustment**(YEAR - base_year)
    for COL in vary_by_year:
        single_year_df[COL] = single_year_df[COL] * adj_factor

    # Turn data into list and append
    single_year_df_aslist = single_year_df.to_dict(orient='records')
    ahle_combo_plhdyear_aslist.extend(single_year_df_aslist)

# Convert list of dictionaries into data frame
ahle_combo_plhdyear = pd.DataFrame.from_dict(ahle_combo_plhdyear_aslist ,orient='columns')
del ahle_combo_plhdyear_aslist ,single_year_df ,single_year_df_aslist

# Remove duplicate values, keeping the first (the first is the actual value for that year if it exists)
ahle_combo_plhdyear = ahle_combo_plhdyear.drop_duplicates(
    subset=['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex' ,'year']
    ,keep='first'
)
datainfo(ahle_combo_plhdyear)

ahle_combo = ahle_combo_plhdyear

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
    gmchange_dueto_mortality = mean_mortality_zero - mean_current
    gmchange_dueto_production = gmchange_ideal_overall - gmchange_dueto_mortality
    gmchange_dueto_mortality_prpn = gmchange_dueto_mortality / gmchange_ideal_overall
    '''
    ,inplace=True
)
print('\n> Checking the change in Gross Margin for ideal overall vs. individual ideal scenarios')
print(check_grossmargin_overall[['species' ,'production_system' ,'year' ,'gmchange_ideal_check']])

print('\n> Checking mortality as proportion of total AHLE')
print(check_grossmargin_overall[['species' ,'production_system' ,'year' ,'gmchange_dueto_mortality_prpn']])

# =============================================================================
#### Change in AHLE when adding health cost to individual sum
# =============================================================================
mean_cols = [i for i in list(check_ahle_combo) if 'mean' in i]
_items_gm_hc = (check_ahle_combo['item'].str.upper() == 'GROSS MARGIN') \
    | (check_ahle_combo['item'].str.upper() == 'HEALTH COST')

# Pivot items into columns
check_grossmargin_withhealth = check_ahle_combo.loc[_group_overall].loc[_items_gm_hc].pivot(
    index=['species' ,'production_system' ,'group' ,'age_group' ,'sex' ,'year']
    ,columns='item'
    ,values=mean_cols
).reset_index()
check_grossmargin_withhealth = colnames_from_index(check_grossmargin_withhealth)   # Change multi-index to column names
cleancolnames(check_grossmargin_withhealth)

# Remove underscores added when collapsing column index
check_grossmargin_withhealth = check_grossmargin_withhealth.rename(
    columns={
        'species_':'species'
        ,'production_system_':'production_system'
        ,'group_':'group'
        ,'age_group_':'age_group'
        ,'sex_':'sex'
        ,'year_':'year'
    }
)

check_grossmargin_withhealth.eval(
    #### Change in Gross Margin overall vs. individual ideal scenarios
    '''
    gmchange_ideal_overall = mean_ideal_gross_margin - mean_current_gross_margin

    gmchange_ideal_af = mean_ideal_af_gross_margin - mean_current_gross_margin
    gmchange_ideal_am = mean_ideal_am_gross_margin - mean_current_gross_margin
    gmchange_ideal_jf = mean_ideal_jf_gross_margin - mean_current_gross_margin
    gmchange_ideal_jm = mean_ideal_jm_gross_margin - mean_current_gross_margin
    gmchange_ideal_nf = mean_ideal_nf_gross_margin - mean_current_gross_margin
    gmchange_ideal_nm = mean_ideal_nm_gross_margin - mean_current_gross_margin

    gmchange_ideal_sumind = gmchange_ideal_af + gmchange_ideal_am \
        + gmchange_ideal_jf + gmchange_ideal_jm \
            + gmchange_ideal_nf + gmchange_ideal_nm

    gmchange_ideal_sumind_withhealth = gmchange_ideal_sumind + mean_current_health_cost

    gmchange_ideal_check_withhealth = gmchange_ideal_sumind_withhealth / gmchange_ideal_overall
    '''
    ,inplace=True
)
print('\n> Checking the change in Gross Margin for ideal overall vs. individual ideal scenarios')
print('> With health cost added to sum of individual ideal scenarios')
print(check_grossmargin_withhealth[['species' ,'production_system' ,'year' ,'gmchange_ideal_check_withhealth']])

# =============================================================================
#### Sum of agesex groups compared to system total for each item
# =============================================================================
# Sum individual agesex groups for each item
check_agesex_sums = pd.DataFrame(check_ahle_combo.loc[~ _sex_combined]\
    .groupby(['species' ,'production_system' ,'year' ,'item'] ,observed=True)['mean_current'].sum())
check_agesex_sums.columns = ['mean_current_sumagesex']

# Merge group total for each item
check_agesex_sums = pd.merge(
    left=check_agesex_sums
    ,right=check_ahle_combo.loc[_group_overall ,['species' ,'production_system' ,'year' ,'item' ,'mean_current']]
    ,on=['species' ,'production_system' ,'year' ,'item']
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
print('\nMaximum ratio \n-------------')
print(check_agesex_sums.groupby(['species' ,'production_system' ,'year'])['check_ratio'].max())
print('\nMinimum ratio \n-------------')
print(check_agesex_sums.groupby(['species' ,'production_system' ,'year'])['check_ratio'].min())

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
# item_placeholder = ahle_combo_indiv[['species' ,'production_system' ,'group' ,'age_group' ,'sex' ,'year']].drop_duplicates()
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
keepcols = ['species' ,'production_system' ,'item' ,'group' ,'age_group' ,'sex' ,'year'] \
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
    index=['species' ,'production_system' ,'item' ,'year']
    ,values=mean_cols + var_cols
    ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
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
        index=['species' ,'production_system' ,'item' ,'age_group' ,'year']
        ,values=mean_cols + var_cols
        ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
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
        index=['species' ,'production_system' ,'item' ,'sex' ,'year']
        ,values=mean_cols + var_cols
        ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
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
   subset=['species' ,'production_system' ,'item' ,'group' ,'year']       # List (opt): only consider these columns when identifying duplicates. If None, consider all columns.
   ,keep='first'
)

# -----------------------------------------------------------------------------
# Create overall production system for each species and group
# -----------------------------------------------------------------------------
ahle_combo_withagg_sumprod = ahle_combo_withagg.pivot_table(
   index=['species' ,'item' ,'group' ,'age_group' ,'sex' ,'year']
   ,values=mean_cols + var_cols
   ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
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
# Create combined species
# -----------------------------------------------------------------------------
# All Small Ruminants
ahle_combo_withagg_sumspec = ahle_combo_withagg.query("species.str.upper().isin(['SHEEP' ,'GOAT'])").pivot_table(
   index=['production_system' ,'item' ,'group' ,'age_group' ,'sex' ,'year']
   ,values=mean_cols + var_cols
   ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
).reset_index()
ahle_combo_withagg_sumspec['species'] = 'All Small Ruminants'

# All poultry
ahle_combo_withagg_sumspec2 = ahle_combo_withagg.query("species.str.contains('poultry' ,case=False ,na=False)").pivot_table(
   index=['production_system' ,'item' ,'group' ,'age_group' ,'sex' ,'year']
   ,values=mean_cols + var_cols
   ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
).reset_index()
ahle_combo_withagg_sumspec2['species'] = 'All Poultry'

ahle_combo_withagg = pd.concat(
   [ahle_combo_withagg ,ahle_combo_withagg_sumspec ,ahle_combo_withagg_sumspec2]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_withagg_sumspec ,ahle_combo_withagg_sumspec2

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
    ,left_on=['country_name' ,'year']
    ,right_on=['country_name' ,'time']
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
    ,'year'

    # In Birr
    ,'mean_current'
    ,'stdev_current'
    ,'mean_ideal'
    ,'stdev_ideal'

    ,'mean_all_mort_25_imp'
    ,'mean_all_mort_50_imp'
    ,'mean_all_mort_75_imp'
    ,'mean_mortality_zero'
    ,'stdev_mortality_zero'

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
    ,'mean_mortality_zero_usd'
    ,'stdev_mortality_zero_usd'

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
datainfo(ahle_combo_withagg_smry)

ahle_combo_withagg_smry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.csv') ,index=False)
ahle_combo_withagg_smry.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary.pkl.gz'))

# Output for Dash
ahle_combo_withagg_smry.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_summary.csv') ,index=False)

#%% Calculate AHLE

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
    index=['species' ,'production_system' ,'group' ,'age_group' ,'sex' ,'year']
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
        ,'year_':'year'
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
    ahle_dueto_mortality_mean = mean_mortality_zero_gross_margin - mean_current_gross_margin
    ahle_dueto_healthcost_mean = mean_current_health_cost
    ahle_dueto_productionloss_mean = ahle_total_mean - ahle_dueto_mortality_mean - ahle_dueto_healthcost_mean

    ahle_when_af_repro_imp25_mean = mean_current_repro_25_imp_gross_margin - mean_current_gross_margin
    ahle_when_af_repro_imp50_mean = mean_current_repro_50_imp_gross_margin - mean_current_gross_margin
    ahle_when_af_repro_imp75_mean = mean_current_repro_75_imp_gross_margin - mean_current_gross_margin
    ahle_when_af_repro_imp100_mean = mean_current_repro_100_imp_gross_margin - mean_current_gross_margin

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
    # These apply to poultry
    '''
    ahle_when_a_ideal_mean = mean_ideal_a_gross_margin - mean_current_gross_margin
    ahle_when_j_ideal_mean = mean_ideal_j_gross_margin - mean_current_gross_margin
    ahle_when_n_ideal_mean = mean_ideal_n_gross_margin - mean_current_gross_margin

    ahle_when_a_mort_imp100_mean = mean_mortality_zero_a_gross_margin - mean_current_gross_margin
    ahle_when_j_mort_imp100_mean = mean_mortality_zero_j_gross_margin - mean_current_gross_margin
    ahle_when_n_mort_imp100_mean = mean_mortality_zero_n_gross_margin - mean_current_gross_margin
    '''
    ,inplace=True
)

# Standard deviations require summing variances and taking square root
# Must be done outside eval()
ahle_combo_withahle['ahle_total_stdev'] = np.sqrt(ahle_combo_withahle['stdev_ideal_gross_margin']**2 + ahle_combo_withahle['stdev_current_gross_margin']**2)

ahle_combo_withahle['ahle_dueto_mortality_stdev'] = np.sqrt(ahle_combo_withahle['stdev_mortality_zero_gross_margin']**2 + ahle_combo_withahle['stdev_current_gross_margin']**2)
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
    ,left_on=['country_name' ,'year']
    ,right_on=['country_name' ,'time']
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
# ahle_combo_withahle.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_intermediate_calcs.pkl.gz'))

# Keep only key columns and AHLE calcs
_ahle_cols = [i for i in list(ahle_combo_withahle) if 'ahle' in i]
_cols_for_summary = ['species' ,'production_system' ,'group' ,'year'] + _ahle_cols

# For this summary, keep only system total AHLE
_groups_for_summary = (ahle_combo_withahle['group'].str.upper() == 'OVERALL')

ahle_combo_withahle_smry = ahle_combo_withahle.loc[_groups_for_summary][_cols_for_summary].reset_index(drop=True)
datainfo(ahle_combo_withahle_smry)

ahle_combo_withahle_smry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.csv') ,index=False)
ahle_combo_withahle_smry.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_summary2.pkl.gz'))

# Output for Dash
ahle_combo_withahle_smry.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_summary2.csv') ,index=False)

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
print(ahle_combo_withahle_smry_checks[['species' ,'production_system' ,'year' ,'sum_ahle_individual_vs_overall']])

#%% Create alternative scenario summary
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
        etc.
'''
# =============================================================================
#### Create a row for each age*sex scenario and the overall scenarios
# =============================================================================
scenario_basetable = pd.DataFrame({
   'agesex_scenario':[
      'Adult Female'
      ,'Adult Male'
      ,'Adult Combined'     # Only applied to poultry

      ,'Juvenile Female'
      ,'Juvenile Male'
      ,'Juvenile Combined'     # Only applied to poultry

      ,'Neonatal Female'
      ,'Neonatal Male'
      ,'Neonatal Combined'     # Only applied to poultry

      ,'Oxen'       # Only applies to Cattle

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

# Drop rows for age*sex scenarios that don't apply to species
_droprows = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'OXEN') \
    & (ahle_combo_scensmry['species'].str.upper() != 'CATTLE')
print(f"> Dropping {_droprows.sum() :,} rows where agesex_scenario does not apply to species.")
ahle_combo_scensmry = ahle_combo_scensmry.drop(ahle_combo_scensmry.loc[_droprows].index).reset_index(drop=True)

# =============================================================================
#### Assign results from correct scenario column to each row
# =============================================================================
'''
Note that current scenario column applies to every row.
Note also that columns are already populated for the Overall group.
'''
# Create a function to fill values of one column with another for a subset of rows
def fill_column_where(
        DATAFRAME           # Dataframe
        ,LOC                # Dataframe mask e.g. _loc = (df['col'] == 'Value')
        ,COLUMN_TOFILL      # String
        ,COLUMN_TOUSE       # String
        ,DROP=False         # True: drop COLUMN_TOUSE
    ):
    dfmod = DATAFRAME.copy()
    print(f"> Processing {dfmod.loc[LOC].shape[0]} rows.")
    try:
        dfmod[COLUMN_TOUSE]     # If column to use exists
        print(f">> Filling {COLUMN_TOFILL} with {COLUMN_TOUSE}.")
        dfmod.loc[LOC ,COLUMN_TOFILL] = dfmod.loc[LOC ,COLUMN_TOUSE]
        if DROP:
            dfmod = dfmod.drop(columns=COLUMN_TOUSE)
    except:
        print(f">> {COLUMN_TOUSE} not found. Filling {COLUMN_TOFILL} with nan.")
        dfmod.loc[LOC ,COLUMN_TOFILL] = np.nan
    return dfmod

# -----------------------------------------------------------------------------
# Adult Female
# -----------------------------------------------------------------------------
_scen_af = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'ADULT FEMALE')
print(f"> Selected {_scen_af.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_ideal' ,'mean_ideal_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_ideal' ,'stdev_ideal_af' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_mortality_zero' ,'mean_mortality_zero_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_mortality_zero' ,'stdev_mortality_zero_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_af' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_af' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_af ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_af' ,DROP=True)

# Reproduction scenario already applies to adult females
# 'mean_current_repro_25_imp'
# 'mean_current_repro_50_imp'
# 'mean_current_repro_75_imp'
# 'mean_current_repro_100_imp'

# -----------------------------------------------------------------------------
# Adult Male
# -----------------------------------------------------------------------------
_scen_am = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'ADULT MALE')
print(f"> Selected {_scen_am.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_ideal' ,'mean_ideal_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_ideal' ,'stdev_ideal_am' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_mortality_zero' ,'mean_mortality_zero_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_mortality_zero' ,'stdev_mortality_zero_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_am' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_am' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_am ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_am' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_am ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_am ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Adult combined - currently poultry only
# -----------------------------------------------------------------------------
_scen_ac = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'ADULT COMBINED')
print(f"> Selected {_scen_ac.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_ideal' ,'mean_ideal_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_ideal' ,'stdev_ideal_a' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_mortality_zero' ,'mean_mortality_zero_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_mortality_zero' ,'stdev_mortality_zero_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_a' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_a' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ac ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_a' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_ac ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ac ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ac ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ac ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_ac ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ac ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ac ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ac ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Juvenile Female
# -----------------------------------------------------------------------------
_scen_jf = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'JUVENILE FEMALE')
print(f"> Selected {_scen_jf.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_ideal' ,'mean_ideal_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_ideal' ,'stdev_ideal_jf' ,DROP=True)

# For juveniles, mortality scenarios are not sex specific
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_mortality_zero' ,'mean_mortality_zero_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_mortality_zero' ,'stdev_mortality_zero_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_j')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_mortality_zero' ,'mean_mortality_zero_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_mortality_zero' ,'stdev_mortality_zero_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_jf' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_jf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jf ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_jf' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_jf ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jf ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Juvenile Male
# -----------------------------------------------------------------------------
_scen_jm = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'JUVENILE MALE')
print(f"> Selected {_scen_jm.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_ideal' ,'mean_ideal_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_ideal' ,'stdev_ideal_jm' ,DROP=True)

# For juveniles, mortality scenarios are not sex specific
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_mortality_zero' ,'mean_mortality_zero_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_mortality_zero' ,'stdev_mortality_zero_j')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_j' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_j' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_j' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_j' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_j' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_j' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_mortality_zero' ,'mean_mortality_zero_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_mortality_zero' ,'stdev_mortality_zero_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_jm' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_jm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jm ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_jm' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_jm ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jm ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Juvenile combined - currently poultry only
# -----------------------------------------------------------------------------
_scen_jc = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'JUVENILE COMBINED')
print(f"> Selected {_scen_jc.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_ideal' ,'mean_ideal_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_ideal' ,'stdev_ideal_j' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_mortality_zero' ,'mean_mortality_zero_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_mortality_zero' ,'stdev_mortality_zero_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_j' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_j' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_jc ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_j' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_jc ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jc ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jc ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jc ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_jc ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jc ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jc ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_jc ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Neonatal Female
# -----------------------------------------------------------------------------
_scen_nf = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'NEONATAL FEMALE')
print(f"> Selected {_scen_nf.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_ideal' ,'mean_ideal_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_ideal' ,'stdev_ideal_nf' ,DROP=True)

# For neonates, mortality scenarios are not sex specific
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_mortality_zero' ,'mean_mortality_zero_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_mortality_zero' ,'stdev_mortality_zero_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_n')

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_mortality_zero' ,'mean_mortality_zero_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_mortality_zero' ,'stdev_mortality_zero_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_nf' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_nf' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nf ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_nf' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_nf ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nf ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Neonatal Male
# -----------------------------------------------------------------------------
_scen_nm = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'NEONATAL MALE')
print(f"> Selected {_scen_nm.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_ideal' ,'mean_ideal_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_ideal' ,'stdev_ideal_nm' ,DROP=True)

# For neonates, mortality scenarios are not sex specific
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_mortality_zero' ,'mean_mortality_zero_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_mortality_zero' ,'stdev_mortality_zero_n')
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_n' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_n' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_n' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_n' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_n' ,DROP=True)
# ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_n' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_mortality_zero' ,'mean_mortality_zero_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_mortality_zero' ,'stdev_mortality_zero_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_nm' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_nm' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nm ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_nm' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_nm ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nm ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Neonatal combined - currently poultry only
# -----------------------------------------------------------------------------
_scen_nc = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'NEONATAL COMBINED')
print(f"> Selected {_scen_nc.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_ideal' ,'mean_ideal_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_ideal' ,'stdev_ideal_n' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_mortality_zero' ,'mean_mortality_zero_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_mortality_zero' ,'stdev_mortality_zero_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_n' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_n' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_nc ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_n' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_nc ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nc ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nc ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nc ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_nc ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nc ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nc ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_nc ,'stdev_current_repro_100_imp'] = np.nan

# -----------------------------------------------------------------------------
# Oxen
# -----------------------------------------------------------------------------
_scen_ox = (ahle_combo_scensmry['agesex_scenario'].str.upper() == 'OXEN')
print(f"> Selected {_scen_ox.sum(): ,} rows.")

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_ideal' ,'mean_ideal_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_ideal' ,'stdev_ideal_o' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_mortality_zero' ,'mean_mortality_zero_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_mortality_zero' ,'stdev_mortality_zero_o' ,DROP=True)

# Mortality and growth improvement scenarios have not been run for cattle
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_all_mort_25_imp' ,'mean_mort_25_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_all_mort_25_imp' ,'stdev_mort_25_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_all_mort_50_imp' ,'mean_mort_50_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_all_mort_50_imp' ,'stdev_mort_50_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_all_mort_75_imp' ,'mean_mort_75_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_all_mort_75_imp' ,'stdev_mort_75_imp_o' ,DROP=True)

ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_current_growth_25_imp_all' ,'mean_current_growth_25_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_current_growth_25_imp_all' ,'stdev_current_growth_25_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_current_growth_50_imp_all' ,'mean_current_growth_50_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_current_growth_50_imp_all' ,'stdev_current_growth_50_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_current_growth_75_imp_all' ,'mean_current_growth_75_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_current_growth_75_imp_all' ,'stdev_current_growth_75_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'mean_current_growth_100_imp_all' ,'mean_current_growth_100_imp_o' ,DROP=True)
ahle_combo_scensmry = fill_column_where(ahle_combo_scensmry ,_scen_ox ,'stdev_current_growth_100_imp_all' ,'stdev_current_growth_100_imp_o' ,DROP=True)

# Reproduction scenario only applies to adult females
ahle_combo_scensmry.loc[_scen_ox ,'mean_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ox ,'mean_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ox ,'mean_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ox ,'mean_current_repro_100_imp'] = np.nan

ahle_combo_scensmry.loc[_scen_ox ,'stdev_current_repro_25_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ox ,'stdev_current_repro_50_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ox ,'stdev_current_repro_75_imp'] = np.nan
ahle_combo_scensmry.loc[_scen_ox ,'stdev_current_repro_100_imp'] = np.nan

# =============================================================================
#### Create aggregate Species and Production System
# =============================================================================
'''
Note: while item values do not sum across age/sex scenarios, they do sum across
species and production systems.
'''
mean_cols = [i for i in list(ahle_combo_scensmry) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo_scensmry) if 'stdev' in i]
var_cols = ['sqrd_' + COLNAME for COLNAME in sd_cols]
for i ,VARCOL in enumerate(var_cols):
   SDCOL = sd_cols[i]
   ahle_combo_scensmry[VARCOL] = ahle_combo_scensmry[SDCOL]**2

# -----------------------------------------------------------------------------
# Create overall production system
# -----------------------------------------------------------------------------
ahle_combo_scensmry_sumprod = ahle_combo_scensmry.pivot_table(
   index=['species' ,'item' ,'agesex_scenario' ,'year']
   ,values=mean_cols + var_cols
   ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
).reset_index()
ahle_combo_scensmry_sumprod['production_system'] = 'Overall'

ahle_combo_scensmry = pd.concat(
   [ahle_combo_scensmry ,ahle_combo_scensmry_sumprod]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_scensmry_sumprod

# -----------------------------------------------------------------------------
# Create overall species
# -----------------------------------------------------------------------------
# "All Small Ruminants" for Sheep and Goats
ahle_combo_scensmry_sumspec1 = ahle_combo_scensmry.query("species.str.upper().isin(['SHEEP' ,'GOAT'])").pivot_table(
   index=['production_system' ,'item' ,'agesex_scenario' ,'year']
   ,values=mean_cols + var_cols
   ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
).reset_index()
ahle_combo_scensmry_sumspec1['species'] = 'All Small Ruminants'

# "All poultry"
ahle_combo_scensmry_sumspec2 = ahle_combo_scensmry.query("species.str.contains('poultry' ,case=False ,na=False)").pivot_table(
   index=['production_system' ,'item' ,'agesex_scenario' ,'year']
   ,values=mean_cols + var_cols
   ,aggfunc=lambda x: x.mean() * x.count()  # Hack: sum is equal to zero if all values are missing. This will cause all missings to produce missing.
).reset_index()
ahle_combo_scensmry_sumspec2['species'] = 'All Poultry'

# Concatenate
ahle_combo_scensmry = pd.concat(
   [ahle_combo_scensmry ,ahle_combo_scensmry_sumspec1 ,ahle_combo_scensmry_sumspec2]
   ,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
   ,join='outer'        # 'outer': keep all index values from all data frames
   ,ignore_index=True   # True: do not keep index values on concatenation axis
)
del ahle_combo_scensmry_sumspec1 ,ahle_combo_scensmry_sumspec2

# -----------------------------------------------------------------------------
# Calculate standard deviations
# -----------------------------------------------------------------------------
for i ,VARCOL in enumerate(var_cols):
   SDCOL = sd_cols[i]
   ahle_combo_scensmry[SDCOL] = np.sqrt(ahle_combo_scensmry[VARCOL])
   del ahle_combo_scensmry[VARCOL]

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo_scensmry['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo_scensmry = pd.merge(
    left=ahle_combo_scensmry
    ,right=exchg_data_tomerge
    ,left_on=['country_name' ,'year']
    ,right_on=['country_name' ,'time']
    ,how='left'
    )
del ahle_combo_scensmry['country_name']

# Add columns in USD for appropriate items
currency_items_containing = ['cost' ,'value' ,'margin' ,'expenditure']
currency_items = []
for STR in currency_items_containing:
   currency_items = currency_items + [item for item in ahle_combo_scensmry['item'].unique() if STR.upper() in item.upper()]

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

datainfo(ahle_combo_scensmry)

ahle_combo_scensmry.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry.csv') ,index=False)
ahle_combo_scensmry.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry.pkl.gz'))

# Output for Dash
ahle_combo_scensmry.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_scensmry.csv') ,index=False)

#%% Calculate alternative AHLE

# =============================================================================
#### Restructure
# =============================================================================
# For AHLE calcs, we want each item in a column
# Only need item 'gross margin'
# Need means and standard deviations for later calculations
mean_cols = [i for i in list(ahle_combo_scensmry) if 'mean' in i]
sd_cols = [i for i in list(ahle_combo_scensmry) if 'stdev' in i]

_items_for_ahle = (ahle_combo_scensmry['item'].str.upper() == 'GROSS MARGIN')

ahle_combo_scensmry_p = ahle_combo_scensmry.loc[_items_for_ahle].pivot(
    index=['species' ,'production_system' ,'agesex_scenario' ,'year']
    ,columns='item'
    ,values=mean_cols + sd_cols
).reset_index()
ahle_combo_scensmry_p = colnames_from_index(ahle_combo_scensmry_p)   # Change multi-index to column names
cleancolnames(ahle_combo_scensmry_p)

# Remove underscores added when collapsing column index
ahle_combo_scensmry_p = ahle_combo_scensmry_p.rename(
    columns={
        'species_':'species'
        ,'production_system_':'production_system'
        ,'agesex_scenario_':'agesex_scenario'
        ,'year_':'year'
    }
)

datainfo(ahle_combo_scensmry_p)

# =============================================================================
#### Add Health Cost
# =============================================================================
'''
The health cost component of AHLE is not estimated by running a scenario; it is
simply the current health cost expenditure. For a given agesex group, it is the
current health expenditure on that group. To get this, we need to go back to the
group-specific item values in ahle_combo.
'''
# Get health cost for each group
_healthcost_item = (ahle_combo_withagg['item'].str.upper() == 'HEALTH COST')
_healthcost_cols = ['species' ,'production_system' ,'group' ,'year' ,'mean_current' ,'stdev_current']
current_healthcosts_bygroup = ahle_combo_withagg.loc[_healthcost_item][_healthcost_cols]

# Rename
current_healthcosts_bygroup = current_healthcosts_bygroup.rename(
    columns={
        'mean_current':'mean_current_health_cost'
        ,'stdev_current':'stdev_current_health_cost'
        ,'group':'agesex_scenario'
        }
    )

# Merge
ahle_combo_scensmry_p = pd.merge(
    left=ahle_combo_scensmry_p
    ,right=current_healthcosts_bygroup
    ,on=['species' ,'production_system' ,'agesex_scenario' ,'year']
    ,how='left'
    )
datainfo(ahle_combo_scensmry_p)

# =============================================================================
#### Calculate AHLE
# =============================================================================
'''
Calculating mean and standard deviation for each AHLE component.
Relying on the following properties of sums of random variables:
    mean(aX + bY) = a*mean(X) + b*mean(Y), regardless of correlation
    var(aX + bY) = a^2*var(X) + b^2*var(Y), assuming X and Y are uncorrelated
'''
ahle_combo_scensmry_withahle = ahle_combo_scensmry_p.copy()

ahle_combo_scensmry_withahle.eval(
    # Scenarios that change all age/sex groups
    '''
    ahle_total_mean = mean_ideal_gross_margin - mean_current_gross_margin

    ahle_dueto_mortality_mean = mean_mortality_zero_gross_margin - mean_current_gross_margin
    ahle_dueto_healthcost_mean = mean_current_health_cost
    ahle_dueto_productionloss_mean = ahle_total_mean - ahle_dueto_mortality_mean - ahle_dueto_healthcost_mean

    ahle_when_mort_imp25_mean = mean_all_mort_25_imp_gross_margin - mean_current_gross_margin
    ahle_when_mort_imp50_mean = mean_all_mort_50_imp_gross_margin - mean_current_gross_margin
    ahle_when_mort_imp75_mean = mean_all_mort_75_imp_gross_margin - mean_current_gross_margin
    ahle_when_mort_imp100_mean = mean_mortality_zero_gross_margin - mean_current_gross_margin

    ahle_when_repro_imp25_mean = mean_current_repro_25_imp_gross_margin - mean_current_gross_margin
    ahle_when_repro_imp50_mean = mean_current_repro_50_imp_gross_margin - mean_current_gross_margin
    ahle_when_repro_imp75_mean = mean_current_repro_75_imp_gross_margin - mean_current_gross_margin
    ahle_when_repro_imp100_mean = mean_current_repro_100_imp_gross_margin - mean_current_gross_margin

    ahle_when_all_growth_imp25_mean = mean_current_growth_25_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_all_growth_imp50_mean = mean_current_growth_50_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_all_growth_imp75_mean = mean_current_growth_75_imp_all_gross_margin - mean_current_gross_margin
    ahle_when_all_growth_imp100_mean = mean_current_growth_100_imp_all_gross_margin - mean_current_gross_margin
    '''
    ,inplace=True
)

# Standard deviations require summing variances and taking square root
# Must be done outside eval()
ahle_combo_scensmry_withahle['ahle_total_stdev'] = np.sqrt(ahle_combo_scensmry_withahle['stdev_ideal_gross_margin']**2 + ahle_combo_scensmry_withahle['stdev_current_gross_margin']**2)

ahle_combo_scensmry_withahle['ahle_dueto_mortality_stdev'] = np.sqrt(ahle_combo_scensmry_withahle['stdev_mortality_zero_gross_margin']**2 + ahle_combo_scensmry_withahle['stdev_current_gross_margin']**2)
ahle_combo_scensmry_withahle['ahle_dueto_healthcost_stdev'] = np.sqrt(ahle_combo_scensmry_withahle['stdev_current_health_cost']**2)
ahle_combo_scensmry_withahle['ahle_dueto_productionloss_stdev'] = np.sqrt(ahle_combo_scensmry_withahle['ahle_total_stdev']**2 + ahle_combo_scensmry_withahle['ahle_dueto_mortality_stdev']**2 + ahle_combo_scensmry_withahle['ahle_dueto_healthcost_stdev']**2)

# =============================================================================
#### Add currency conversion
# =============================================================================
# Merge exchange rates onto data
ahle_combo_scensmry_withahle['country_name'] = 'Ethiopia'     # Add country for joining
ahle_combo_scensmry_withahle = pd.merge(
    left=ahle_combo_scensmry_withahle
    ,right=exchg_data_tomerge
    ,left_on=['country_name' ,'year']
    ,right_on=['country_name' ,'time']
    ,how='left'
    )
del ahle_combo_scensmry_withahle['country_name']

# Add columns in USD
mean_cols_ahle = [i for i in list(ahle_combo_scensmry_withahle) if 'mean' in i and 'ahle' in i]
for MEANCOL in mean_cols_ahle:
    MEANCOL_USD = MEANCOL + '_usd'
    ahle_combo_scensmry_withahle[MEANCOL_USD] = ahle_combo_scensmry_withahle[MEANCOL] / ahle_combo_scensmry_withahle['exchg_rate_lcuperusdol']

# For standard deviations, convert to variances then scale by the squared exchange rate
# VAR(aX) = a^2 * VAR(X).  a = 1/exchange rate.
sd_cols_ahle = [i for i in list(ahle_combo_scensmry_withahle) if 'stdev' in i and 'ahle' in i]
for SDCOL in sd_cols_ahle:
    SDCOL_USD = SDCOL + '_usd'
    ahle_combo_scensmry_withahle[SDCOL_USD] = np.sqrt(ahle_combo_scensmry_withahle[SDCOL]**2 / ahle_combo_scensmry_withahle['exchg_rate_lcuperusdol']**2)

# =============================================================================
#### Cleanup and export
# =============================================================================
datainfo(ahle_combo_scensmry_withahle)

# Keep only key columns and AHLE calcs
_cols_for_summary = [i for i in list(ahle_combo_scensmry_withahle) if 'ahle' in i]
_keepcols = ['species' ,'production_system' ,'agesex_scenario'] + _cols_for_summary
ahle_combo_scensmry_withahle_sub = ahle_combo_scensmry_withahle[_keepcols]

datainfo(ahle_combo_scensmry_withahle_sub)

ahle_combo_scensmry_withahle_sub.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry_ahle.csv') ,index=False)
ahle_combo_scensmry_withahle_sub.to_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry_ahle.pkl.gz'))

# Output for Dash
ahle_combo_scensmry_withahle_sub.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_scensmry_ahle.csv') ,index=False)
