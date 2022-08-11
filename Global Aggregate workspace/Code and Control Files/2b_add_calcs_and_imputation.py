#%% About
'''
'''
#%% Read data

world_ahle_combo1 = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_combo1.pkl.gz'))

# Create a copy to be modified
world_ahle_abt = world_ahle_combo1.copy()

#%% Region and Income group

# -----------------------------------------------------------------------------
# Missing incomegroup?
# -----------------------------------------------------------------------------
# Not finding data on these, so filling with "Unk"
missing_incomegroup = world_ahle_abt.query("incomegroup.isnull()")
missing_incomegroup_countries = list(missing_incomegroup['country'].unique())

fill_iso3_income = {
    "COK":"UNK"
    ,"GLP":"UNK"
    ,"MTQ":"UNK"
    ,"NIU":"UNK"
}
for ISO3 ,INCOME in fill_iso3_income.items():
    world_ahle_abt.loc[world_ahle_abt['country_iso3'] == ISO3 ,'incomegroup'] = INCOME

# -----------------------------------------------------------------------------
# Missing region?
# -----------------------------------------------------------------------------
# Filling based on https://ourworldindata.org/grapher/world-regions-according-to-the-world-bank
missing_region = world_ahle_abt.query("region.isnull()")
missing_region_countries = list(missing_region['country'].unique())

fill_iso3_region = {
    "CAN":"NA"
    ,"USA":"NA"
    ,"COK":"EAP"
    ,"GLP":"LAC"
    ,"MTQ":"LAC"
    ,"NIU":"EAP"
}
for ISO3 ,REGION in fill_iso3_region.items():
    world_ahle_abt.loc[world_ahle_abt['country_iso3'] == ISO3 ,'region'] = REGION

#%% Population and Biomass
'''
Biomass table from GBADSKE only has data to 2017. Fill in later years as follows:
    Impute population with FAOstat stocks
    Use same liveweight as it is constant for each country and species
    Calculate biomass as population * liveweight
'''
# =============================================================================
#### Impute Population, Liveweight, and Biomass
# =============================================================================
# Create copies of original columns
world_ahle_abt['population_raw'] = world_ahle_abt['population']
world_ahle_abt['liveweight_raw'] = world_ahle_abt['liveweight']
world_ahle_abt['biomass_raw'] = world_ahle_abt['biomass']

# Impute population with FAOstat stocks
_popln_missing = (world_ahle_abt['population'].isnull())
print(f"> Filling {_popln_missing.sum(): ,} rows where population is missing.")
world_ahle_abt.loc[_popln_missing ,'population'] = world_ahle_abt.loc[_popln_missing ,'stocks_hd']

# Use same liveweight as it is constant for each country and species
liveweight_lookup = world_ahle_abt.pivot_table(
    index=['country' ,'species']
    ,values='liveweight'
    ,aggfunc=['min' ,'mean' ,'max' ,'std']
)
liveweight_lookup = colnames_from_index(liveweight_lookup)

world_ahle_abt = pd.merge(
    left=world_ahle_abt
    ,right=liveweight_lookup
    ,on=['country' ,'species']
    ,how='left'
)
_livewt_missing = (world_ahle_abt['liveweight'].isnull())
print(f"> Filling {_livewt_missing.sum(): ,} rows where liveweight is missing.")
world_ahle_abt.loc[_livewt_missing ,'liveweight'] = world_ahle_abt.loc[_livewt_missing ,'max_liveweight']

# Calculate biomass as population * liveweight
world_ahle_abt['biomass'] = world_ahle_abt['liveweight'] * world_ahle_abt['population']

# Cleanup intermediate columns
world_ahle_abt = world_ahle_abt.drop(columns=[
    'stocks_hd'
    ,'min_liveweight'
    ,'mean_liveweight'
    ,'max_liveweight'
    ,'std_liveweight'
    ])

datainfo(world_ahle_abt)

# =============================================================================
#### Summarize results of imputation
# =============================================================================
imputed_cols = ['population' ,'liveweight' ,'biomass']

