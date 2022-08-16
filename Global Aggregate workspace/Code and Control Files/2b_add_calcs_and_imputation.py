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
    ,"NRU":"UNK"
    ,"TUV":"UNK"
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
    Use same liveweight (it is constant for each country and species)
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
#### Summarize imputation changes
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
    # snplt = sns.catplot(
    #     data=check_imputation
    #     ,x='species'
    #     ,y='impdiff'
    #     # ,hue='colorvar'
    #     ,kind='box'
    #     ,orient='v'
    #     )
    # plt.title(COL)

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
# =============================================================================
#### Summarize
# =============================================================================
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

# What is the distribution of production per kg biomass for each product?
for PROD_BASE in production_cols:
    # Global
    snplt = sns.catplot(
        data=world_ahle_abt
        ,y=f"{PROD_BASE}_perkgbm"
        ,kind='box'
        ,orient='v'
        )
    plt.title(f"Distribution Globally\n{PROD_BASE} per kg biomass")

    # By Region
    snplt = sns.catplot(
        data=world_ahle_abt
        ,x='region'
        ,y=f"{PROD_BASE}_perkgbm"
        ,kind='box'
        ,orient='v'
        )
    plt.title(f"Distribution by Region\n{PROD_BASE} per kg biomass")

    # By Income group
    snplt = sns.catplot(
        data=world_ahle_abt
        ,x='incomegroup'
        ,y=f"{PROD_BASE}_perkgbm"
        ,kind='box'
        ,orient='v'
        )
    plt.title(f"Distribution by Income Group\n{PROD_BASE} per kg biomass")

# =============================================================================
#### Impute
# =============================================================================
# Check average for meat at different levels of aggregation
# wtavg1_meat_perkgbm = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="production_meat_tonnes_perkgbm"
#     ,WT_VAR='biomass'
#     ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
# )
# wtavg2a_meat_perkgbm = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="production_meat_tonnes_perkgbm"
#     ,WT_VAR='biomass'
#     ,BY_VARS=['species' ,'year' ,'incomegroup']
# )
# wtavg2b_meat_perkgbm = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="production_meat_tonnes_perkgbm"
#     ,WT_VAR='biomass'
#     ,BY_VARS=['species' ,'year' ,'region']
# )
# wtavg3_meat_perkgbm = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="production_meat_tonnes_perkgbm"
#     ,WT_VAR='biomass'
#     ,BY_VARS=['species' ,'year']
# )

