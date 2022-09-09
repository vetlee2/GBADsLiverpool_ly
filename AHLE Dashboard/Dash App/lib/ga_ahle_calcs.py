#%% About
'''
This defines the functions to calculate AHLE for the global aggregate tab.
'''
#%% Imports

import numpy as np

#%% Define functions

# =============================================================================
# Utility
# =============================================================================
# To add a column to a data frame by lookup on keys
# Usage: df['new_col'] = df['col_with_lookup'].apply(lookup_from_dictionary ,DICT=my_dictionary)
def lookup_from_dictionary(KEY ,DICT):
    try:
        return DICT[KEY]      # If key is found in dictionary, return value
    except:
        return None

# =============================================================================
# Add mortality, morbidity, and vet & med rates by income group
# These are currently trivial functions, but they could be made to recalculate
# rates with various user input.
# =============================================================================
def add_mortality_rate(INPUT_DF):
    mortality_byincome = {
        "Low":0.15
        ,"Lower Middle":0.1
        ,"Upper Middle":0.06
        ,"High":0.04
    }
    INPUT_DF['mortality_rate'] = INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=mortality_byincome)
    return INPUT_DF

def add_morbidity_rate(INPUT_DF):
    morbidity_byincome = {
        "Low":0.15
        ,"Lower Middle":0.15
        ,"Upper Middle":0.15
        ,"High":0.15
    }
    INPUT_DF['morbidity_rate'] = INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=morbidity_byincome)
    return INPUT_DF

def add_vetmed_rates(INPUT_DF):
    # Spend per kg biomass, farm level
    farmspend_perkg_biomass_byincome = {
        "Low":0.01
        ,"Lower Middle":0.02
        ,"Upper Middle":0.03
        ,"High":0.05
    }
    # Spend per kg biomass, public level
    pubspend_perkg_biomass_byincome = {
        "Low":0.005
        ,"Lower Middle":0.01
        ,"Upper Middle":0.02
        ,"High":0.03
    }
    # Spend per kg production
    vetspend_perkg_prod_byincome = {
        "Low":0.0025
        ,"Lower Middle":0.005
        ,"Upper Middle":0.01
        ,"High":0.01
    }
    INPUT_DF['vetspend_biomass_farm_usdperkgbm'] = \
        INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=farmspend_perkg_biomass_byincome)
    INPUT_DF['vetspend_biomass_public_usdperkgbm'] = \
        INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=pubspend_perkg_biomass_byincome)
    INPUT_DF['vetspend_production_usdperkgprod'] = \
        INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=vetspend_perkg_prod_byincome)
    return INPUT_DF

# =============================================================================
# These center on adjusting OUTPUTS under ideal conditions and match the original
# spreadsheet produced by William. See World AHLE.xlsx.
# =============================================================================
def ahle_calcs_adj_outputs(INPUT_DF):
    OUTPUT_DF = INPUT_DF.eval(
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
        OUTPUT_DF[COL] = OUTPUT_DF[COL].replace(np.nan ,0)

    OUTPUT_DF = OUTPUT_DF.eval(
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
        ahle_2010usd_perkgbm = ahle_total_2010usd / biomass

        ahle_dueto_reducedoutput_pctofoutput = (ahle_dueto_reducedoutput_2010usd / output_plus_biomass_value_2010usd) * 100
        ahle_dueto_vetandmedcost_pctofoutput = (ahle_dueto_vetandmedcost_2010usd / output_plus_biomass_value_2010usd) * 100
        ahle_total_pctofoutput = (ahle_total_2010usd / output_plus_biomass_value_2010usd) * 100
        '''
    )
    return OUTPUT_DF

# =============================================================================
# These center on adjusting INPUTS under ideal conditions.
# See Animal stock and flow.docx from William.
# =============================================================================
def ahle_calcs_adj_inputs(INPUT_DF):
    OUTPUT_DF = INPUT_DF.copy()

    # Calculate births outside eval() so I can round
    OUTPUT_DF['births_hd'] = (OUTPUT_DF['output_total_hd'] / (1 - OUTPUT_DF['mortality_rate'])) \
        - (OUTPUT_DF['stocks_hd'] + OUTPUT_DF['import_animals_hd'])
    OUTPUT_DF['births_hd'] = round(OUTPUT_DF['births_hd'] ,0)

    OUTPUT_DF.eval(
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
    return OUTPUT_DF
