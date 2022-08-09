#%% About
'''
'''
#%% Merge

# =============================================================================
#### Prep UN Geo codes
# =============================================================================
try:
   un_geo_codes.shape
except NameError:
   un_geo_codes = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'un_geo_codes.pkl.gz'))

un_geo_codes_tomatch = un_geo_codes.copy()

keep_rename_cols_ordered = {
    'shortname':'country'
    ,'iso3':'country_iso3'
    # ,'iso2':'country_iso2'
    }
un_geo_codes_tomatch = un_geo_codes_tomatch[list(keep_rename_cols_ordered)].rename(columns=keep_rename_cols_ordered)

# Add Puerto Rico
add_geo_codes = pd.DataFrame({"country":"Puerto Rico" ,"country_iso3":"PRI"}
                             ,index=[0])
un_geo_codes_tomatch = pd.concat([un_geo_codes_tomatch ,add_geo_codes])

countries_geocodes = list(un_geo_codes_tomatch['country'].unique())

# =============================================================================
#### Prep Base table: biomass
# =============================================================================
try:
   biomass.shape
except NameError:
   biomass = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))

countries_biomass = list(biomass['country'].unique())

# Reconcile country names with UN Geo Codes
recode_countries = {
    "China, Hong Kong SAR":"Hong Kong"
    ,"Cte d'Ivoire":"Côte d'Ivoire"
    ,"Sudan (former)":"Sudan"
}
biomass['country'] = biomass['country'].replace(recode_countries)

# Add country iso code
biomass_iso = pd.merge(
    left=biomass
    ,right=un_geo_codes_tomatch
    ,on='country'
    ,how='left'
    )
datainfo(biomass_iso)

biomass_iso_missing = biomass_iso.query("country_iso3.isnull()")

# =============================================================================
#### Prep FAO tables
# =============================================================================
try:
   fao_production_p.shape
except NameError:
   fao_production_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_production.pkl.gz'))

try:
   fao_producerprice_p.shape
except NameError:
   fao_producerprice_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_producerprice.pkl.gz'))

# Combine FAO tables
fao_combo = pd.merge(
    left=fao_production_p
    ,right=fao_producerprice_p
    ,on=['country' ,'year']
    ,how='outer'
    ,indicator='_merge_fao'
    )
fao_combo['_merge_fao'].value_counts()
fao_country_merge_status = fao_combo[['country' ,'_merge_fao']].value_counts()

countries_fao = list(fao_combo['country'].unique())

# Reconcile country names with UN Geo Codes
recode_countries = {
    "China":"China"
    ,"China, Hong Kong SAR":"Hong Kong"
    # ,"China, Macao SAR":""
    ,"China, Taiwan Province of":"Taiwan, Province of China"
    # ,"China, mainland":""
    ,"Sudan (former)":"Sudan"
}
fao_combo['country'] = fao_combo['country'].replace(recode_countries)

# Add country iso code
fao_combo_iso = pd.merge(
    left=fao_combo
    ,right=un_geo_codes_tomatch
    ,on='country'
    ,how='left'
    )
datainfo(fao_combo_iso)

# =============================================================================
#### Prep World Bank tables
# =============================================================================
try:
   wb_income.shape
except NameError:
   wb_income = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_income.pkl.gz'))

try:
   wb_region.shape
except NameError:
   wb_region = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_region.pkl.gz'))

try:
   wb_infl_exchg.shape
except NameError:
   wb_infl_exchg = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_infl_exchg.pkl.gz'))

# Combine World Bank tables
wb_combo = pd.merge(
    left=wb_income
    ,right=wb_region
    ,on='iso3'
    ,how='outer'
    ,indicator='_merge_wb_1'
    )
wb_combo['_merge_wb_1'].value_counts()

wb_combo = pd.merge(
    left=wb_combo
    ,right=wb_infl_exchg
    ,on=['iso3' ,'year']
    ,how='outer'
    ,indicator='_merge_wb_2'
    )
wb_combo['_merge_wb_2'].value_counts()

wb_combo = wb_combo.rename(columns={"iso3":"country_iso3"})