# Find average for each species, year, region, and income group, weighted by biomass
# UPDATE: Using median price instead of average as it is robust to outliers.
for PRODCOL in production_cols:
    # # -----------------------------------------------------------------------------
    # # Calculate averages at different aggregation levels
    # # -----------------------------------------------------------------------------
    # # Get weighted average by group at least aggregate level
    # wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
    #     ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
    #     ,RESULT_SUFFIX='_wtavg1'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg1"]
    #     ,on=['species' ,'year' ,'region' ,'incomegroup']
    #     ,how='left'
    # )
    # # Get weighted average by group at middle aggregate level
    # wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
    #     ,BY_VARS=['species' ,'year' ,'incomegroup']
    #     ,RESULT_SUFFIX='_wtavg2a'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg2a"]
    #     ,on=['species' ,'year' ,'incomegroup']
    #     ,how='left'
    # )
    # # Get weighted average by group at middle aggregate level
    # wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
    #     ,BY_VARS=['species' ,'year' ,'region']
    #     ,RESULT_SUFFIX='_wtavg2b'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg2b"]
    #     ,on=['species' ,'year' ,'region']
    #     ,how='left'
    # )
    # # Get weighted average by group at most aggregate level
    # wtavg = weighted_average(world_ahle_abt ,AVG_VAR=f"{PRODCOL}_perkgbm" ,WT_VAR='biomass'
    #     ,BY_VARS=['species' ,'year']
    #     ,RESULT_SUFFIX='_wtavg3'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRODCOL}_perkgbm_wtavg3"]
    #     ,on=['species' ,'year']
    #     ,how='left'
    # )

    # -----------------------------------------------------------------------------
    # Alternative: get median at different aggregation levels
    # -----------------------------------------------------------------------------
    # Get median by group at least aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year' ,'region' ,'incomegroup']
       ,values=f"{PRODCOL}_perkgbm" ,aggfunc='median'
    )
    median = median.add_suffix('_median1')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year' ,'region' ,'incomegroup']
        ,how='left'
    )

    # Get median by group at mid aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year' ,'incomegroup']
       ,values=f"{PRODCOL}_perkgbm" ,aggfunc='median'
    )
    median = median.add_suffix('_median2a')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year' ,'incomegroup']
        ,how='left'
    )

    # Get median by group at mid aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year' ,'region']
       ,values=f"{PRODCOL}_perkgbm" ,aggfunc='median'
    )
    median = median.add_suffix('_median2b')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year' ,'region']
        ,how='left'
    )

    # Get median by group at most aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year']
       ,values=f"{PRODCOL}_perkgbm" ,aggfunc='median'
    )
    median = median.add_suffix('_median3')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
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
        # ,f'{PRODCOL}_perkgbm_wtavg1'
        # ,f'{PRODCOL}_perkgbm_wtavg2a'
        # ,f'{PRODCOL}_perkgbm_wtavg2b'
        # ,f'{PRODCOL}_perkgbm_wtavg3'
        ,f'{PRODCOL}_perkgbm_median1'
        ,f'{PRODCOL}_perkgbm_median2a'
        ,f'{PRODCOL}_perkgbm_median2b'
        ,f'{PRODCOL}_perkgbm_median3'
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
#### Summarize imputation changes
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
    # snplt = sns.catplot(
    #     data=check_imputation
    #     ,x='species'
    #     ,y='impdiff'
    #     # ,hue='colorvar'
    #     ,kind='box'
    #     ,orient='v'
    #     )
    # plt.title(COL)

#%% Producer Prices

# =============================================================================
#### Summarize
# =============================================================================
price_cols = [i for i in list(world_ahle_abt) if 'producer_price_' in i]
price_cols_base = [
    'producer_price_eggs'
    ,'producer_price_meat'
    ,'producer_price_meat_live'
    ,'producer_price_milk'
    ,'producer_price_wool'
]

# Where is price missing?
missing_price_eggs = world_ahle_abt.query("producer_price_eggs_lcupertonne.isnull()")
missing_price_eggs_species = list(missing_price_eggs['species'].unique())

missing_price_meat = world_ahle_abt.query("producer_price_meat_lcupertonne.isnull()")
missing_price_meat_species = list(missing_price_meat['species'].unique())

missing_price_meat_live = world_ahle_abt.query("producer_price_meat_live_lcupertonne.isnull()")
missing_price_meat_live_species = list(missing_price_meat_live['species'].unique())

missing_price_milk = world_ahle_abt.query("producer_price_milk_lcupertonne.isnull()")
missing_price_milk_species = list(missing_price_milk['species'].unique())

missing_price_wool = world_ahle_abt.query("producer_price_wool_lcupertonne.isnull()")
missing_price_wool_species = list(missing_price_wool['species'].unique())

# =============================================================================
#### Calculate constant US dollars
# =============================================================================
'''
The World Bank and the IMF seem to agree on an approach for converting prices in LCU to constant US dollars:
1. Convert LCU each year to constant price for a base year by adjusting for inflation.
    Calculate the annual growth in constant LCU price.
2. Convert LCU to USD for the base year by applying the exchange rate for that year.
3. Apply the annual growth from step 1 to the USD price from step 2 to get the USD price each year.

IMF:
https://www.imf.org/external/pubs/ft/weo/faq.htm#q3c

World Bank:
These descriptions are not as clear, but upon re-reading, they seem to agree with the IMF.

Short description:
https://datahelpdesk.worldbank.org/knowledgebase/articles/114943-what-is-your-constant-u-s-dollar-methodology

Longer description in paragraph 2:
https://datahelpdesk.worldbank.org/knowledgebase/articles/114968-how-do-you-derive-your-constant-price-series-for-t
'''
def addcol_constant_currency(INPUT_DF ,CURRENCY_COLUMN ,CPI_COLUMN):
    # Apply CPI ratio to get constant currency
    # Using method from https://www.census.gov/topics/income-poverty/income/guidance/current-vs-constant-dollars.html
    # Also explained here https://www.investopedia.com/terms/c/constantdollar.asp
    constant_currency = INPUT_DF[CURRENCY_COLUMN] * (100 / INPUT_DF[CPI_COLUMN])  # Will return constant currency for same year that CPI is indexed to
    return constant_currency

