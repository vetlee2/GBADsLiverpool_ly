#%% About
'''
'''
#%% Extend biomass data
'''
Biomass table from GBADSKE only has data to 2017. Extend with FAOstat population data to 2020.
UPDATE JAN. 2023: This is not longer necessary because Informatics has provided an updated
biomass table with data through 2020.
'''
# biomass = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))

# # -----------------------------------------------------------------------------
# # Create rows for additional years
# # -----------------------------------------------------------------------------
# # Get country*species combos from biomass data
# biomass_country_spec_combos = pd.DataFrame(biomass[['iso3' ,'country' ,'species']].value_counts())
# biomass_country_spec_combos = indextocolumns(biomass_country_spec_combos)
# biomass_country_spec_combos['identity'] = 1     # Add constant column for merging

# # Create full list of desired years
# extend_years = pd.DataFrame({'year':range(2000 ,2021) ,'identity':1})

# # Create dummy data with all desired countries, species, and years
# extended_data = pd.merge(
#     left=biomass_country_spec_combos
#     ,right=extend_years
#     ,on='identity'
#     ,how='outer'
# )

# # Merge dummy data with biomass
# biomass_extended = pd.merge(
#     left=biomass
#     ,right=extended_data[['iso3' ,'country' ,'species' ,'year']]
#     ,on=['iso3' ,'country' ,'species' ,'year']
#     ,how='right'    # Keep all rows from extended data
# )

biomass_extended = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'biomass_live_weight_fao.pkl.gz'))

#%% Merge

# =============================================================================
#### Prep UN Geo codes
# =============================================================================
un_geo_codes = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'un_geo_codes.pkl.gz'))

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

biomass_iso_countries = list(biomass_iso['country'].unique())
biomass_iso_missing = biomass_iso.query("country_iso3.isnull()")

# =============================================================================
#### Prep FAO tables
# =============================================================================
fao_production_p = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'fao_production.pkl.gz'))
fao_producerprice_p = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'fao_producerprice.pkl.gz'))
fao_impexp_p = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'fao_impexp_p.pkl.gz'))

# Combine FAO production and price tables
fao_combo = pd.merge(
    left=fao_production_p
    ,right=fao_producerprice_p
    ,on=['country' ,'year']
    ,how='outer'
    ,indicator='_merge_fao'
    )
fao_combo['_merge_fao'].value_counts()
fao_country_merge_status = fao_combo[['country' ,'_merge_fao']].value_counts()

# Combine FAO import/export table
fao_combo = pd.merge(
    left=fao_combo
    ,right=fao_impexp_p
    ,on=['country_code_iso3_' ,'country' ,'year']
    ,how='outer'
    ,indicator='_merge_fao2'
    )
fao_combo['_merge_fao2'].value_counts()

countries_fao = list(fao_combo['country'].unique())

# =============================================================================
# # No longer needed because FAO data has iso3 codes
# # Reconcile country names with UN Geo Codes
# recode_countries = {
#     "China":"China"
#     ,"China, Hong Kong SAR":"Hong Kong"
#     # ,"China, Macao SAR":""
#     ,"China, Taiwan Province of":"Taiwan, Province of China"
#     # ,"China, mainland":""
#     ,"Sudan (former)":"Sudan"
# }
# fao_combo['country'] = fao_combo['country'].replace(recode_countries)

# # Add country iso code
# fao_combo_iso = pd.merge(
#     left=fao_combo
#     ,right=un_geo_codes_tomatch
#     ,on='country'
#     ,how='left'
#     )
# =============================================================================

fao_combo_iso = fao_combo.copy()
fao_combo_iso = fao_combo_iso.rename(columns={'country_code_iso3_':'country_iso3'})

datainfo(fao_combo_iso)

# =============================================================================
#### Prep World Bank tables
# =============================================================================
# Income groups
wb_income = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'wb_income.pkl.gz'))

# Regions
wb_region = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'wb_region.pkl.gz'))

