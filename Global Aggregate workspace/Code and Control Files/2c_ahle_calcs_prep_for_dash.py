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

#%% Calculate values of production

# =============================================================================
#### Indiviudal products
# =============================================================================
# Excluding hides from value calcs because no price is available
# If production is zero, output value should be zero, even if price is missing
_production_zero = (world_ahle_abt['production_eggs_tonnes'] == 0)
world_ahle_abt.loc[_production_zero ,'output_value_eggs_2010usd'] = 0
world_ahle_abt.loc[~_production_zero ,'output_value_eggs_2010usd'] = \
    world_ahle_abt['production_eggs_tonnes'] * world_ahle_abt['producer_price_eggs_usdpertonne_cnst2010']

_production_zero = (world_ahle_abt['production_meat_tonnes'] == 0)
world_ahle_abt.loc[_production_zero ,'output_value_meat_2010usd'] = 0
world_ahle_abt.loc[~_production_zero ,'output_value_meat_2010usd'] = \
    world_ahle_abt['production_meat_tonnes'] * world_ahle_abt['producer_price_meat_usdpertonne_cnst2010']

_production_zero = (world_ahle_abt['production_milk_tonnes'] == 0)
world_ahle_abt.loc[_production_zero ,'output_value_milk_2010usd'] = 0
world_ahle_abt.loc[~_production_zero ,'output_value_milk_2010usd'] = \
    world_ahle_abt['production_milk_tonnes'] * world_ahle_abt['producer_price_milk_usdpertonne_cnst2010']

_production_zero = (world_ahle_abt['production_wool_tonnes'] == 0)
world_ahle_abt.loc[_production_zero ,'output_value_wool_2010usd'] = 0
world_ahle_abt.loc[~_production_zero ,'output_value_wool_2010usd'] = \
    world_ahle_abt['production_wool_tonnes'] * world_ahle_abt['producer_price_wool_usdpertonne_cnst2010']

world_ahle_abt['biomass_value_2010usd'] = (world_ahle_abt['biomass'] / 1000) \
    * world_ahle_abt['producer_price_meat_live_usdpertonne_cnst2010']

# If any output values are missing, fill with zero
fill_cols = [
    'output_value_eggs_2010usd'
    ,'output_value_meat_2010usd'
    ,'output_value_milk_2010usd'
    ,'output_value_wool_2010usd'
    ,'biomass_value_2010usd'
    ]
for COL in fill_cols:
    world_ahle_abt[COL] = world_ahle_abt[COL].replace(np.nan ,0)

# =============================================================================
#### Biomass
# =============================================================================
world_ahle_abt.eval(
    # Using snapshot biomass value
    '''
    output_plus_biomass_value_2010usd = biomass_value_2010usd + output_value_meat_2010usd \
        + output_value_eggs_2010usd + output_value_milk_2010usd + output_value_wool_2010usd
    '''
    # Using total animals for the year
    '''
    output_live_hd = export_animals_hd + stocks_hd_nextyear
    output_total_hd = output_live_hd + producing_animals_meat_hd

    output_live_biomass_kg = output_live_hd * liveweight
    output_total_biomass_kg = output_total_hd * liveweight

    output_value_live_2010usd = (output_live_biomass_kg / 1000) * producer_price_meat_live_usdpertonne_cnst2010
    output_value_total_2010usd = (output_total_biomass_kg / 1000) * producer_price_meat_live_usdpertonne_cnst2010
    output_value_meatlive_2010usd = output_value_meat_2010usd + output_value_live_2010usd
    '''
    ,inplace=True
)

datainfo(world_ahle_abt)

# =============================================================================
#### Export
# =============================================================================
world_ahle_abt.to_csv(os.path.join(FINDATA_FOLDER ,'world_ahle_abt.csv') ,index=False)
world_ahle_abt.to_pickle(os.path.join(FINDATA_FOLDER ,'world_ahle_abt.pkl.gz'))