for PRICE_BASE in price_cols_base:
    # Convert LCU each year to constant price for reference year by adjusting for inflation
    world_ahle_abt[f"{PRICE_BASE}_lcupertonne_cnst2010"] = \
        addcol_constant_currency(world_ahle_abt ,f"{PRICE_BASE}_lcupertonne" ,'cpi_2010idx')

    # If LCU price is coded missing, code constant price the same
    _row_selection = (world_ahle_abt[f"{PRICE_BASE}_lcupertonne"] == 999.999)
    world_ahle_abt.loc[_row_selection ,f"{PRICE_BASE}_lcupertonne_cnst2010"] = 999.999

    # Add reference year price as both LCU and USD to data, by country and species
    ref_price_rows = (world_ahle_abt['year'] == 2010)
    ref_price_columns = ['country' ,'species' ,f"{PRICE_BASE}_lcupertonne" ,f"{PRICE_BASE}_usdpertonne"]
    ref_price_df = world_ahle_abt.loc[ref_price_rows ,ref_price_columns]

    ref_price_df = ref_price_df.set_index(keys=['country' ,'species'] ,drop=True ,append=False)
    ref_price_df = ref_price_df.add_suffix('_2010')
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=ref_price_df ,on=['country' ,'species'] ,how='left')

    # Calculate the annual growth in LCU from reference year
    world_ahle_abt[f"{PRICE_BASE}_lcupertonne_growth"] = \
        world_ahle_abt[f"{PRICE_BASE}_lcupertonne_cnst2010"] / world_ahle_abt[f"{PRICE_BASE}_lcupertonne_2010"]

    # Apply the annual growth in LCU to the USD price for reference year
    world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010"] = \
        world_ahle_abt[f"{PRICE_BASE}_usdpertonne_2010"] * world_ahle_abt[f"{PRICE_BASE}_lcupertonne_growth"]

datainfo(world_ahle_abt)

# =============================================================================
#### Apply exchange rates
# =============================================================================
# for PRICE_BASE in price_cols_base:
#     # Calculate USD by appling exchange rate
#     world_ahle_abt[f"{PRICE_BASE}_usdpertonne_calc"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne"] / world_ahle_abt["exchg_lcuperusd"]

#     # If LCU price is coded missing, code USD the same
#     _row_selection = (world_ahle_abt[f"{PRICE_BASE}_lcupertonne"] == 999.999)
#     world_ahle_abt.loc[_row_selection ,f"{PRICE_BASE}_usdpertonne_calc"] = 999.999

# datainfo(world_ahle_abt)

# -----------------------------------------------------------------------------
# Explore
# -----------------------------------------------------------------------------
# # Are there differences between USD prices as reported by FAO and as calculated by me?
# # Yes. Particularly in countries that had wild currency fluctuations where World Bank exchange rate didn't adjust.
# for PRICE_BASE in price_cols_base:
#     world_ahle_abt[f'check_diff_{PRICE_BASE}_usdpertonne'] = \
#         world_ahle_abt[f"{PRICE_BASE}_usdpertonne_calc"] / world_ahle_abt[f"{PRICE_BASE}_usdpertonne"]

# # Test: Does order matter for inflation adjustment and exchange rate calcs?
# for PRICE_BASE in price_cols_base:
#     # First adjust for inflation, then apply exchange rate
#     world_ahle_abt[f"{PRICE_BASE}_lcupertonne_cnst"] = \
#         addcol_constant_currency(world_ahle_abt ,f"{PRICE_BASE}_lcupertonne" ,'cpi_2010idx')
#     world_ahle_abt[f"{PRICE_BASE}_cnst_exchg"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne_cnst"] / world_ahle_abt["exchg_lcuperusd"]