# =============================================================================
#### Merge
# =============================================================================
# FAO onto Biomass
world_ahle_abt = pd.merge(
    left=biomass_iso
    ,right=fao_combo_iso
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_1'
    )
world_ahle_abt['_merge_1'].value_counts()

# World Bank
world_ahle_abt = pd.merge(
    left=world_ahle_abt
    ,right=wb_combo
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_2'
    )
world_ahle_abt['_merge_2'].value_counts()

# Drop and Rename
world_ahle_abt = world_ahle_abt.drop(columns=[
    'country'
    ,'country_y'
    ,'time_code'
    ,'_merge_fao'
    ,'_merge_1'
    ,'flag_y'
    ,'_merge_wb_1'
    ,'_merge_wb_2'
    ,'_merge_2'
    ]
    ,errors='ignore')
world_ahle_abt = world_ahle_abt.rename(columns={'country_x':'country' ,'flag_x':'flag_biomass' ,'flag_y':'flag_wb'})

datainfo(world_ahle_abt)

# =============================================================================
#### Checks
# =============================================================================
# Missing iso3?
missing_iso3 = world_ahle_abt.query("country_iso3.isnull()")
missing_iso3_countries = list(iso3_missing['country'].unique())

# Missing incomegroup?
missing_incomegroup = world_ahle_abt.query("incomegroup.isnull()")
missing_incomegroup_countries = list(missing_incomegroup['country'].unique())

# Missing region?
missing_region = world_ahle_abt.query("region.isnull()")
missing_region_countries = list(missing_region['country'].unique())

#%% Assign columns to correct species

species_list = list(world_ahle_abt['species'].unique())
prices_lcu = [i for i in list(world_ahle_abt) if 'lcupertonne' in i]

# Assume missing production means zero production.
# If production is zero, corresponding price is missing.
def assign_columns_to_species(INPUT_ROW):
   if INPUT_ROW['species'].upper() == 'BUFFALOES':
       prod_eggs = 0
       prod_hides = INPUT_ROW['production_hides_buffalo_fresh_tonnes']
       prod_meat = INPUT_ROW['production_meat_buffalo_tonnes']
       prod_milk = INPUT_ROW['production_milk_whole_fresh_buffalo_tonnes']
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_buffalo_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_buffalo_lcupertonne']
       price_milk = INPUT_ROW['producer_price_milk_whole_fresh_buffalo_lcupertonne']
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'CAMELS':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_camel_tonnes']
       prod_milk = INPUT_ROW['production_milk_whole_fresh_camel_tonnes']
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_camel_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_camel_lcupertonne']
       price_milk = INPUT_ROW['producer_price_milk_whole_fresh_camel_lcupertonne']
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'CATTLE':
       prod_eggs = 0
       prod_hides = INPUT_ROW['production_hides_cattle_fresh_tonnes']
       prod_meat = INPUT_ROW['production_meat_cattle_tonnes']
       prod_milk = INPUT_ROW['production_milk_whole_fresh_cow_tonnes']
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_cattle_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_cattle_lcupertonne']
       price_milk = INPUT_ROW['producer_price_milk_whole_fresh_cow_lcupertonne']
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'CHICKENS':
       prod_eggs = INPUT_ROW['production_eggs_hen_in_shell_tonnes']
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_chicken_tonnes']
       prod_milk = 0
       prod_wool = 0

       price_eggs = INPUT_ROW['producer_price_eggs_hen_in_shell_lcupertonne']
       price_meat = INPUT_ROW['producer_price_meat_chicken_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_chicken_lcupertonne']
       price_milk = np.nan
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'DUCKS':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_duck_tonnes']
       prod_milk = 0
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_duck_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_duck_lcupertonne']
       price_milk = np.nan
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'GOATS':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_goat_tonnes']
       prod_milk = INPUT_ROW['production_milk_whole_fresh_goat_tonnes']
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_goat_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_goat_lcupertonne']
       price_milk = INPUT_ROW['producer_price_milk_whole_fresh_goat_lcupertonne']
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'HORSES':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_horse_tonnes']
       prod_milk = 0
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_horse_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_horse_lcupertonne']
       price_milk = np.nan
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'PIGS':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_pig_tonnes']
       prod_milk = 0
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_pig_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_pig_lcupertonne']
       price_milk = np.nan
       price_wool = np.nan
   elif INPUT_ROW['species'].upper() == 'SHEEP':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_sheep_tonnes']
       prod_milk = INPUT_ROW['production_milk_whole_fresh_sheep_tonnes']
       prod_wool = INPUT_ROW['production_wool_greasy_tonnes']

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_sheep_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_sheep_lcupertonne']
       price_milk = INPUT_ROW['producer_price_milk_whole_fresh_sheep_lcupertonne']
       price_wool = INPUT_ROW['producer_price_wool_greasy_lcupertonne']
   elif INPUT_ROW['species'].upper() == 'TURKEYS':
       prod_eggs = 0
       prod_hides = 0
       prod_meat = INPUT_ROW['production_meat_turkey_tonnes']
       prod_milk = 0
       prod_wool = 0

       price_eggs = np.nan
       price_meat = INPUT_ROW['producer_price_meat_turkey_lcupertonne']
       price_meat_live = INPUT_ROW['producer_price_meat_livewt_turkey_lcupertonne']
       price_milk = np.nan
       price_wool = np.nan
   else:
       prod_eggs = 0
       prod_hides = 0
       prod_meat = 0
       prod_milk = 0
       prod_wool = 0

       price_eggs = np.nan
       price_meat = np.nan
       price_meat_live = np.nan
       price_milk = np.nan
       price_wool = np.nan
   return pd.Series([prod_eggs ,prod_hides ,prod_meat ,prod_milk ,prod_wool
                     ,price_eggs ,price_meat ,price_meat_live ,price_milk ,price_wool])