for COL in imputed_cols:
    # Get raw and imputed versions and difference between them
    check_imputation = world_ahle_abt[['country' ,'species' ,'year' ,COL ,f'{COL}_raw']].copy()
    check_imputation['impdiff'] = check_imputation[COL] - check_imputation[f'{COL}_raw']
    check_imputation['impdiff_abs'] = abs(check_imputation['impdiff'])
    check_imputation['impdiff_pct'] = check_imputation['impdiff'] / check_imputation[f'{COL}_raw']

    # Number of rows different
    _nrows_impdiff = (check_imputation['impdiff_abs'] > 0)
    print(f"<check_imputation> {COL}: {_nrows_impdiff.sum(): ,} rows where imputed value is different from original.")

    # Boxplots of differences by Species
    snplt = sns.catplot(
        data=check_imputation
        ,x='species'
        ,y='impdiff'
        # ,hue='colorvar'
        ,kind='box'
        ,orient='v'
        )
    plt.title(COL)

    # Plot imputed vs. raw with reference line
    # Uses a lot of memory
    # scatterplot = sns.relplot(data=check_imputation ,x=f'{COL}_raw' ,y=COL ,alpha=0.2)
    # sns.lineplot(data=check_imputation ,x=f'{COL}_raw' ,y=f'{COL}_raw' ,ci=None ,ax=scatterplot.ax
    #              ,linestyle='--' ,linewidth=1 ,color='grey')
    # plt.title(COL)

#%% Production
'''
Plan:
First calculate production per kg biomass.
Impute this with average by species and year for countries in same region and
income group, weighted by biomass.
Back-calculate total production from production per kg biomass.
'''
# Where is production missing?
# Limited to appropriate species because other species get zero
missing_prod_eggs = world_ahle_abt.query("production_eggs_tonnes.isnull()")
missing_prod_eggs_species = list(missing_prod_eggs['species'].unique())

missing_prod_hides = world_ahle_abt.query("production_hides_tonnes.isnull()")
missing_prod_hides_species = list(missing_prod_hides['species'].unique())

missing_prod_meat = world_ahle_abt.query("production_meat_tonnes.isnull()")
missing_prod_meat_species = list(missing_prod_meat['species'].unique())

missing_prod_milk = world_ahle_abt.query("production_milk_tonnes.isnull()")
missing_prod_milk_species = list(missing_prod_milk['species'].unique())

missing_prod_wool = world_ahle_abt.query("production_wool_tonnes.isnull()")
missing_prod_wool_species = list(missing_prod_wool['species'].unique())

# =============================================================================
#### Calculate production outputs per kg biomass
# =============================================================================
production_cols = [i for i in list(world_ahle_abt) if 'production_' in i]

for PRODCOL in production_cols:
    # If biomass is zero, set production and production per kg biomass to zero
    _biomass_zero = (world_ahle_abt['biomass'] == 0)
    world_ahle_abt.loc[_biomass_zero ,f"{PRODCOL}"] = 0
    world_ahle_abt.loc[_biomass_zero ,f"{PRODCOL}_perkgbm"] = 0

    world_ahle_abt.loc[~ _biomass_zero ,f"{PRODCOL}_perkgbm"] = world_ahle_abt[PRODCOL] / world_ahle_abt['biomass']

missing_prod_eggs_perkgbm = world_ahle_abt.query("production_eggs_tonnes_perkgbm.isnull()")
missing_prod_hides_perkgbm = world_ahle_abt.query("production_hides_tonnes_perkgbm.isnull()")
missing_prod_meat_perkgbm = world_ahle_abt.query("production_meat_tonnes_perkgbm.isnull()")
missing_prod_milk_perkgbm = world_ahle_abt.query("production_milk_tonnes_perkgbm.isnull()")
missing_prod_wool_perkgbm = world_ahle_abt.query("production_wool_tonnes_perkgbm.isnull()")

# =============================================================================
#### Impute
# =============================================================================
# Check average for meat at different levels of aggregation
wtavg1_meat_perkgbm = weighted_average(
    world_ahle_abt
    ,AVG_VAR="production_meat_tonnes_perkgbm"
    ,WT_VAR='biomass'
    ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
)
wtavg2a_meat_perkgbm = weighted_average(
    world_ahle_abt
    ,AVG_VAR="production_meat_tonnes_perkgbm"
    ,WT_VAR='biomass'
    ,BY_VARS=['species' ,'year' ,'region']
)
wtavg2b_meat_perkgbm = weighted_average(
    world_ahle_abt
    ,AVG_VAR="production_meat_tonnes_perkgbm"
    ,WT_VAR='biomass'
    ,BY_VARS=['species' ,'year' ,'incomegroup']
)
wtavg3_meat_perkgbm = weighted_average(
    world_ahle_abt
    ,AVG_VAR="production_meat_tonnes_perkgbm"
    ,WT_VAR='biomass'
    ,BY_VARS=['species' ,'year']
)