#     # First apply exchange rate, then adjust for inflation
#     world_ahle_abt[f"{PRICE_BASE}_usdpertonne_calc"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne"] / world_ahle_abt["exchg_lcuperusd"]
#     world_ahle_abt[f"{PRICE_BASE}_exchg_cnst"] = \
#         addcol_constant_currency(world_ahle_abt ,f"{PRICE_BASE}_usdpertonne_calc" ,'cpi_2010idx')

# What is the distribution of price for each product in constant USD per tonne?
for PRICE_BASE in price_cols_base:
    # Global
    snplt = sns.catplot(
        data=world_ahle_abt
        ,y=f"{PRICE_BASE}_usdpertonne_cnst2010"
        ,kind='box'
        ,orient='v'
        )
    plt.title(f"Distribution Globally\n{PRICE_BASE} per tonne in constant 2010 USD")

    # By Region
    snplt = sns.catplot(
        data=world_ahle_abt
        ,x='region'
        ,y=f"{PRICE_BASE}_usdpertonne_cnst2010"
        ,kind='box'
        ,orient='v'
        )
    plt.title(f"Distribution by Region\n{PRICE_BASE} per tonne in constant 2010 USD")

    # By Income group
    snplt = sns.catplot(
        data=world_ahle_abt
        ,x='incomegroup'
        ,y=f"{PRICE_BASE}_usdpertonne_cnst2010"
        ,kind='box'
        ,orient='v'
        )
    plt.title(f"Distribution by Income Group\n{PRICE_BASE} per tonne in constant 2010 USD")

# # Identify countries with outlier prices for each species and year
# # Above 20k USD per tonne
# _row_selection = (world_ahle_abt['producer_price_meat_usdpertonne'] > 20000)
# high_prices_meat = world_ahle_abt.loc[_row_selection].copy()
# high_prices_meat_countries = list(high_prices_meat['country'].unique())

# =============================================================================
#### Impute
# =============================================================================
# -----------------------------------------------------------------------------
# Get average price in USD for each species, year, region, and income group,
# weighted by production.
# UPDATE: Using median price instead of average as it is robust to outliers.
# Does not make sense to take average LCU across multiple countries!
# Convert to USD first, and maybe constant 2010 dollars, and then find averages.
# -----------------------------------------------------------------------------
# wtavg1_price_meat = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="producer_price_meat_usdpertonne"
#     ,WT_VAR='production_meat_tonnes'
#     ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
# )
# wtavg2a_price_meat = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="producer_price_meat_usdpertonne"
#     ,WT_VAR='production_meat_tonnes'
#     ,BY_VARS=['species' ,'year' ,'incomegroup']
# )
# wtavg2b_price_meat = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="producer_price_meat_usdpertonne"
#     ,WT_VAR='production_meat_tonnes'
#     ,BY_VARS=['species' ,'year' ,'region']
# )
# wtavg3_price_meat = weighted_average(
#     world_ahle_abt
#     ,AVG_VAR="producer_price_meat_usdpertonne"
#     ,WT_VAR='production_meat_tonnes'
#     ,BY_VARS=['species' ,'year']
# )

