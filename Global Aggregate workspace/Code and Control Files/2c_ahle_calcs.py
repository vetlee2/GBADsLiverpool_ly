#%% About
'''
'''
#%% Read data

world_ahle_imp = pd.read_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_2_imputed.pkl.gz'))

# Remove intermediate columns used in imputation
wtavg_cols = [i for i in list(world_ahle_imp) if '_wtavg' in i]
median_cols = [i for i in list(world_ahle_imp) if '_median' in i]
intermed_price_cols = [i for i in list(world_ahle_imp) if 'pertonne_2010' in i]
intermed_price_cols2 = [i for i in list(world_ahle_imp) if 'pertonne_growth' in i]
raw_cols = [i for i in list(world_ahle_imp) if '_raw' in i]

dropcols = wtavg_cols + median_cols + intermed_price_cols + intermed_price_cols2 + raw_cols
world_ahle_abt = world_ahle_imp.drop(columns=dropcols ,errors='ignore')

datainfo(world_ahle_abt)

#%% Add mortality and other rates
'''
Currently using the same rates for all species.
'''

# =============================================================================
#### Mortality and morbidity
# =============================================================================
mortality_byincome = {
    "L":0.15
    ,"LM":0.1
    ,"UM":0.06
    ,"H":0.04
}
morbidity_byincome = {
    "L":0.15
    ,"LM":0.15
    ,"UM":0.15
    ,"H":0.15
}

world_ahle_abt['mortality_rate'] = world_ahle_abt['incomegroup'].apply(lookup_from_dictionary ,DICT=mortality_byincome)
world_ahle_abt['morbidity_rate'] = world_ahle_abt['incomegroup'].apply(lookup_from_dictionary ,DICT=morbidity_byincome)

# =============================================================================
#### Expenditures
# =============================================================================
# Currently the same for all products
# Spend per kg biomass
farmspend_perkg_biomass_byincome = {
    "L":0.01
    ,"LM":0.02
    ,"UM":0.03
    ,"H":0.05
}
pubspend_perkg_biomass_byincome = {
    "L":0.005
    ,"LM":0.01
    ,"UM":0.02
    ,"H":0.03
}
world_ahle_abt['vetspend_biomass_farm_usdperkgbm'] = \
    world_ahle_abt['incomegroup'].apply(lookup_from_dictionary ,DICT=farmspend_perkg_biomass_byincome)
world_ahle_abt['vetspend_biomass_public_usdperkgbm'] = \
    world_ahle_abt['incomegroup'].apply(lookup_from_dictionary ,DICT=pubspend_perkg_biomass_byincome)

# Spend per kg production
vetspend_perkg_prod_byincome = {
    "L":0.0025
    ,"LM":0.005
    ,"UM":0.01
    ,"H":0.01
}
world_ahle_abt['vetspend_production_usdperkgprod'] = \
    world_ahle_abt['incomegroup'].apply(lookup_from_dictionary ,DICT=vetspend_perkg_prod_byincome)

# =============================================================================
#### Carcass yield
# =============================================================================
# # Not currently used
# carcass_yield_byspecies = {
#     "BUFFALOES":0.75
#     ,"CAMELS":0.75
#     ,"CATTLE":0.75
#     ,"CHICKENS":0.90
#     ,"DUCKS":0.90
#     ,"GOATS":0.75
#     ,"HORSES":0.75
#     ,"PIGS":0.75
#     ,"SHEEP":0.75
#     ,"TURKEYS":0.90
# }
# world_ahle_abt['carcass_yield'] = world_ahle_abt['species'].str.upper().apply(lookup_from_dictionary ,DICT=carcass_yield_byspecies)

datainfo(world_ahle_abt)

#%% AHLE Calcs matching Will's original spreadsheet
'''
See World AHLE.xlsx from William.
'''
# Create a version of data frame for these calcs
world_ahle_abt_simple = world_ahle_abt.copy()

