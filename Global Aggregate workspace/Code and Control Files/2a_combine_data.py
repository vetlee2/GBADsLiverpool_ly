#%% About
'''
'''
#%% Extend biomass data
'''
Biomass table from GBADSKE only has data to 2017. Extend with FAOstat population data to 2020.
'''
biomass = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))
fao_production_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_production.pkl.gz'))

# -----------------------------------------------------------------------------
# Create rows for additional years
# -----------------------------------------------------------------------------
# Get country*species combos from biomass data
biomass_country_spec_combos = pd.DataFrame(biomass[['iso3' ,'country' ,'species']].value_counts())
biomass_country_spec_combos = indextocolumns(biomass_country_spec_combos)
biomass_country_spec_combos['identity'] = 1     # Add constant column for merging

# Create full list of desired years
extend_years = pd.DataFrame({'year':range(2000 ,2021) ,'identity':1})

# Create dummy data with all desired countries, species, and years
extended_data = pd.merge(
    left=biomass_country_spec_combos
    ,right=extend_years
    ,on='identity'
    ,how='outer'
)

# Merge dummy data with biomass
biomass_extended = pd.merge(
    left=biomass
    ,right=extended_data[['iso3' ,'country' ,'species' ,'year']]
    ,on=['iso3' ,'country' ,'species' ,'year']
    ,how='right'    # Keep all rows from extended data
)

#%% Merge

# =============================================================================
#### Prep UN Geo codes
# =============================================================================
un_geo_codes = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'un_geo_codes.pkl.gz'))

un_geo_codes_tomatch = un_geo_codes.copy()

keep_rename_cols_ordered = {
    'shortname':'country'
    ,'iso3':'country_iso3'
    # ,'iso2':'country_iso2'
    }
un_geo_codes_tomatch = un_geo_codes_tomatch[list(keep_rename_cols_ordered)].rename(columns=keep_rename_cols_ordered)

# Add Puerto Rico
add_geo_codes = pd.DataFrame({"country":"Puerto Rico" ,"country_iso3":"PRI"} ,index=[0])
un_geo_codes_tomatch = pd.concat([un_geo_codes_tomatch ,add_geo_codes] ,ignore_index=True)

countries_geocodes = list(un_geo_codes_tomatch['country'].unique())

# =============================================================================
#### Prep Base table: biomass
# =============================================================================
# =============================================================================
# # No longer needed because Guelph has added iso3 to biomass table
# # Reconcile country names with UN Geo Codes
# countries_biomass = list(biomass_extended['country'].unique())
# recode_countries = {
#     "China, Hong Kong SAR":"Hong Kong"
#     ,"Cte d'Ivoire":"Côte d'Ivoire"
#     ,"Sudan (former)":"Sudan"
# }
# biomass_extended['country'] = biomass_extended['country'].replace(recode_countries)
#
# # Add country iso code
# biomass_iso = pd.merge(
#     left=biomass_extended
#     ,right=un_geo_codes_tomatch
#     ,on='country'
#     ,how='left'
#     )
#
# =============================================================================
biomass_iso = biomass_extended.copy()
biomass_iso = biomass_iso.rename(columns={'iso3':'country_iso3'})

datainfo(biomass_iso)

biomass_iso_missing = biomass_iso.query("country_iso3.isnull()")

# =============================================================================
#### Prep FAO tables
# =============================================================================
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
# Income groups
wb_income = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_income.pkl.gz'))

# Regions
wb_region = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_region.pkl.gz'))

# Inflation and Exchange rates
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
# World Bank onto Biomass
world_ahle_combo1 = pd.merge(
    left=biomass_iso
    ,right=wb_combo
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_1'
    )
world_ahle_combo1['_merge_1'].value_counts()

# FAO
world_ahle_combo1 = pd.merge(
    left=world_ahle_combo1
    ,right=fao_combo_iso
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_2'
    )
world_ahle_combo1['_merge_2'].value_counts()