# price_weight_lookup = {
#     'producer_price_eggs_usdpertonne':'production_eggs_tonnes'
#     ,'producer_price_meat_usdpertonne':'production_meat_tonnes'
#     ,'producer_price_meat_live_usdpertonne':'production_meat_tonnes'
#     ,'producer_price_milk_usdpertonne':'production_milk_tonnes'
#     ,'producer_price_wool_usdpertonne':'production_wool_tonnes'
# }
# for PRICE ,WEIGHT in price_weight_lookup.items():
    # # -----------------------------------------------------------------------------
    # # Calculate average price in USD at different aggregation levels
    # # -----------------------------------------------------------------------------
    # # Get weighted average by group at least aggregate level
    # wtavg = weighted_average(INPUT_DF=world_ahle_abt ,AVG_VAR=PRICE ,WT_VAR=WEIGHT
    #     ,BY_VARS=['species' ,'year' ,'region' ,'incomegroup']
    #     ,RESULT_SUFFIX='_wtavg1'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRICE}_wtavg1"]
    #     ,on=['species' ,'year' ,'region' ,'incomegroup']
    #     ,how='left'
    # )
    # # Get weighted average by group at middle aggregate level
    # wtavg = weighted_average(INPUT_DF=world_ahle_abt ,AVG_VAR=PRICE ,WT_VAR=WEIGHT
    #     ,BY_VARS=['species' ,'year' ,'incomegroup']
    #     ,RESULT_SUFFIX='_wtavg2a'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRICE}_wtavg2a"]
    #     ,on=['species' ,'year' ,'incomegroup']
    #     ,how='left'
    # )
    # # Get weighted average by group at middle aggregate level
    # wtavg = weighted_average(INPUT_DF=world_ahle_abt ,AVG_VAR=PRICE ,WT_VAR=WEIGHT
    #     ,BY_VARS=['species' ,'year' ,'region']
    #     ,RESULT_SUFFIX='_wtavg2b'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRICE}_wtavg2b"]
    #     ,on=['species' ,'year' ,'region']
    #     ,how='left'
    # )
    # # Get weighted average by group at most aggregate level
    # wtavg = weighted_average(INPUT_DF=world_ahle_abt ,AVG_VAR=PRICE ,WT_VAR=WEIGHT
    #     ,BY_VARS=['species' ,'year']
    #     ,RESULT_SUFFIX='_wtavg3'
    # )
    # # Merge with data
    # world_ahle_abt = pd.merge(
    #     left=world_ahle_abt
    #     ,right=wtavg[f"{PRICE}_wtavg3"]
    #     ,on=['species' ,'year']
    #     ,how='left'
    # )