# =============================================================================
#### Calcs
# =============================================================================
# If production is zero, output value should be zero, even if price is missing
_production_zero = (world_ahle_abt_simple['production_eggs_tonnes'] == 0)
world_ahle_abt_simple.loc[_production_zero ,'egg_output_value_2010usd'] = 0
world_ahle_abt_simple.loc[~_production_zero ,'egg_output_value_2010usd'] = \
    world_ahle_abt_simple['production_eggs_tonnes'] * world_ahle_abt_simple['producer_price_eggs_usdpertonne_cnst2010']

_production_zero = (world_ahle_abt_simple['production_meat_tonnes'] == 0)
world_ahle_abt_simple.loc[_production_zero ,'meat_output_value_2010usd'] = 0
world_ahle_abt_simple.loc[~_production_zero ,'meat_output_value_2010usd'] = \
    world_ahle_abt_simple['production_meat_tonnes'] * world_ahle_abt_simple['producer_price_meat_usdpertonne_cnst2010']

_production_zero = (world_ahle_abt_simple['production_milk_tonnes'] == 0)
world_ahle_abt_simple.loc[_production_zero ,'milk_output_value_2010usd'] = 0
world_ahle_abt_simple.loc[~_production_zero ,'milk_output_value_2010usd'] = \
    world_ahle_abt_simple['production_milk_tonnes'] * world_ahle_abt_simple['producer_price_milk_usdpertonne_cnst2010']

world_ahle_abt_simple.eval(
    # ----------------------------------------------------------------------
    # Fundamentals
    # ----------------------------------------------------------------------
    '''
    liveweight_value_2010usd = biomass * producer_price_meat_live_usdpertonne_cnst2010

    total_output_plus_liveweight_value_2010usd = liveweight_value_2010usd + meat_output_value_2010usd \
        + egg_output_value_2010usd + milk_output_value_2010usd

    total_biomass_tonnes = biomass / 1000
    '''
    # ----------------------------------------------------------------------
    # Ideals
    # ----------------------------------------------------------------------
    '''
    ideal_liveweight_value_2010usd = liveweight_value_2010usd * (1 / (1 - mortality_rate))
    ideal_meat_output_value_2010usd = meat_output_value_2010usd * (1 / (1 - morbidity_rate))
    ideal_egg_output_value_2010usd = egg_output_value_2010usd * (1 / (1 - morbidity_rate))
    ideal_milk_output_value_2010usd = milk_output_value_2010usd * (1 / (1 - morbidity_rate))

    ideal_total_output_plus_liveweight_value_2010usd = ideal_liveweight_value_2010usd + ideal_meat_output_value_2010usd \
        + ideal_egg_output_value_2010usd + ideal_milk_output_value_2010usd
    '''
    # ----------------------------------------------------------------------
    # Vet & Med spending
    # ----------------------------------------------------------------------
    '''
    vetspend_biomass_farm_usd = vetspend_biomass_farm_usdperkgbm * total_biomass_tonnes * 1000
    vetspend_biomass_public_usd = vetspend_biomass_public_usdperkgbm * total_biomass_tonnes * 1000

    vetspend_production_meat_usd = vetspend_production_usdperkgprod * production_meat_tonnes * 1000
    vetspend_production_eggs_usd = vetspend_production_usdperkgprod * production_eggs_tonnes * 1000
    vetspend_production_milk_usd = vetspend_production_usdperkgprod * production_milk_tonnes * 1000
    '''
    # ----------------------------------------------------------------------
    # AHLE
    # ----------------------------------------------------------------------
    '''
    ahle_dueto_reducedoutput_2010usd = ideal_total_output_plus_liveweight_value_2010usd - total_output_plus_liveweight_value_2010usd
    ahle_dueto_vetandmedcost_2010usd = vetspend_biomass_farm_usd + vetspend_biomass_public_usd \
        + vetspend_production_eggs_usd + vetspend_production_meat_usd + vetspend_production_milk_usd
    ahle_total_2010usd = ahle_dueto_reducedoutput_2010usd + ahle_dueto_vetandmedcost_2010usd

    ahle_dueto_reducedoutput_pctofvalue = (ahle_dueto_reducedoutput_2010usd / total_output_plus_liveweight_value_2010usd) * 100
    ahle_dueto_vetandmedcost_pctofvalue = (ahle_dueto_vetandmedcost_2010usd / total_output_plus_liveweight_value_2010usd) * 100
    ahle_total_pctofvalue = (ahle_total_2010usd / total_output_plus_liveweight_value_2010usd) * 100
    '''
    ,inplace=True
)

