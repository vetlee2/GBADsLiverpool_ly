#%% About
'''
This defines the functions to calculate AHLE for the global aggregate tab.
'''
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
        "L":0.15
        ,"LM":0.1
        ,"UM":0.06
        ,"H":0.04
    }
    INPUT_DF['mortality_rate'] = INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=mortality_byincome)
    return INPUT_DF

def add_morbidity_rate(INPUT_DF):
    morbidity_byincome = {
        "L":0.15
        ,"LM":0.15
        ,"UM":0.15
        ,"H":0.15
    }
    INPUT_DF['morbidity_rate'] = INPUT_DF['incomegroup'].apply(lookup_from_dictionary ,DICT=morbidity_byincome)
    return INPUT_DF

def add_vetmed_rates(INPUT_DF):
    # Spend per kg biomass, farm level
    farmspend_perkg_biomass_byincome = {
        "L":0.01
        ,"LM":0.02
        ,"UM":0.03
        ,"H":0.05
    }
    # Spend per kg biomass, public level
    pubspend_perkg_biomass_byincome = {
        "L":0.005
        ,"LM":0.01
        ,"UM":0.02
        ,"H":0.03
    }
    # Spend per kg production
    vetspend_perkg_prod_byincome = {
        "L":0.0025
        ,"LM":0.005
        ,"UM":0.01
        ,"H":0.01
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
        # Excluding Wool to match William's calcs
        '''
        ideal_biomass_value_2010usd = biomass_value_2010usd * (1 / (1 - mortality_rate))
        ideal_output_value_meat_2010usd = output_value_meat_2010usd * (1 / (1 - morbidity_rate))
        ideal_output_value_eggs_2010usd = output_value_eggs_2010usd * (1 / (1 - morbidity_rate))
        ideal_output_value_milk_2010usd = output_value_milk_2010usd * (1 / (1 - morbidity_rate))
        ideal_output_value_wool_2010usd = output_value_wool_2010usd * (1 / (1 - morbidity_rate))

        ideal_output_plus_biomass_value_2010usd = ideal_biomass_value_2010usd + ideal_output_value_meat_2010usd \
            + ideal_output_value_eggs_2010usd + ideal_output_value_milk_2010usd
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

        vetspend_farm_usd = vetspend_biomass_farm_usd + vetspend_production_meat_usd \
            + vetspend_production_eggs_usd + vetspend_production_milk_usd + vetspend_production_wool_usd
        vetspend_public_usd = vetspend_biomass_public_usd
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
    )
    return OUTPUT_DF

# =============================================================================
# These center on adjusting INPUTS under ideal conditions.
# See Animal stock and flow.docx from William.
# =============================================================================
# def ahle_calcs_adj_inputs():
#     return