# Inflation and Exchange rates
wb_infl_exchg = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'wb_infl_exchg.pkl.gz'))

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
#### Merge all
# =============================================================================
# World Bank onto Biomass
world_ahle_combined = pd.merge(
    left=biomass_iso
    ,right=wb_combo
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_1'
    )
world_ahle_combined['_merge_1'].value_counts()

# FAO
world_ahle_combined = pd.merge(
    left=world_ahle_combined
    ,right=fao_combo_iso
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_2'
    )
world_ahle_combined['_merge_2'].value_counts()

# Drop and Rename
world_ahle_combined = world_ahle_combined.drop(columns=[
    'country'
    ,'country_y'
    ,'time_code'
    ,'_merge_fao'
    ,'_merge_fao2'
    ,'_merge_1'
    ,'flag_y'
    ,'_merge_wb_1'
    ,'_merge_wb_2'
    ,'_merge_2'
    ]
    ,errors='ignore')
world_ahle_combined = world_ahle_combined.rename(columns={'country_x':'country' ,'flag_x':'flag_biomass' ,'flag_y':'flag_wb'})

datainfo(world_ahle_combined)

# =============================================================================
#### Checks
# =============================================================================
# Missing iso3?
missing_iso3 = world_ahle_combined.query("country_iso3.isnull()")
missing_iso3_countries = list(missing_iso3['country'].unique())

#%% Assign columns to correct species

species_list = list(world_ahle_combined['species'].unique())

fao_price_cols = [i for i in list(fao_producerprice_p) if 'producer_price' in i]
fao_stocks_cols = [i for i in list(fao_production_p) if 'stocks' in i]
fao_production_cols = [i for i in list(fao_production_p) if 'production' in i]

fao_producinganimals_cols = [i for i in list(fao_production_p) if 'producing' in i]
fao_producinganimals_cols += [i for i in list(fao_production_p) if 'laying' in i]
fao_producinganimals_cols += [i for i in list(fao_production_p) if 'milk' in i]
fao_producinganimals_cols += [i for i in list(fao_production_p) if 'prod_pop' in i]

fao_impexp_cols = [i for i in list(world_ahle_combined) if 'import' in i]
fao_impexp_cols += [i for i in list(world_ahle_combined) if 'export' in i]