# Find average for each species, year, region, and income group, weighted by biomass
for PRODCOL in production_cols:
    # -----------------------------------------------------------------------------
    # Calculate averages at different aggregation levels
    # -----------------------------------------------------------------------------
    # Get weighted average by group at least aggregate level
    wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
        ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
        ,RESULT_SUFFIX='_wtavg1'
    )
    # Merge with data
    world_ahle_abt = pd.merge(
        left=world_ahle_abt
        ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg1"]
        ,on=['species' ,'year' ,'region' ,'incomegroup']
        ,how='left'
    )
    # Get weighted average by group at middle aggregate level
    wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
        ,BY_VARS=['species' ,'year' ,'incomegroup']
        ,RESULT_SUFFIX='_wtavg2a'
    )
    # Merge with data
    world_ahle_abt = pd.merge(
        left=world_ahle_abt
        ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg2a"]
        ,on=['species' ,'year' ,'incomegroup']
        ,how='left'
    )
    # Get weighted average by group at middle aggregate level
    wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
        ,BY_VARS=['species' ,'year' ,'region']
        ,RESULT_SUFFIX='_wtavg2b'
    )
    # Merge with data
    world_ahle_abt = pd.merge(
        left=world_ahle_abt
        ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg2b"]
        ,on=['species' ,'year' ,'region']
        ,how='left'
    )
    # Get weighted average by group at most aggregate level
    wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
        ,BY_VARS=['species' ,'year']
        ,RESULT_SUFFIX='_wtavg3'
    )
    # Merge with data
    world_ahle_abt = pd.merge(
        left=world_ahle_abt
        ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg3"]
        ,on=['species' ,'year']
        ,how='left'
    )

    # -----------------------------------------------------------------------------
    # Where production per kg biomass is missing or zero, fill with average
    # -----------------------------------------------------------------------------
    _null_rows = (world_ahle_abt[f"{PRODCOL}_perkgbm"].isnull())
    print(f"> Filling {_null_rows.sum() :,} rows where {PRODCOL}_perkgbm is missing.")

    world_ahle_abt[f"{PRODCOL}_perkgbm_raw"] = world_ahle_abt[f"{PRODCOL}_perkgbm"]      # Create copy of original column
    candidate_cols_inorder = [
        f"{PRODCOL}_perkgbm_raw"
        ,f'{PRODCOL}_perkgbm_wtavg1'
        ,f'{PRODCOL}_perkgbm_wtavg2a'
        ,f'{PRODCOL}_perkgbm_wtavg2b'
        ,f'{PRODCOL}_perkgbm_wtavg3'
        ]
    world_ahle_abt[f"{PRODCOL}_perkgbm"] = take_first_nonmissing(world_ahle_abt ,candidate_cols_inorder)

    # -----------------------------------------------------------------------------
    # Recalculate production from production per kg biomass
    # -----------------------------------------------------------------------------
    _null_rows = (world_ahle_abt[f"{PRODCOL}"].isnull())
    print(f"> Filling {_null_rows.sum() :,} rows where {PRODCOL} is missing.")

    world_ahle_abt[f"{PRODCOL}_raw"] = world_ahle_abt[f"{PRODCOL}"]      # Create copy of original column
    world_ahle_abt[f"{PRODCOL}"] = round(world_ahle_abt[f"{PRODCOL}_perkgbm"] * world_ahle_abt['biomass'] ,0)   # Round to integer

datainfo(world_ahle_abt)

_check_imputed_prod_meat_perkg = (world_ahle_abt['production_meat_tonnes_perkgbm'] != world_ahle_abt['production_meat_tonnes_perkgbm_raw'])
check_imputed_prod_meat_perkg = world_ahle_abt[_check_imputed_prod_meat_perkg]