# Drop and Rename
world_ahle_combo1 = world_ahle_combo1.drop(columns=[
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
world_ahle_combo1 = world_ahle_combo1.rename(columns={'country_x':'country' ,'flag_x':'flag_biomass' ,'flag_y':'flag_wb'})

datainfo(world_ahle_combo1)

# =============================================================================
#### Checks
# =============================================================================
# Missing iso3?
missing_iso3 = world_ahle_combo1.query("country_iso3.isnull()")
missing_iso3_countries = list(missing_iso3['country'].unique())

#%% Assign columns to correct species

species_list = list(world_ahle_combo1['species'].unique())
prices_lcu = [i for i in list(world_ahle_combo1) if 'lcupertonne' in i]
fao_stocks_cols = [i for i in list(fao_production_p) if 'stocks' in i]

# Set production to zero for items that don't apply to a species
# Set prices to a coded value (999.999) for items that don't apply to a species
'''
Using Standard Local Currency from FAO:
    The Standard Local Currency of a country is set as the local currency prevailing in the current year.
    Prices in SLC are equal to producer prices in local currency multiplied by currency conversion factors.
    Currency conversion factors (CCF) are a special kind of exchange rates that convert the new currency
    of a given country into the old currency of the same country.
    These series are consistent over time and do not breaks when a currency change occurs.
    Source: FAO Statistics Division
'''
def assign_columns_to_species(INPUT_ROW):
    if INPUT_ROW['species'].upper() == 'BUFFALOES':
        stocks_hd = INPUT_ROW['stocks_buffaloes_head']

        prod_eggs = 0
        prod_hides = INPUT_ROW['production_hides_buffalo_fresh_tonnes']
        prod_meat = INPUT_ROW['production_meat_buffalo_tonnes']
        prod_milk = INPUT_ROW['production_milk_whole_fresh_buffalo_tonnes']
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_buffalo_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_buffalo_slcpertonne']
        price_milk_lcu = INPUT_ROW['producer_price_milk_whole_fresh_buffalo_slcpertonne']
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_buffalo_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_buffalo_usdpertonne']
        price_milk_usd = INPUT_ROW['producer_price_milk_whole_fresh_buffalo_usdpertonne']
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'CAMELS':
        stocks_hd = INPUT_ROW['stocks_camels_head']

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_camel_tonnes']
        prod_milk = INPUT_ROW['production_milk_whole_fresh_camel_tonnes']
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_camel_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_camel_slcpertonne']
        price_milk_lcu = INPUT_ROW['producer_price_milk_whole_fresh_camel_slcpertonne']
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_camel_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_camel_usdpertonne']
        price_milk_usd = INPUT_ROW['producer_price_milk_whole_fresh_camel_usdpertonne']
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'CATTLE':
        stocks_hd = INPUT_ROW['stocks_cattle_head']

        prod_eggs = 0
        prod_hides = INPUT_ROW['production_hides_cattle_fresh_tonnes']
        prod_meat = INPUT_ROW['production_meat_cattle_tonnes']
        prod_milk = INPUT_ROW['production_milk_whole_fresh_cow_tonnes']
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_cattle_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_cattle_slcpertonne']
        price_milk_lcu = INPUT_ROW['producer_price_milk_whole_fresh_cow_slcpertonne']
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_cattle_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_cattle_usdpertonne']
        price_milk_usd = INPUT_ROW['producer_price_milk_whole_fresh_cow_usdpertonne']
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'CHICKENS':
        stocks_hd = INPUT_ROW['stocks_chickens_1000_head'] * 1000

        prod_eggs = INPUT_ROW['production_eggs_hen_in_shell_tonnes']
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_chicken_tonnes']
        prod_milk = 0
        prod_wool = 0

        price_eggs_lcu = INPUT_ROW['producer_price_eggs_hen_in_shell_slcpertonne']
        price_meat_lcu = INPUT_ROW['producer_price_meat_chicken_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_chicken_slcpertonne']
        price_milk_lcu = 999.999
        price_wool_lcu = 999.999

        price_eggs_usd = INPUT_ROW['producer_price_eggs_hen_in_shell_usdpertonne']
        price_meat_usd = INPUT_ROW['producer_price_meat_chicken_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_chicken_usdpertonne']
        price_milk_usd = 999.999
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'DUCKS':
        stocks_hd = INPUT_ROW['stocks_ducks_1000_head'] * 1000

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_duck_tonnes']
        prod_milk = 0
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_duck_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_duck_slcpertonne']
        price_milk_lcu = 999.999
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_duck_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_duck_usdpertonne']
        price_milk_usd = 999.999
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'GOATS':
        stocks_hd = INPUT_ROW['stocks_goats_head']

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_goat_tonnes']
        prod_milk = INPUT_ROW['production_milk_whole_fresh_goat_tonnes']
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_goat_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_goat_slcpertonne']
        price_milk_lcu = INPUT_ROW['producer_price_milk_whole_fresh_goat_slcpertonne']
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_goat_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_goat_usdpertonne']
        price_milk_usd = INPUT_ROW['producer_price_milk_whole_fresh_goat_usdpertonne']
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'HORSES':
        stocks_hd = INPUT_ROW['stocks_horses_head']

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_horse_tonnes']
        prod_milk = 0
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_horse_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_horse_slcpertonne']
        price_milk_lcu = 999.999
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_horse_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_horse_usdpertonne']
        price_milk_usd = 999.999
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'PIGS':
        stocks_hd = INPUT_ROW['stocks_pigs_head']

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_pig_tonnes']
        prod_milk = 0
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_pig_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_pig_slcpertonne']
        price_milk_lcu = 999.999
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_pig_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_pig_usdpertonne']
        price_milk_usd = 999.999
        price_wool_usd = 999.999
    elif INPUT_ROW['species'].upper() == 'SHEEP':
        stocks_hd = INPUT_ROW['stocks_sheep_head']

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_sheep_tonnes']
        prod_milk = INPUT_ROW['production_milk_whole_fresh_sheep_tonnes']
        prod_wool = INPUT_ROW['production_wool_greasy_tonnes']

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_sheep_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_sheep_slcpertonne']
        price_milk_lcu = INPUT_ROW['producer_price_milk_whole_fresh_sheep_slcpertonne']
        price_wool_lcu = INPUT_ROW['producer_price_wool_greasy_slcpertonne']

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_sheep_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_sheep_usdpertonne']
        price_milk_usd = INPUT_ROW['producer_price_milk_whole_fresh_sheep_usdpertonne']
        price_wool_usd = INPUT_ROW['producer_price_wool_greasy_usdpertonne']
    elif INPUT_ROW['species'].upper() == 'TURKEYS':
        stocks_hd = INPUT_ROW['stocks_turkeys_1000_head'] * 1000

        prod_eggs = 0
        prod_hides = 0
        prod_meat = INPUT_ROW['production_meat_turkey_tonnes']
        prod_milk = 0
        prod_wool = 0

        price_eggs_lcu = 999.999
        price_meat_lcu = INPUT_ROW['producer_price_meat_turkey_slcpertonne']
        price_meat_live_lcu = INPUT_ROW['producer_price_meat_livewt_turkey_slcpertonne']
        price_milk_lcu = 999.999
        price_wool_lcu = 999.999

        price_eggs_usd = 999.999
        price_meat_usd = INPUT_ROW['producer_price_meat_turkey_usdpertonne']
        price_meat_live_usd = INPUT_ROW['producer_price_meat_livewt_turkey_usdpertonne']
        price_milk_usd = 999.999
        price_wool_usd = 999.999
    else:
        stocks_hd = np.nan

        prod_eggs = np.nan
        prod_hides = np.nan
        prod_meat = np.nan
        prod_milk = np.nan
        prod_wool = np.nan

        price_eggs_lcu = np.nan
        price_meat_lcu = np.nan
        price_meat_live_lcu = np.nan
        price_milk_lcu = np.nan
        price_wool_lcu = np.nan

        price_eggs_usd = np.nan
        price_meat_usd = np.nan
        price_meat_live_usd = np.nan
        price_milk_usd = np.nan
        price_wool_usd = np.nan
    return pd.Series([stocks_hd
                     ,prod_eggs ,prod_hides ,prod_meat ,prod_milk ,prod_wool
                     ,price_eggs_lcu ,price_meat_lcu ,price_meat_live_lcu ,price_milk_lcu ,price_wool_lcu
                     ,price_eggs_usd ,price_meat_usd ,price_meat_live_usd ,price_milk_usd ,price_wool_usd
                     ])
world_ahle_combo1[[
    'stocksKEEP_hd'

    ,'productionKEEP_eggs_tonnes'
    ,'productionKEEP_hides_tonnes'
    ,'productionKEEP_meat_tonnes'
    ,'productionKEEP_milk_tonnes'
    ,'productionKEEP_wool_tonnes'

    ,'producer_priceKEEP_eggs_lcupertonne'
    ,'producer_priceKEEP_meat_lcupertonne'
    ,'producer_priceKEEP_meat_live_lcupertonne'
    ,'producer_priceKEEP_milk_lcupertonne'
    ,'producer_priceKEEP_wool_lcupertonne'

    ,'producer_priceKEEP_eggs_usdpertonne'
    ,'producer_priceKEEP_meat_usdpertonne'
    ,'producer_priceKEEP_meat_live_usdpertonne'
    ,'producer_priceKEEP_milk_usdpertonne'
    ,'producer_priceKEEP_wool_usdpertonne'
    ]] = world_ahle_combo1.apply(assign_columns_to_species ,axis=1)

# Drop species-specific columns
orig_stocks_cols = [i for i in list(world_ahle_combo1) if 'stocks_' in i]
orig_production_cols = [i for i in list(world_ahle_combo1) if 'production_' in i]
orig_price_cols = [i for i in list(world_ahle_combo1) if 'producer_price_' in i]
world_ahle_combo1 = world_ahle_combo1.drop(columns=orig_stocks_cols + orig_production_cols + orig_price_cols)

# Remove KEEP flag from new columns
world_ahle_combo1.columns = world_ahle_combo1.columns.str.replace('KEEP' ,'')

datainfo(world_ahle_combo1)

# =============================================================================
# # Not used
# stocks_asses_head
# stocks_beehives_no
# stocks_camelids_other_head
# stocks_geese_and_guinea_fowls_1000_head
# stocks_mules_head
# stocks_pigs_head
# stocks_rabbits_and_hares_1000_head
# stocks_rodents_other_1000_head


# production_meat_game_tonnes
# producer_price_meat_game_slcpertonne

# production_meat_rabbit_tonnes
# producer_price_meat_rabbit_slcpertonne

# production_meat_ass_tonnes
# producer_price_meat_ass_slcpertonne

# production_meat_goose_and_guinea_fowl_tonnes
# producer_price_meat_goose_and_guinea_fowl_slcpertonne

# production_meat_mule_tonnes
# producer_price_meat_mule_slcpertonne

# production_meat_other_camelids_tonnes
# producer_price_meat_other_camelids_slcpertonne

# production_meat_other_rodents_tonnes
# =============================================================================

# =============================================================================
#### Describe and output
# =============================================================================
world_ahle_combo1.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_combo1.csv'))
world_ahle_combo1.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_combo1.pkl.gz'))