# For items that don't apply to a species:
# - Set production to zero
# - Set prices to a coded value (999.999)
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

        prod_animals_eggs = 0
        prod_animals_hides = INPUT_ROW['producing_animals_slaughtered_hides_buffalo_fresh_head']
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_buffalo_head']
        prod_animals_milk = INPUT_ROW['milk_animals_milk_whole_fresh_buffalo_head']
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_buffaloes_head']
        export_animals_hd = INPUT_ROW['export_quantity_buffaloes_head']

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_camel_head']
        prod_animals_milk = INPUT_ROW['milk_animals_milk_whole_fresh_camel_head']
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_camels_head']
        export_animals_hd = INPUT_ROW['export_quantity_camels_head']

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

        prod_animals_eggs = 0
        prod_animals_hides = INPUT_ROW['producing_animals_slaughtered_hides_cattle_fresh_head']
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_cattle_head']
        prod_animals_milk = INPUT_ROW['milk_animals_milk_whole_fresh_cow_head']
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_cattle_head']
        export_animals_hd = INPUT_ROW['export_quantity_cattle_head']

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

        prod_animals_eggs = INPUT_ROW['laying_eggs_hen_in_shell_1000_head'] * 1000
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_chicken_1000_head'] * 1000
        prod_animals_milk = 0
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_chickens_1000_head'] * 1000
        export_animals_hd = INPUT_ROW['export_quantity_chickens_1000_head'] * 1000

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_duck_1000_head'] * 1000
        prod_animals_milk = 0
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_ducks_1000_head'] * 1000
        export_animals_hd = INPUT_ROW['export_quantity_ducks_1000_head'] * 1000

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_goat_head']
        prod_animals_milk = INPUT_ROW['milk_animals_milk_whole_fresh_goat_head']
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_goats_head']
        export_animals_hd = INPUT_ROW['export_quantity_goats_head']

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_horse_head']
        prod_animals_milk = 0
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_horses_head']
        export_animals_hd = INPUT_ROW['export_quantity_horses_head']

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_pig_head']
        prod_animals_milk = 0
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_pigs_head']
        export_animals_hd = INPUT_ROW['export_quantity_pigs_head']

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_sheep_head']
        prod_animals_milk = INPUT_ROW['milk_animals_milk_whole_fresh_sheep_head']
        prod_animals_wool = 999      # Not available in FAOstat

        import_animals_hd = INPUT_ROW['import_quantity_sheep_head']
        export_animals_hd = INPUT_ROW['export_quantity_sheep_head']

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

        prod_animals_eggs = 0
        prod_animals_hides = 0
        prod_animals_meat = INPUT_ROW['producing_animals_slaughtered_meat_turkey_1000_head'] * 1000
        prod_animals_milk = 0
        prod_animals_wool = 0

        import_animals_hd = INPUT_ROW['import_quantity_turkeys_1000_head'] * 1000
        export_animals_hd = INPUT_ROW['export_quantity_turkeys_1000_head'] * 1000

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

        prod_animals_eggs = np.nan
        prod_animals_hides = np.nan
        prod_animals_meat = np.nan
        prod_animals_milk = np.nan
        prod_animals_wool = np.nan

        import_animals_hd = np.nan
        export_animals_hd = np.nan

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
                     ,prod_animals_eggs ,prod_animals_hides ,prod_animals_meat ,prod_animals_milk ,prod_animals_wool
                     ,import_animals_hd ,export_animals_hd
                     ,price_eggs_lcu ,price_meat_lcu ,price_meat_live_lcu ,price_milk_lcu ,price_wool_lcu
                     ,price_eggs_usd ,price_meat_usd ,price_meat_live_usd ,price_milk_usd ,price_wool_usd
                     ])
world_ahle_combined[[
    'stocks_hd'

    ,'production_eggs_tonnes'
    ,'production_hides_tonnes'
    ,'production_meat_tonnes'
    ,'production_milk_tonnes'
    ,'production_wool_tonnes'

    ,'producing_animals_eggs_hd'
    ,'producing_animals_hides_hd'
    ,'producing_animals_meat_hd'
    ,'producing_animals_milk_hd'
    ,'producing_animals_wool_hd'

    ,'import_animals_hd'
    ,'export_animals_hd'

    ,'producer_price_eggs_lcupertonne'
    ,'producer_price_meat_lcupertonne'
    ,'producer_price_meat_live_lcupertonne'
    ,'producer_price_milk_lcupertonne'
    ,'producer_price_wool_lcupertonne'

    ,'producer_price_eggs_usdpertonne'
    ,'producer_price_meat_usdpertonne'
    ,'producer_price_meat_live_usdpertonne'
    ,'producer_price_milk_usdpertonne'
    ,'producer_price_wool_usdpertonne'
    ]] = world_ahle_combined.apply(assign_columns_to_species ,axis=1)

# Drop species-specific columns
dropcols = fao_stocks_cols + fao_production_cols + fao_producinganimals_cols + fao_price_cols + fao_impexp_cols
world_ahle_combined = world_ahle_combined.drop(columns=dropcols ,errors='ignore')

datainfo(world_ahle_combined)

# =============================================================================
#### Checks
# =============================================================================
# Missing import/export?
missing_imp = world_ahle_combined.query("import_animals_hd.isnull()")
missing_imp_countries = missing_imp['country'].value_counts()

missing_exp = world_ahle_combined.query("export_animals_hd.isnull()")
missing_exp_countries = missing_exp['country'].value_counts()

# =============================================================================
#### Describe and output
# =============================================================================
world_ahle_combined.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_1_combined.csv') ,index=False)
world_ahle_combined.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_1_combined.pkl.gz'))