datainfo(world_ahle_abt_simple)

# =============================================================================
#### Output
# =============================================================================
world_ahle_abt_simple.to_csv(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_simple.csv') ,index=False)
world_ahle_abt_simple.to_pickle(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_simple.pkl.gz'))

#%% AHLE Calcs improved
'''
See Animal stock and flow.docx from William.
'''

# =============================================================================
#### Outputs
# =============================================================================
# Excluding hides from value calcs because no price is available
world_ahle_abt.eval(
    '''
    output_live_hd = export_animals_hd + stocks_hd_nextyear
    output_total_hd = output_live_hd + producing_animals_meat_hd

    output_live_biomass_kg = output_live_hd * liveweight
    output_total_biomass_kg = output_total_hd * liveweight

    output_value_live_2010usd = (output_live_biomass_kg / 1000) * producer_price_meat_live_usdpertonne_cnst2010
    output_value_total_2010usd = (output_total_biomass_kg / 1000) * producer_price_meat_live_usdpertonne_cnst2010

    output_value_meat_2010usd = production_meat_tonnes * producer_price_meat_usdpertonne_cnst2010
    output_value_eggs_2010usd = production_eggs_tonnes * producer_price_eggs_usdpertonne_cnst2010
    output_value_milk_2010usd = production_milk_tonnes * producer_price_milk_usdpertonne_cnst2010
    output_value_wool_2010usd = production_wool_tonnes * producer_price_wool_usdpertonne_cnst2010

    output_value_meatlive_2010usd = output_value_meat_2010usd + output_value_live_2010usd
    '''
    ,inplace=True
)

# =============================================================================
#### Inputs and ideal
# =============================================================================
# Calculate births outside eval() so I can round
world_ahle_abt['births_hd'] = (world_ahle_abt['output_total_hd'] / (1 - world_ahle_abt['mortality_rate'])) \
    - (world_ahle_abt['stocks_hd'] + world_ahle_abt['import_animals_hd'])
world_ahle_abt['births_hd'] = round(world_ahle_abt['births_hd'] ,0)

world_ahle_abt.eval(
    # ----------------------------------------------------------------------
    # Inputs
    # ----------------------------------------------------------------------
    '''
    input_live_hd = stocks_hd + import_animals_hd + births_hd
    input_biomass_kg = input_live_hd * liveweight
    input_value_total_2010usd = (input_biomass_kg / 1000) * producer_price_meat_live_usdpertonne_cnst2010

    input_value_producing_eggs_2010usd = producing_animals_eggs_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    input_value_producing_meat_2010usd = producing_animals_meat_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    input_value_producing_milk_2010usd = producing_animals_milk_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    input_value_producing_wool_2010usd = producing_animals_wool_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    '''
    # Calculate productivity as output value per kg biomass
    ## Not used
    # productivity_meatlive_usdperkgbm = output_value_meatlive_2010usd / input_biomass_kg
    # productivity_eggs_usdperkgbm = output_value_eggs_2010usd / input_biomass_kg
    # productivity_meat_usdperkgbm = output_value_meat_2010usd / input_biomass_kg
    # productivity_milk_usdperkgbm = output_value_milk_2010usd / input_biomass_kg
    # productivity_wool_usdperkgbm = output_value_wool_2010usd / input_biomass_kg

    # Alternative productivity divides each product by biomass of its producing animals
    # productivity_eggs_usdperkgbm = output_value_eggs_2010usd / producing_animals_eggs_kgbm
    # productivity_meat_usdperkgbm = output_value_meat_2010usd / producing_animals_meat_kgbm
    # productivity_milk_usdperkgbm = output_value_milk_2010usd / producing_animals_milk_kgbm
    # productivity_wool_usdperkgbm = output_value_wool_2010usd / producing_animals_wool_kgbm

    # ----------------------------------------------------------------------
    # Ideal Mortality
    # ----------------------------------------------------------------------
    # Mortality zero means either:
    # - A. More live animals output, or
    # - B. Fewer input animals needed for same output
    # Under B, input head = output head. If no change in liveweight, then input biomass = output biomass.
    # If no change in liveweight price, then input dollar value = output dollar value.

    # ideal_output_live_hd = output_live_hd * (1 / (1 - mortality_rate))
    # ideal_output_value_live_2010usd = (ideal_output_live_hd * liveweight / 1000) \
    #     * producer_price_meat_live_usdpertonne_cnst2010
    # ideal_output_value_meatlive_2010usd = output_value_meatlive_2010usd  * (1 / (1 - mortality_rate))
    '''
    ideal_mrt_input_live_hd = output_total_hd
    ideal_mrt_input_biomass_kg = ideal_mrt_input_live_hd * liveweight
    ideal_mrt_input_value_2010usd = (ideal_mrt_input_biomass_kg / 1000) * producer_price_meat_live_usdpertonne_cnst2010
    '''

    # ----------------------------------------------------------------------
    # Ideal Morbidity
    # ----------------------------------------------------------------------
    # For meat production, morbidity zero means greater liveweight per animal
    # Get new headcount needed to match current production at higher liveweight
    # Assuming carcass yield doesn't change, this means matching current biomass
    #??? No change in required biomass, so no change in value?
    # ideal_producing_animals_meat_kgbm = producing_animals_meat_kgbm
    # ideal_input_value_producing_meat_2010usd = input_value_producing_meat_2010usd
    '''
    ideal_mbd_liveweight = liveweight * (1 / (1 - morbidity_rate))
    ideal_mbd_producing_animals_meat_hd = producing_animals_meat_kgbm / ideal_mbd_liveweight
    check_ideal_mbd_producing_animals_meat_hd = ideal_mbd_producing_animals_meat_hd / producing_animals_meat_hd
    ideal_mbd_producing_animals_meat_kgbm = producing_animals_meat_kgbm
    ideal_mbd_input_value_producing_meat_2010usd = ideal_mbd_producing_animals_meat_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    '''

    # For other products, morbidity zero means greater production per kg biomass
    # Get new biomass needed to match current production at higher rate
    '''
    ideal_mbd_production_eggs_kgperkgbm = production_eggs_kgperkgbm * (1 / (1 - morbidity_rate))
    ideal_mbd_producing_animals_eggs_kgbm = (production_eggs_tonnes * 1000) / ideal_mbd_production_eggs_kgperkgbm
    check_ideal_mbd_producing_animals_eggs_kgbm = ideal_mbd_producing_animals_eggs_kgbm / producing_animals_eggs_kgbm
    ideal_mbd_input_value_producing_eggs_2010usd = ideal_mbd_producing_animals_eggs_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    check_ideal_mbd_input_value_producing_eggs_2010usd = ideal_mbd_input_value_producing_eggs_2010usd / input_value_producing_eggs_2010usd

    ideal_mbd_production_milk_kgperkgbm = production_milk_kgperkgbm * (1 / (1 - morbidity_rate))
    ideal_mbd_producing_animals_milk_kgbm = (production_milk_tonnes * 1000) / ideal_mbd_production_milk_kgperkgbm
    ideal_mbd_input_value_producing_milk_2010usd = ideal_mbd_producing_animals_milk_kgbm * producer_price_meat_live_usdpertonne_cnst2010

    ideal_mbd_production_wool_kgperkgbm = production_wool_kgperkgbm * (1 / (1 - morbidity_rate))
    ideal_mbd_producing_animals_wool_kgbm = (production_wool_tonnes * 1000) / ideal_mbd_production_wool_kgperkgbm
    ideal_mbd_input_value_producing_wool_2010usd = ideal_mbd_producing_animals_wool_kgbm * producer_price_meat_live_usdpertonne_cnst2010
    '''

    # ----------------------------------------------------------------------
    # Vet & Med spending
    # ----------------------------------------------------------------------
    '''
    vetspend_biomass_farm_usd = vetspend_biomass_farm_usdperkgbm * input_biomass_kg
    vetspend_biomass_public_usd = vetspend_biomass_public_usdperkgbm * input_biomass_kg
    '''
    # Update: now that we're calculating biomass for the whole year, don't need to separately apply
    # vet & med rates to production.
    # vetspend_production_eggs_usd = vetspend_production_usdperkgprod * production_eggs_tonnes * 1000
    # vetspend_production_meat_usd = vetspend_production_usdperkgprod * production_meat_tonnes * 1000
    # vetspend_production_milk_usd = vetspend_production_usdperkgprod * production_milk_tonnes * 1000
    # vetspend_production_wool_usd = vetspend_production_usdperkgprod * production_wool_tonnes * 1000
    ,inplace=True
)

world_ahle_abt_head = world_ahle_abt.head(100)
datainfo(world_ahle_abt)

#%% Data checks

# =============================================================================
#### Misc checks
# =============================================================================
world_ahle_abt_chk = world_ahle_abt.copy()

# Check sum of producing animals for each product and compare to
# total head calculated from imports, stocks, and births.
# Excluding producing_animals_hides_hd because this is always equal to producing_animals_meat_hd
# Sum of producing animals is less than total head calculated from imports, stocks, and births.
world_ahle_abt_chk.eval(
    '''
    producing_animals_sum = producing_animals_eggs_hd + producing_animals_meat_hd + \
        producing_animals_milk_hd + producing_animals_wool_hd
    producing_animals_sum_over_input_live_hd = producing_animals_sum / input_live_hd
    '''
    ,inplace=True
)
world_ahle_abt_chk['producing_animals_sum_over_input_live_hd'].describe()

world_ahle_abt_chk_spl = world_ahle_abt_chk.sample(n=100)

# =============================================================================
#### Distribution by country and species
# =============================================================================
vars_for_distributions = [
    'output_value_meatlive_2010usd'
    ,'output_value_eggs_2010usd'
    ,'output_value_milk_2010usd'
    ,'output_value_wool_2010usd'

    # ,'ideal_output_value_meatlive_2010usd'
    # ,'ideal_output_value_eggs_2010usd'
    # ,'ideal_output_value_milk_2010usd'
    # ,'ideal_output_value_wool_2010usd'
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
    try:    # If raw variable exists
        df_desc = world_ahle_abt.groupby(['country' ,'species'])[f"{VAR}_raw"].describe()
        df_desc = indextocolumns(df_desc)
        df_desc['variable'] = f"{VAR}_raw"
        df_desc_aslist = df_desc.to_dict(orient='records')
        dist_bycountryspecies_aslist.extend(df_desc_aslist)
    except:
        None

dist_bycountryspecies = pd.DataFrame.from_dict(dist_bycountryspecies_aslist ,orient='columns')
del dist_bycountryspecies_aslist

# Reorder columns
cols_first = ['country' ,'species' ,'variable']
cols_other = [i for i in list(dist_bycountryspecies) if i not in cols_first]
dist_bycountryspecies = dist_bycountryspecies.reindex(columns=cols_first + cols_other)

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
plotvars = [
    'output_value_meatlive_2010usd'
    ,'output_value_eggs_2010usd'
    ,'output_value_milk_2010usd'
    ,'output_value_wool_2010usd'

    # ,'ideal_output_value_meatlive_2010usd'
    # ,'ideal_output_value_eggs_2010usd'
    # ,'ideal_output_value_milk_2010usd'
    # ,'ideal_output_value_wool_2010usd'
]
# for VAR in plotvars:
#     snplt = sns.catplot(
#         data=world_ahle_abt
#         ,x='species'
#         ,y=VAR
#         ,kind='box'
#         ,orient='v'
#     )

# Plot over time for each species and country

# =============================================================================
#### Export
# =============================================================================
dist_bycountryspecies.to_csv(os.path.join(PROGRAM_OUTPUT_FOLDER ,'check_distributions_ahlecalcs.csv') ,index=False)

#%% Cleanup and output

# =============================================================================
#### Cleanup
# =============================================================================
datainfo(world_ahle_abt)

# =============================================================================
#### Export
# =============================================================================
world_ahle_abt.to_csv(os.path.join(FINDATA_FOLDER ,'world_ahle_abt.csv') ,index=False)
world_ahle_abt.to_pickle(os.path.join(FINDATA_FOLDER ,'world_ahle_abt.pkl.gz'))