#%% Output table to feed Dash
'''
The remainder of this program performs calculations that we want to update in Dash
based on user input. Dash will read the data without these calcs and then update them
using functions defined in the dash app.
'''
# =============================================================================
#### Drop unnecessary columns
# =============================================================================
dropcols = [
    'flag_biomass'

    ,'cpi_2010idx'
    ,'inflation_pct_gdpdef'
    ,'inflation_pct_gdpdef_lnk'
    ,'inflation_pct_cp'
    ,'exchg_lcuperusd'

    ,'stocks_hd'
    ,'import_animals_hd'
    ,'export_animals_hd'
    ,'net_imports_hd'
    ,'stocks_hd_nextyear'
    ,'netchange_stocks_hd'

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

    ,'producer_price_eggs_lcupertonne_cnst2010'
    ,'producer_price_meat_lcupertonne_cnst2010'
    ,'producer_price_meat_live_lcupertonne_cnst2010'
    ,'producer_price_milk_lcupertonne_cnst2010'
    ,'producer_price_wool_lcupertonne_cnst2010'
]

# =============================================================================
#### Drop problematic rows
# =============================================================================
droprows = (world_ahle_abt['country'].str.upper() == 'FRENCH GUIANA') \
    | (world_ahle_abt['country'].str.upper() == 'GUADELOUPUE') \
        | (world_ahle_abt['country'].str.upper() == 'MARTINIQUE') \
            | (world_ahle_abt['country'].str.upper() == 'BRUNEI DARUSSALAM')

world_ahle_abt_fordash = world_ahle_abt.loc[~ droprows].drop(columns=dropcols ,errors='ignore')
datainfo(world_ahle_abt_fordash)

