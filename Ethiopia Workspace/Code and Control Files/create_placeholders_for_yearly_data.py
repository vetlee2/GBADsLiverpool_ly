#%% About
'''
This program adds placeholders for yearly data in the Ethiopia output files,
to be used for developing longitudinal displays in the dashboard.
'''
#%% Packages

import seaborn as sns                     # Statistical graphics

#%% Do it

# =============================================================================
#### ahle_all_scensmry
# =============================================================================
# Read data
ahle_combo_scensmry = pd.read_pickle(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry.pkl.gz'))
ahle_combo_scensmry_yearly = ahle_combo_scensmry.copy()

# Add year column for base year
base_year = 2021
ahle_combo_scensmry_yearly['year'] = base_year

datainfo(ahle_combo_scensmry_yearly)

# Create rows for other years
# Each numeric column gets inflated/deflated by a percentage
yearly_adjustment = 1.05    # Desired yearly change in values

# Get list of columns for which to add placeholders
vary_by_year = list(ahle_combo_scensmry_yearly.select_dtypes(include='float'))

# Turn data into list
ahle_combo_scensmry_yearly_aslist = ahle_combo_scensmry_yearly.to_dict(orient='records')

create_years = list(range(2017 ,2021))
for YEAR in create_years:
    # Create dataset for this year
    single_year_df = ahle_combo_scensmry_yearly.copy()
    single_year_df['year'] = YEAR

    # Adjust numeric columns
    adj_factor = yearly_adjustment**(YEAR - base_year)
    for COL in vary_by_year:
        single_year_df[COL] = single_year_df[COL] * adj_factor

    # Turn data into list and append
    single_year_df_aslist = single_year_df.to_dict(orient='records')
    ahle_combo_scensmry_yearly_aslist.extend(single_year_df_aslist)

# Convert list of dictionaries into data frame
ahle_combo_scensmry_yearly = pd.DataFrame.from_dict(ahle_combo_scensmry_yearly_aslist ,orient='columns')
del ahle_combo_scensmry_yearly_aslist ,single_year_df ,single_year_df_aslist

datainfo(ahle_combo_scensmry_yearly)

# Export
cols_first = [
    'agesex_scenario'
    ,'species'
    ,'production_system'
    ,'item'
    ,'year'
    ,'mean_current'
    ,'stdev_current'
    ,'mean_ideal'
    ,'stdev_ideal'
    ]
cols_other = [i for i in list(ahle_combo_scensmry_yearly) if i not in cols_first]
ahle_combo_scensmry_yearly = ahle_combo_scensmry_yearly.reindex(columns=cols_first + cols_other)

ahle_combo_scensmry_yearly.to_csv(os.path.join(ETHIOPIA_OUTPUT_FOLDER ,'ahle_all_scensmry_yearlyfake.csv'))
ahle_combo_scensmry_yearly.to_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_scensmry_yearlyfake.csv'))

# Check
ahle_combo_scensmry_yearly['year'].value_counts()

_plot = (ahle_combo_scensmry_yearly['agesex_scenario'] == ahle_combo_scensmry_yearly['agesex_scenario'].unique()[0]) \
    & (ahle_combo_scensmry_yearly['species'] == ahle_combo_scensmry_yearly['species'].unique()[0]) \
        & (ahle_combo_scensmry_yearly['production_system'] == ahle_combo_scensmry_yearly['production_system'].unique()[0]) \
            & (ahle_combo_scensmry_yearly['item'] == ahle_combo_scensmry_yearly['item'].unique()[0])
snplt = sns.relplot(
	data=ahle_combo_scensmry_yearly.loc[_plot]
	,x='year'
	,y='mean_current'
	,kind='line'      # 'scatter' (default): scatterplot. 'line': line chart.
)