world_ahle_abt[[
    'productionKEEP_eggs_tonnes'
    ,'productionKEEP_hides_tonnes'
    ,'productionKEEP_meat_tonnes'
    ,'productionKEEP_milk_tonnes'
    ,'productionKEEP_wool_tonnes'
    ,'producer_priceKEEP_eggs_lcupertonne'
    ,'producer_priceKEEP_meat_lcupertonne'
    ,'producer_priceKEEP_meat_live_lcupertonne'
    ,'producer_priceKEEP_milk_lcupertonne'
    ,'producer_priceKEEP_wool_lcupertonne'
    ]] = world_ahle_abt.apply(assign_columns_to_species ,axis=1)

# Drop species-specific columns
orig_production_cols = [i for i in list(world_ahle_abt) if 'production_' in i]
orig_price_cols = [i for i in list(world_ahle_abt) if 'producer_price_' in i]
world_ahle_abt = world_ahle_abt.drop(columns=orig_production_cols + orig_price_cols)

# Remove KEEP flag from new columns
world_ahle_abt.columns = world_ahle_abt.columns.str.replace('KEEP' ,'')

datainfo(world_ahle_abt)

# =============================================================================
# # Not used
# producer_price_eggs_other_bird_in_shell_lcupertonne
#
# producer_price_meat_livewt_ass_lcupertonne
# producer_price_meat_livewt_camelids_other_lcupertonne
# producer_price_meat_livewt_goose_lcupertonne
# producer_price_meat_livewt_mule_lcupertonne
# producer_price_meat_livewt_poultry_other_lcupertonne
# producer_price_meat_livewt_rabbit_lcupertonne
#
# producer_price_meat_ass_lcupertonne
# producer_price_meat_game_lcupertonne
# producer_price_meat_goose_and_guinea_fowl_lcupertonne
# producer_price_meat_mule_lcupertonne
# producer_price_meat_other_camelids_lcupertonne
# producer_price_meat_rabbit_lcupertonne
#
# production_meat_game_tonnes
# production_meat_rabbit_tonnes
# production_meat_ass_tonnes
# production_meat_goose_and_guinea_fowl_tonnes
# production_meat_mule_tonnes
# production_meat_other_camelids_tonnes
# production_meat_other_rodents_tonnes
# =============================================================================

#%% Describe and output

world_ahle_abt.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.csv'))
world_ahle_abt.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.pkl.gz'))

#%% Impute