# =============================================================================
#### Export
# =============================================================================
world_ahle_abt_fordash.to_csv(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_fordash.csv') ,index=False)
world_ahle_abt_fordash.to_pickle(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_fordash.pkl.gz'))

#%% Add mortality and other rates
'''
Currently using the same rates for all species.
'''

# =============================================================================
#### Create copy of data for further calcs
# =============================================================================
world_ahle_abt_withcalcs = world_ahle_abt.copy()

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

world_ahle_abt_withcalcs['mortality_rate'] = world_ahle_abt_withcalcs['incomegroup'].apply(lookup_from_dictionary ,DICT=mortality_byincome)
world_ahle_abt_withcalcs['morbidity_rate'] = world_ahle_abt_withcalcs['incomegroup'].apply(lookup_from_dictionary ,DICT=morbidity_byincome)

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
world_ahle_abt_withcalcs['vetspend_biomass_farm_usdperkgbm'] = \
    world_ahle_abt_withcalcs['incomegroup'].apply(lookup_from_dictionary ,DICT=farmspend_perkg_biomass_byincome)
world_ahle_abt_withcalcs['vetspend_biomass_public_usdperkgbm'] = \
    world_ahle_abt_withcalcs['incomegroup'].apply(lookup_from_dictionary ,DICT=pubspend_perkg_biomass_byincome)

# Spend per kg production
vetspend_perkg_prod_byincome = {
    "L":0.0025
    ,"LM":0.005
    ,"UM":0.01
    ,"H":0.01
}
world_ahle_abt_withcalcs['vetspend_production_usdperkgprod'] = \
    world_ahle_abt_withcalcs['incomegroup'].apply(lookup_from_dictionary ,DICT=vetspend_perkg_prod_byincome)

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
# world_ahle_abt_withcalcs['carcass_yield'] = world_ahle_abt_withcalcs['species'].str.upper().apply(lookup_from_dictionary ,DICT=carcass_yield_byspecies)

datainfo(world_ahle_abt_withcalcs)

#%% AHLE calcs adjusting outputs
'''
These center on adjusting OUTPUTS under ideal conditions and match the original spreadsheet
produced by William. See World AHLE.xlsx.
'''
# =============================================================================
#### Calcs
# =============================================================================
world_ahle_abt_withcalcs.eval(
    # ----------------------------------------------------------------------
    # Ideals
    # ----------------------------------------------------------------------
    '''
    ideal_biomass_value_2010usd = biomass_value_2010usd * (1 / (1 - mortality_rate))
    ideal_output_value_eggs_2010usd = output_value_eggs_2010usd * (1 / (1 - morbidity_rate))
    ideal_output_value_meat_2010usd = output_value_meat_2010usd * (1 / (1 - morbidity_rate))
    ideal_output_value_milk_2010usd = output_value_milk_2010usd * (1 / (1 - morbidity_rate))
    ideal_output_value_wool_2010usd = output_value_wool_2010usd * (1 / (1 - morbidity_rate))
    '''
    # ----------------------------------------------------------------------
    # Vet & Med spending
    # ----------------------------------------------------------------------
    '''
    vetspend_biomass_farm_usd = vetspend_biomass_farm_usdperkgbm * (biomass / 1000) * 1000
    vetspend_biomass_public_usd = vetspend_biomass_public_usdperkgbm * (biomass / 1000) * 1000

    vetspend_production_meat_usd = vetspend_production_usdperkgprod * production_meat_tonnes * 1000
    vetspend_production_eggs_usd = vetspend_production_usdperkgprod * production_eggs_tonnes * 1000
    vetspend_production_milk_usd = vetspend_production_usdperkgprod * production_milk_tonnes * 1000
    vetspend_production_wool_usd = vetspend_production_usdperkgprod * production_wool_tonnes * 1000
    '''
    ,inplace=True
)
# If any expenditure values are missing, fill with zero
fill_cols = [
    'ideal_biomass_value_2010usd'
    ,'ideal_output_value_eggs_2010usd'
    ,'ideal_output_value_meat_2010usd'
    ,'ideal_output_value_milk_2010usd'
    ,'ideal_output_value_wool_2010usd'

    ,'vetspend_biomass_farm_usd'
    ,'vetspend_biomass_public_usd'
    ,'vetspend_production_meat_usd'
    ,'vetspend_production_eggs_usd'
    ,'vetspend_production_milk_usd'
    ,'vetspend_production_wool_usd'
    ]
for COL in fill_cols:
    world_ahle_abt_withcalcs[COL] = world_ahle_abt_withcalcs[COL].replace(np.nan ,0)

world_ahle_abt_withcalcs.eval(
    '''
    vetspend_farm_usd = vetspend_biomass_farm_usd + vetspend_production_meat_usd \
        + vetspend_production_eggs_usd + vetspend_production_milk_usd + vetspend_production_wool_usd
    vetspend_public_usd = vetspend_biomass_public_usd
    net_value_2010usd = output_plus_biomass_value_2010usd - vetspend_farm_usd - vetspend_public_usd

    ideal_output_plus_biomass_value_2010usd = ideal_biomass_value_2010usd + ideal_output_value_meat_2010usd \
        + ideal_output_value_eggs_2010usd + ideal_output_value_milk_2010usd + ideal_output_value_wool_2010usd
    '''
    # ----------------------------------------------------------------------
    # AHLE
    # ----------------------------------------------------------------------
    '''
    ahle_dueto_reducedoutput_2010usd = ideal_output_plus_biomass_value_2010usd - output_plus_biomass_value_2010usd
    ahle_dueto_vetandmedcost_2010usd = vetspend_farm_usd + vetspend_public_usd
    ahle_total_2010usd = ahle_dueto_reducedoutput_2010usd + ahle_dueto_vetandmedcost_2010usd

    ahle_dueto_reducedoutput_pctofoutput = (ahle_dueto_reducedoutput_2010usd / output_plus_biomass_value_2010usd) * 100
    ahle_dueto_vetandmedcost_pctofoutput = (ahle_dueto_vetandmedcost_2010usd / output_plus_biomass_value_2010usd) * 100
    ahle_total_pctofoutput = (ahle_total_2010usd / output_plus_biomass_value_2010usd) * 100
    '''
    ,inplace=True
)

datainfo(world_ahle_abt_withcalcs)

# =============================================================================
#### Output
# =============================================================================
world_ahle_abt_withcalcs.to_csv(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_withcalcs.csv') ,index=False)
world_ahle_abt_withcalcs.to_pickle(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_withcalcs.pkl.gz'))

#%% AHLE calcs adjusting inputs
'''
These center on adjusting INPUTS under ideal conditions. See Animal stock and flow.docx from William.
'''
# =============================================================================
#### Calcs
# =============================================================================
# Calculate births outside eval() so I can round
world_ahle_abt_withcalcs['births_hd'] = (world_ahle_abt_withcalcs['output_total_hd'] / (1 - world_ahle_abt_withcalcs['mortality_rate'])) \
    - (world_ahle_abt_withcalcs['stocks_hd'] + world_ahle_abt_withcalcs['import_animals_hd'])
world_ahle_abt_withcalcs['births_hd'] = round(world_ahle_abt_withcalcs['births_hd'] ,0)

world_ahle_abt_withcalcs.eval(
    # ----------------------------------------------------------------------
    # Input values
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
    # # Calculate productivity as output value per kg biomass
    # # Not used
    # productivity_meatlive_usdperkgbm = output_value_meatlive_2010usd / input_biomass_kg
    # productivity_eggs_usdperkgbm = output_value_eggs_2010usd / input_biomass_kg
    # productivity_meat_usdperkgbm = output_value_meat_2010usd / input_biomass_kg
    # productivity_milk_usdperkgbm = output_value_milk_2010usd / input_biomass_kg
    # productivity_wool_usdperkgbm = output_value_wool_2010usd / input_biomass_kg

    # # Alternative productivity divides each product by biomass of its producing animals
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

    # Note: production (kg) = animals (head) * liveweight (kg per head) * productivity (kg per kg biomass)
    # Mortality rate impacts animals (head)
    # Morbidity impacts EITHER liveweight or productivity. We don't have to distinguish, because the result will
    # be the same (all multiplicative).

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
    vetspend_farm_usd = vetspend_biomass_farm_usdperkgbm * input_biomass_kg
    vetspend_public_usd = vetspend_biomass_public_usdperkgbm * input_biomass_kg
    '''
    # Update: now that we're calculating biomass for the whole year, don't need to separately apply
    # vet & med rates to production.
    # vetspend_production_eggs_usd = vetspend_production_usdperkgprod * production_eggs_tonnes * 1000
    # vetspend_production_meat_usd = vetspend_production_usdperkgprod * production_meat_tonnes * 1000
    # vetspend_production_milk_usd = vetspend_production_usdperkgprod * production_milk_tonnes * 1000
    # vetspend_production_wool_usd = vetspend_production_usdperkgprod * production_wool_tonnes * 1000

    # ----------------------------------------------------------------------
    # AHLE
    # ----------------------------------------------------------------------
    '''
    '''
    ,inplace=True
)

world_ahle_abt_withcalcs_head = world_ahle_abt_withcalcs.head(100)
datainfo(world_ahle_abt_withcalcs)

# =============================================================================
#### Output
# =============================================================================
world_ahle_abt_withcalcs.to_csv(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_withcalcs.csv') ,index=False)
world_ahle_abt_withcalcs.to_pickle(os.path.join(FINDATA_FOLDER ,'world_ahle_abt_withcalcs.pkl.gz'))

#%% Experimenting for Dash

current_values_labels = {
    'biomass_value_2010usd':'Biomass'
    ,'output_value_meat_2010usd':'Meat'
    ,'output_value_eggs_2010usd':'Eggs'
    ,'output_value_milk_2010usd':'Milk'
    ,'output_value_wool_2010usd':'Wool'

    ,'vetspend_farm_usd':'Vet & Med costs on producers'
    ,'vetspend_public_usd':'Vet & Med costs on public'

    ,'net_value_2010usd':'Net value'
}
current_value_columns = list(current_values_labels)
ideal_values_labels = {
    'ideal_biomass_value_2010usd':'Biomass'
    ,'ideal_output_value_meat_2010usd':'Meat'
    ,'ideal_output_value_eggs_2010usd':'Eggs'
    ,'ideal_output_value_milk_2010usd':'Milk'
    ,'ideal_output_value_wool_2010usd':'Wool'
    ,'ideal_output_plus_biomass_value_2010usd':'Net value'
}
ideal_value_columns = list(ideal_values_labels)

# Sum to country-year level (summing over species)
country_year_level = world_ahle_abt_withcalcs.pivot_table(
    index=['country' ,'year' ,'incomegroup']
    ,observed=True  # Limit to combinations of index variables that are in data
    ,values=current_value_columns + ideal_value_columns
    ,aggfunc='sum'
    ,fill_value=0                     # Replace missing values with this
    )
country_year_level = country_year_level.reset_index()     # Pivoting will change columns to indexes. Change them back.

# Restructure to create columns 'current_value' and 'ideal_value'
# Keys: Country, Species, Year.  Columns: Income group, Item.
# Current values
values_current = country_year_level.melt(
    id_vars=['country' ,'year' ,'incomegroup']
    ,value_vars=current_value_columns
    ,var_name='orig_col'             # Name for new "variable" column
    ,value_name='value_usd_current'              # Name for new "value" column
    )
values_current['item'] = values_current['orig_col'].apply(lookup_from_dictionary ,DICT=current_values_labels)
del values_current['orig_col']

# Ideal values
values_ideal = country_year_level.melt(
    id_vars=['country' ,'year' ,'incomegroup']
    ,value_vars=ideal_value_columns
    ,var_name='orig_col'             # Name for new "variable" column
    ,value_name='value_usd_ideal'              # Name for new "value" column
    )
values_ideal['item'] = values_ideal['orig_col'].apply(lookup_from_dictionary ,DICT=ideal_values_labels)
del values_ideal['orig_col']

# Merge current and ideal
values_combined = pd.merge(
    left=values_current
    ,right=values_ideal
    ,on=['country' ,'year' ,'incomegroup' ,'item']
    ,how='outer'
)
datainfo(values_combined)

# Fill in zeros for ideal vetmed costs
_vetmed_rows = (values_combined['item'].str.contains('VET' ,case=False))
values_combined.loc[_vetmed_rows ,'value_usd_ideal'] = 0

# Make costs negative
values_combined.loc[_vetmed_rows ,'value_usd_current'] = -1 * values_combined['value_usd_current']

# Filter
values_combined_filtered = values_combined.query("year == 2020")
values_combined_filtered = values_combined_filtered.query("country == 'Australia'")

values_combined_filtered_sum = values_combined_filtered.groupby('item')[['value_usd_current' ,'value_usd_ideal']].sum()
values_combined_filtered_sum = values_combined_filtered_sum.reset_index()

# Extract total
_netvalue = (values_combined_filtered_sum['item'] == 'Net value')
current_net_value = values_combined_filtered_sum.loc[_netvalue ,'value_usd_current'].values[0]
ideal_net_value = values_combined_filtered_sum.loc[_netvalue ,'value_usd_ideal'].values[0]
total_ahle = ideal_net_value - current_net_value

#%% Data checks

# =============================================================================
#### Misc checks
# =============================================================================
world_ahle_abt_withcalcs_chk = world_ahle_abt_withcalcs.copy()

# Check sum of producing animals for each product and compare to
# total head calculated from imports, stocks, and births.
# Excluding producing_animals_hides_hd because this is always equal to producing_animals_meat_hd
# Sum of producing animals is less than total head calculated from imports, stocks, and births.
world_ahle_abt_withcalcs_chk.eval(
    '''
    producing_animals_sum = producing_animals_eggs_hd + producing_animals_meat_hd + \
        producing_animals_milk_hd + producing_animals_wool_hd
    producing_animals_sum_over_input_live_hd = producing_animals_sum / input_live_hd
    '''
    ,inplace=True
)
world_ahle_abt_withcalcs_chk['producing_animals_sum_over_input_live_hd'].describe()

world_ahle_abt_withcalcs_chk_spl = world_ahle_abt_withcalcs_chk.sample(n=100)

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
    df_desc = world_ahle_abt_withcalcs.groupby(['country' ,'species'])[VAR].describe()
    df_desc = indextocolumns(df_desc)
    df_desc['variable'] = VAR
    df_desc_aslist = df_desc.to_dict(orient='records')
    dist_bycountryspecies_aslist.extend(df_desc_aslist)

    # Get distribution of raw variable (before imputation)
    try:    # If raw variable exists
        df_desc = world_ahle_abt_withcalcs.groupby(['country' ,'species'])[f"{VAR}_raw"].describe()
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
#         data=world_ahle_abt_withcalcs
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