_check_imputed_prod_meat = (world_ahle_abt['production_meat_tonnes'] != world_ahle_abt['production_meat_tonnes_raw'])
check_imputed_prod_meat = world_ahle_abt[_check_imputed_prod_meat]

# =============================================================================
#### Summarize results of imputation
# =============================================================================
# Note: if original column was missing, it will not be counted as different from
# the imputed value.
imputed_cols = [
   'production_meat_tonnes'
   ,'production_meat_tonnes_perkgbm'
   ,'production_eggs_tonnes'
   ,'production_eggs_tonnes_perkgbm'
   ,'production_milk_tonnes'
   ,'production_milk_tonnes_perkgbm'
   ,'production_hides_tonnes'
   ,'production_hides_tonnes_perkgbm'
   ,'production_wool_tonnes'
   ,'production_wool_tonnes_perkgbm'
]

for COL in imputed_cols:
    # Get raw and imputed versions and difference between them
    check_imputation = world_ahle_abt[['country' ,'species' ,'year' ,COL ,f'{COL}_raw']].copy()
    check_imputation['impdiff'] = check_imputation[COL] - check_imputation[f'{COL}_raw']
    check_imputation['impdiff_abs'] = abs(check_imputation['impdiff'])
    check_imputation['impdiff_pct'] = check_imputation['impdiff'] / check_imputation[f'{COL}_raw']

    # Number of rows different
    _nrows_impdiff = (check_imputation['impdiff_abs'] > 0)
    print(f"<check_imputation> {COL}: {_nrows_impdiff.sum(): ,} rows where imputed value is different from original.")

    # Boxplots of differences by Species
    snplt = sns.catplot(
        data=check_imputation
        ,x='species'
        ,y='impdiff'
        # ,hue='colorvar'
        ,kind='box'
        ,orient='v'
        )
    plt.title(COL)

#%% Producer Prices

price_cols = [i for i in list(world_ahle_abt) if 'producer_price_' in i]

# -----------------------------------------------------------------------------
# Average price by species and year for countries in same region and income group,
# weighted by production.
# -----------------------------------------------------------------------------
# Get average price for each species, year, region, and income group, weighted by production
price_weight_lookup = {
    'producer_price_eggs_lcupertonne':'production_eggs_tonnes'
    ,'producer_price_meat_lcupertonne':'production_meat_tonnes'
    ,'producer_price_meat_live_lcupertonne':'production_meat_tonnes'
    ,'producer_price_milk_lcupertonne':'production_milk_tonnes'
    ,'producer_price_wool_lcupertonne':'production_wool_tonnes'
}
for PRICE ,WEIGHT in price_weight_lookup.items():
    wtavg = weighted_average(
        INPUT_DF=world_ahle_abt
        ,AVG_VAR=PRICE
        ,WT_VAR=WEIGHT
        ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
    )