for PRICE_BASE in price_cols_base:
    # -----------------------------------------------------------------------------
    # Alternative: get median price in USD at different aggregation levels
    # -----------------------------------------------------------------------------
    # Get median by group at least aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year' ,'region' ,'incomegroup']
       ,values=f"{PRICE_BASE}_usdpertonne_cnst2010" ,aggfunc='median'
    )
    median = median.add_suffix('_median1')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year' ,'region' ,'incomegroup']
        ,how='left'
    )

    # Get median by group at mid aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year' ,'incomegroup']
       ,values=f"{PRICE_BASE}_usdpertonne_cnst2010" ,aggfunc='median'
    )
    median = median.add_suffix('_median2a')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year' ,'incomegroup']
        ,how='left'
    )

    # Get median by group at mid aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year' ,'region']
       ,values=f"{PRICE_BASE}_usdpertonne_cnst2010" ,aggfunc='median'
    )
    median = median.add_suffix('_median2b')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year' ,'region']
        ,how='left'
    )

    # Get median by group at most aggregate level
    median = world_ahle_abt.pivot_table(
       index=['species' ,'year']
       ,values=f"{PRICE_BASE}_usdpertonne_cnst2010" ,aggfunc='median'
    )
    median = median.add_suffix('_median3')
    # Merge with data
    world_ahle_abt = pd.merge(left=world_ahle_abt ,right=median
        ,on=['species' ,'year']
        ,how='left'
    )

    # -----------------------------------------------------------------------------
    # Where price in USD is missing, fill with average
    # -----------------------------------------------------------------------------
    _null_rows = (world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010"].isnull())
    print(f"> Filling {_null_rows.sum() :,} rows where {PRICE_BASE}_usdpertonne_cnst2010 is missing.")

    world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010_raw"] = world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010"]      # Create copy of original column
    candidate_cols_inorder = [
        f"{PRICE_BASE}_usdpertonne_cnst2010_raw"
        # ,f'{PRICE}_wtavg1'
        # ,f'{PRICE}_wtavg2a'
        # ,f'{PRICE}_wtavg2b'
        # ,f'{PRICE}_wtavg3'
        ,f'{PRICE_BASE}_usdpertonne_cnst2010_median1'
        ,f'{PRICE_BASE}_usdpertonne_cnst2010_median2a'
        ,f'{PRICE_BASE}_usdpertonne_cnst2010_median2b'
        ,f'{PRICE_BASE}_usdpertonne_cnst2010_median3'
        ]
    world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010"] = take_first_nonmissing(world_ahle_abt ,candidate_cols_inorder)

    # -----------------------------------------------------------------------------
    # Replace coded values (supposed to be missing) with np.nan
    # -----------------------------------------------------------------------------
    world_ahle_abt[f"{PRICE_BASE}_lcupertonne"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne"].replace(999.999 ,np.nan)
    world_ahle_abt[f"{PRICE_BASE}_usdpertonne"] = world_ahle_abt[f"{PRICE_BASE}_usdpertonne"].replace(999.999 ,np.nan)
    world_ahle_abt[f"{PRICE_BASE}_lcupertonne_cnst2010"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne_cnst2010"].replace(999.999 ,np.nan)
    world_ahle_abt[f"{PRICE_BASE}_lcupertonne_2010"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne_2010"].replace(999.999 ,np.nan)
    world_ahle_abt[f"{PRICE_BASE}_usdpertonne_2010"] = world_ahle_abt[f"{PRICE_BASE}_usdpertonne_2010"].replace(999.999 ,np.nan)
    world_ahle_abt[f"{PRICE_BASE}_lcupertonne_growth"] = world_ahle_abt[f"{PRICE_BASE}_lcupertonne_growth"].replace(1 ,np.nan)
    world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010"] = world_ahle_abt[f"{PRICE_BASE}_usdpertonne_cnst2010"].replace(999.999 ,np.nan)

datainfo(world_ahle_abt)

# # -----------------------------------------------------------------------------
# # Recalculate price in LCU
# # -----------------------------------------------------------------------------
# for PRICE_BASE in price_cols_base:
#     world_ahle_abt.eval(
#         f'''
#         {PRICE_BASE}_lcupertonne_raw = {PRICE_BASE}_lcupertonne
#         {PRICE_BASE}_lcupertonne = {PRICE_BASE}_usdpertonne * exchg_lcuperusd
#         '''
#         ,inplace=True
#     )

# =============================================================================
#### Checks
# =============================================================================
# # Check meat vs. live meat price for each country, species, and year
# world_ahle_abt.eval(
#     '''
#     check_price_meat_vs_live = producer_price_meat_usdpertonne / producer_price_meat_live_usdpertonne
#     check_price_raw_meat_vs_live = producer_price_meat_usdpertonne_raw / producer_price_meat_live_usdpertonne_raw
#     '''
#     ,inplace=True
# )
# datainfo(world_ahle_abt)

# =============================================================================
#### Summarize imputation changes
# =============================================================================
# Note: if original column was missing, it will not be counted as different from
# the imputed value.
imputed_cols = [
    'producer_price_eggs_usdpertonne_cnst2010'
    ,'producer_price_meat_usdpertonne_cnst2010'
    ,'producer_price_meat_live_usdpertonne_cnst2010'
    ,'producer_price_milk_usdpertonne_cnst2010'
    ,'producer_price_wool_usdpertonne_cnst2010'
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
    # snplt = sns.catplot(
    #     data=check_imputation
    #     ,x='species'
    #     ,y='impdiff'
    #     # ,hue='colorvar'
    #     ,kind='box'
    #     ,orient='v'
    #     )
    # plt.title(COL)

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

    ,'production_eggs_tonnes'
    ,'production_eggs_tonnes_perkgbm'
    ,'production_hides_tonnes'
    ,'production_hides_tonnes_perkgbm'
    ,'production_meat_tonnes'
    ,'production_meat_tonnes_perkgbm'
    ,'production_milk_tonnes'
    ,'production_milk_tonnes_perkgbm'
    ,'production_wool_tonnes'
    ,'production_wool_tonnes_perkgbm'

    # ,'producer_price_eggs_lcupertonne'
    # ,'producer_price_eggs_usdpertonne'
    ,'producer_price_eggs_usdpertonne_cnst2010'

    # ,'producer_price_meat_lcupertonne'
    # ,'producer_price_meat_usdpertonne'
    ,'producer_price_meat_usdpertonne_cnst2010'

    # ,'producer_price_meat_live_lcupertonne'
    # ,'producer_price_meat_live_usdpertonne'
    ,'producer_price_meat_live_usdpertonne_cnst2010'

    # ,'producer_price_milk_lcupertonne'
    # ,'producer_price_milk_usdpertonne'
    ,'producer_price_milk_usdpertonne_cnst2010'

    # ,'producer_price_wool_lcupertonne'
    # ,'producer_price_wool_usdpertonne'
    ,'producer_price_wool_usdpertonne_cnst2010'
]
dist_bycountryspecies_aslist = []   # Initialize
for VAR in vars_for_distributions:
    # Get distribution of variable as dataframe
   df_desc = world_ahle_abt.groupby(['country' ,'species'])[VAR].describe()
   df_desc = indextocolumns(df_desc)
   df_desc['variable'] = VAR
   df_desc_aslist = df_desc.to_dict(orient='records')
   dist_bycountryspecies_aslist.extend(df_desc_aslist)

    # Get distribution of raw variable (before imputation)
   df_desc = world_ahle_abt.groupby(['country' ,'species'])[f"{VAR}_raw"].describe()
   df_desc = indextocolumns(df_desc)
   df_desc['variable'] = f"{VAR}_raw"
   df_desc_aslist = df_desc.to_dict(orient='records')
   dist_bycountryspecies_aslist.extend(df_desc_aslist)

dist_bycountryspecies = pd.DataFrame.from_dict(dist_bycountryspecies_aslist ,orient='columns')
del dist_bycountryspecies_aslist

dist_bycountryspecies['iqr'] = dist_bycountryspecies['75%'] - dist_bycountryspecies['25%']
dist_bycountryspecies['max_iqrdist'] = (dist_bycountryspecies['max'] - dist_bycountryspecies['50%']) / dist_bycountryspecies['iqr']
dist_bycountryspecies['min_iqrdist'] = (dist_bycountryspecies['50%'] - dist_bycountryspecies['min']) / dist_bycountryspecies['iqr']
dist_bycountryspecies['range'] = dist_bycountryspecies['max'] - dist_bycountryspecies['min']
dist_bycountryspecies['range_mult'] = dist_bycountryspecies['max'] / dist_bycountryspecies['min']
dist_bycountryspecies['range_iqrdist'] = dist_bycountryspecies['range'] / dist_bycountryspecies['iqr']
dist_bycountryspecies['range_scaled'] = dist_bycountryspecies['range'] / dist_bycountryspecies['50%']

# =============================================================================
#### Plots
# =============================================================================
# Box plots by species (& country?)
# checkvar = 'biomass'
# for SPECIES in world_ahle_abt['species'].unique():
#    snplt = sns.catplot(
#       data=world_ahle_abt.query(f"species == '{SPECIES}'")
#       ,y=checkvar
#       ,kind='box'
#       ,orient='v'
#    )
#    plt.title(SPECIES)

# Plot over time for each species and country

# =============================================================================
#### Export
# =============================================================================
dist_bycountryspecies.to_csv(os.path.join(PROGRAM_OUTPUT_FOLDER ,'check_distributions_bycountryspecies.csv') ,index=False)

#%% Cleanup and output

# =============================================================================
#### Cleanup
# =============================================================================
# Remove intermediate columns
wtavg_cols = [i for i in list(world_ahle_abt) if '_wtavg' in i]
median_cols = [i for i in list(world_ahle_abt) if '_median' in i]
intermed_price_cols = [i for i in list(world_ahle_abt) if 'pertonne_2010' in i]
intermed_price_cols2 = [i for i in list(world_ahle_abt) if 'pertonne_growth' in i]

dropcols = wtavg_cols + median_cols + intermed_price_cols + intermed_price_cols2
world_ahle_abt = world_ahle_abt.drop(columns=dropcols ,errors='ignore')

datainfo(world_ahle_abt)

# =============================================================================
#### Export
# =============================================================================
world_ahle_abt.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.csv'))
world_ahle_abt.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.pkl.gz'))