# =============================================================================
#### Production
# =============================================================================
# Fill missings with zero
production_cols = [i for i in list(world_ahle_abt) if 'production_' in i]
for COL in production_cols:
    origcol = COL + '_raw'
    world_ahle_abt[origcol] = world_ahle_abt[COL]                   # Create copy of original column
    world_ahle_abt[COL] = world_ahle_abt[COL].replace(np.nan ,0)    # Impute
datainfo(world_ahle_abt)

# =============================================================================
#### Producer Prices
# =============================================================================
price_cols = [i for i in list(world_ahle_abt) if 'producer_price_' in i]

# -----------------------------------------------------------------------------
# Most universal: average price by species and year for countries in same
# region and income group, weighted by production
# -----------------------------------------------------------------------------
# Get average price for each species, region, and income group, weighted by production
world_ahle_abt.eval(
    '''
    total_lcu_eggs = producer_price_eggs_lcupertonne * production_eggs_tonnes
    total_lcu_meat = producer_price_meat_lcupertonne * production_meat_tonnes
    total_lcu_meat_live = producer_price_meat_live_lcupertonne * production_meat_tonnes
    total_lcu_milk = producer_price_milk_lcupertonne * production_milk_tonnes
    total_lcu_wool = producer_price_wool_lcupertonne * production_wool_tonnes
    '''
    ,inplace=True
)

avgprice_specreginc = world_ahle_abt.pivot_table(
   index=['species' ,'year' ,'region' ,'incomegroup']
   ,values=[
       'total_lcu_eggs' ,'production_eggs_tonnes'
       ,'total_lcu_meat' ,'production_meat_tonnes'
       ,'total_lcu_meat_live'
       ,'total_lcu_milk' ,'production_milk_tonnes'
       ,'total_lcu_wool' ,'production_wool_tonnes'
       ]
   ,aggfunc='sum'
)
avgprice_specreginc = avgprice_specreginc.add_suffix('_sum')
avgprice_specreginc = avgprice_specreginc.reset_index()
avgprice_specreginc.eval(
    '''
    producer_price_eggs_lcupertonne_wtavg = total_lcu_eggs_sum / production_eggs_tonnes_sum
    producer_price_meat_lcupertonne_wtavg = total_lcu_meat_sum / production_meat_tonnes_sum
    producer_price_meat_live_lcupertonne_wtavg = total_lcu_meat_live_sum / production_meat_tonnes_sum
    producer_price_milk_lcupertonne_wtavg = total_lcu_milk_sum / production_milk_tonnes_sum
    producer_price_wool_lcupertonne_wtavg = total_lcu_wool_sum / production_wool_tonnes_sum
    '''
    ,inplace=True
)
datainfo(avgprice_specreginc)

# Merge average prices onto base data
world_ahle_abt = pd.merge(
    left=world_ahle_abt
    ,right=avgprice_specreginc
    ,on=['species' ,'year' ,'region' ,'incomegroup']
    ,how='left'
)
datainfo(world_ahle_abt)

# Where prices are missing, fill with average
for COL in price_cols:
    world_ahle_abt[f"{COL}_raw"] = world_ahle_abt[COL]      # Create copy of original column
    _null_rows = (world_ahle_abt[COL].isnull())
    world_ahle_abt.loc[_null_rows ,COL] = world_ahle_abt.loc[_null_rows ,f"{COL}_wtavg"]

# Prices will still be missing for species where they don't apply.
# Check missings by species
species_recordcount = world_ahle_abt['species'].value_counts()
check_price_imp = world_ahle_abt.pivot_table(
   index='species'
   ,values=price_cols
   ,aggfunc='count'
)
check_price_imp = check_price_imp.add_suffix('_nonmissing')

# Drop intermediate columns
dropcols = [i for i in list(world_ahle_abt) if 'total_lcu' in i]
dropcols += [i for i in list(world_ahle_abt) if '_sum' in i]
dropcols += [i for i in list(world_ahle_abt) if '_wtavg' in i]
world_ahle_abt = world_ahle_abt.drop(columns=dropcols)
datainfo(world_ahle_abt)

# -----------------------------------------------------------------------------
# Average adjacent years for same country and species, weighted by production
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# For Meat (dead) and meat (live), if one is non-missing, set the other using a conversion rate
# -----------------------------------------------------------------------------