# =============================================================================
# Before weighted_average() function
# # Get average price for each species, year, region, and income group, weighted by production
# world_ahle_abt.eval(
#     '''
#     total_lcu_eggs = producer_price_eggs_lcupertonne * production_eggs_tonnes
#     total_lcu_meat = producer_price_meat_lcupertonne * production_meat_tonnes
#     total_lcu_meat_live = producer_price_meat_live_lcupertonne * production_meat_tonnes
#     total_lcu_milk = producer_price_milk_lcupertonne * production_milk_tonnes
#     total_lcu_wool = producer_price_wool_lcupertonne * production_wool_tonnes
#     '''
#     ,inplace=True
# )
#
# avgprice_specreginc = world_ahle_abt.pivot_table(
#    index=['species' ,'year' ,'region' ,'incomegroup']
#    ,values=[
#        'total_lcu_eggs' ,'production_eggs_tonnes'
#        ,'total_lcu_meat' ,'production_meat_tonnes'
#        ,'total_lcu_meat_live'
#        ,'total_lcu_milk' ,'production_milk_tonnes'
#        ,'total_lcu_wool' ,'production_wool_tonnes'
#        ]
#    ,aggfunc='sum'
# )
# avgprice_specreginc = avgprice_specreginc.add_suffix('_sum')
# avgprice_specreginc = avgprice_specreginc.reset_index()
# avgprice_specreginc.eval(
#     '''
#     producer_price_eggs_lcupertonne_wtavg = total_lcu_eggs_sum / production_eggs_tonnes_sum
#     producer_price_meat_lcupertonne_wtavg = total_lcu_meat_sum / production_meat_tonnes_sum
#     producer_price_meat_live_lcupertonne_wtavg = total_lcu_meat_live_sum / production_meat_tonnes_sum
#     producer_price_milk_lcupertonne_wtavg = total_lcu_milk_sum / production_milk_tonnes_sum
#     producer_price_wool_lcupertonne_wtavg = total_lcu_wool_sum / production_wool_tonnes_sum
#     '''
#     ,inplace=True
# )
# datainfo(avgprice_specreginc)
#
# # Merge average prices onto base data
# world_ahle_abt = pd.merge(
#     left=world_ahle_abt
#     ,right=avgprice_specreginc
#     ,on=['species' ,'year' ,'region' ,'incomegroup']
#     ,how='left'
# )
# datainfo(world_ahle_abt)
#
# # Where prices are missing, fill with average
# for COL in price_cols:
#     world_ahle_abt[f"{COL}_raw"] = world_ahle_abt[COL]      # Create copy of original column
#     _null_rows = (world_ahle_abt[COL].isnull())
#     world_ahle_abt.loc[_null_rows ,COL] = world_ahle_abt.loc[_null_rows ,f"{COL}_wtavg"]
#
# # Prices will still be missing for species where they don't apply.
# # Check missings by species
# species_recordcount = world_ahle_abt['species'].value_counts()
# check_price_imp = world_ahle_abt.pivot_table(
#    index='species'
#    ,values=price_cols
#    ,aggfunc='count'
# )
# check_price_imp = check_price_imp.add_suffix('_nonmissing')
#
# # Drop intermediate columns
# dropcols = [i for i in list(world_ahle_abt) if 'total_lcu' in i]
# dropcols += [i for i in list(world_ahle_abt) if '_sum' in i]
# dropcols += [i for i in list(world_ahle_abt) if '_wtavg' in i]
# world_ahle_abt = world_ahle_abt.drop(columns=dropcols)
# datainfo(world_ahle_abt)
#
# =============================================================================
# -----------------------------------------------------------------------------
# For meat (dead) and meat (live) prices, if one is non-missing, set the other
# using a conversion rate
# -----------------------------------------------------------------------------

#%% Data checks

# Population, Liveweight, Biomass
# Each production metric and price

# =============================================================================
#### Data summaries
# =============================================================================
# Distribution by country and species
vars_for_distributions = [
   'population'
   ,'liveweight'
   ,'biomass'

   ,'production_meat_tonnes'
   ,'production_meat_tonnes_perkgbm'
   ,'production_eggs_tonnes'
   ,'production_eggs_tonnes_perkgbm'
   ,'production_milk_tonnes'
   ,'production_milk_tonnes_perkgbm'
   ,'production_hides_tonnes'
   ,'production_hides_tonnes_perkgbm'
   ,'production_wool_tonnes'
   ,'production_wool_tonnes_perkgbm'
]
dist_bycountryspecies = pd.DataFrame()   # Initialize
for VAR in vars_for_distributions:
   df_desc = world_ahle_abt.groupby(['country' ,'species'])[VAR].describe()
   df_desc = indextocolumns(df_desc)
   df_desc['variable'] = VAR
   dist_bycountryspecies = pd.concat([dist_bycountryspecies ,df_desc] ,ignore_index=True)

dist_bycountryspecies['range'] = dist_bycountryspecies['max'] - dist_bycountryspecies['min']
dist_bycountryspecies['range_scaled'] = dist_bycountryspecies['range'] / dist_bycountryspecies['50%']

# =============================================================================
#### Plots
# =============================================================================
# Box plots by species (& country?)
checkvar = 'biomass'
for SPECIES in world_ahle_abt['species'].unique():
   snplt = sns.catplot(
      data=world_ahle_abt.query(f"species == '{SPECIES}'")
      ,y=checkvar
      ,kind='box'
      ,orient='v'          # 'v' = vertical, 'h' = horizontal
   )
   plt.title(SPECIES)

# Plot over time for each species and country

#%% Describe and output

# Export
world_ahle_abt.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.csv'))
world_ahle_abt.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.pkl.gz'))
