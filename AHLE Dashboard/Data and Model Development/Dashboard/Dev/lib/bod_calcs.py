#%% About
'''
This defines functions that respond to user inputs in Dash, adding calculated
columns to the base table for each species.
'''
#%% Libraries

import os
import sys
import datetime as dt
import inspect
import numpy as np
import scipy.interpolate
import pandas as pd

#%% Master functions
# These are species-specific and call all other functions.

def calc_bod_master_poultry(
      INPUT_DF
      ,ACHIEVABLE_PCT_MASTER        # Integer [0, 120]: proportion of ideal production that is achievable without disease, i.e. efficiency of feed, medications, and practices
      ,BREED_DF_MASTER              # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_g'.
      ,AVG_DOF_MASTER               # Integer (0, 63]: Average days on feed. Will lookup breed standard weight for this day on feed.
      ,FEEDPRICE_USDPERTONNE_MASTER    # Float
      ,IDEAL_FCR_LIVE_MASTER           # Float: ideal FCR per kg live weight
      ,AVG_CARC_YIELD_MASTER=None   # Float [0, 1]: average carcass yield as proportion of live weight. If blank, will use column 'bod_breedstdyield_prpn'.
      ):
   # Create copy of input data frame
   OUTPUT_DF = INPUT_DF.copy()

   # Apply BOD calculations. Each one adds a column to the data frame.
   # Order matters as some rely on variables created by others!!!
   OUTPUT_DF['bod_dof_used'] = AVG_DOF_MASTER   # Save this as a column for display
   OUTPUT_DF['bod_breedstdwt_kg'] = OUTPUT_DF.apply(calc_bod_breedstdwt_kg_fromdays_poultry ,axis=1
      ,BREED_DF=BREED_DF_MASTER
      ,AVG_DOF=AVG_DOF_MASTER
   )
   if AVG_CARC_YIELD_MASTER:
      OUTPUT_DF['bod_breedstdyield_prpn'] = AVG_CARC_YIELD_MASTER
   else:
      OUTPUT_DF['bod_breedstdyield_prpn'] = OUTPUT_DF.apply(calc_bod_breedstdyield_prpn_poultry ,axis=1
         ,BREED_DF=BREED_DF_MASTER
         ,AVG_DOF=AVG_DOF_MASTER
      )
   OUTPUT_DF['bod_breedstdcarcwt_kg'] = OUTPUT_DF.apply(calc_bod_breedstdcarcwt_kg ,axis=1)
   OUTPUT_DF['bod_referenceproduction_tonnes'] = OUTPUT_DF.apply(calc_bod_referenceproduction_tonnes ,axis=1)
   OUTPUT_DF['bod_efficiency_tonnes'] = OUTPUT_DF.apply(calc_bod_efficiency_tonnes_frompct ,axis=1
      ,ACHIEVABLE_PCT=ACHIEVABLE_PCT_MASTER
   )
   OUTPUT_DF['bod_gmax_tonnes'] = OUTPUT_DF.apply(calc_bod_gmax_tonnes ,axis=1)
   OUTPUT_DF['bod_realizedproduction_tonnes'] = OUTPUT_DF.apply(calc_bod_realizedproduction_tonnes ,axis=1)
   OUTPUT_DF['bod_deathloss_tonnes'] = OUTPUT_DF.apply(calc_bod_deathloss_tonnes ,axis=1)
   OUTPUT_DF['bod_totalburden_tonnes'] = OUTPUT_DF.apply(calc_bod_totalburden_tonnes ,axis=1)
   OUTPUT_DF['bod_morbidity_tonnes'] = OUTPUT_DF.apply(calc_bod_morbidity_tonnes ,axis=1)

   # Adjustments & Corrections
   # If user selected an achievable proportion too low, morbidity will be the wrong sign
   # For these, set morbidity = 0 and add reduced growth to effect of feed
   rows_with_wrongsign_morbidity = (OUTPUT_DF['bod_morbidity_tonnes'] > 0)
   OUTPUT_DF.loc[rows_with_wrongsign_morbidity] = OUTPUT_DF.loc[rows_with_wrongsign_morbidity].eval(
       '''
       bod_efficiency_tonnes = bod_efficiency_tonnes + bod_morbidity_tonnes
       bod_morbidity_tonnes = 0
       bod_totalburden_tonnes = bod_deathloss_tonnes
       '''
   )

   # Ideal Costs
   OUTPUT_DF['adjusted_feedcost_usdperkglive'] = OUTPUT_DF.apply(calc_adjusted_feedcost_usdperkglive ,axis=1
         ,FEEDPRICE_USDPERTONNE=FEEDPRICE_USDPERTONNE_MASTER
      )
   OUTPUT_DF['ideal_headplaced'] = OUTPUT_DF.apply(calc_ideal_headplaced ,axis=1)
   OUTPUT_DF['ideal_fcr'] = IDEAL_FCR_LIVE_MASTER
   OUTPUT_DF[['ideal_feed_tonnes' ,'ideal_feedcost_usdperkglive']] = \
      OUTPUT_DF.apply(calc_ideal_feedcost_usdperkglive ,axis=1
         ,IDEAL_FCR_LIVE=IDEAL_FCR_LIVE_MASTER
         ,FEEDPRICE_USDPERTONNE=FEEDPRICE_USDPERTONNE_MASTER
      )
   OUTPUT_DF['ideal_chickcost_usdperkglive'] = OUTPUT_DF.apply(calc_ideal_chickcost_usdperkglive ,axis=1)
   OUTPUT_DF['ideal_landhousingcost_usdperkglive'] = OUTPUT_DF.apply(calc_ideal_landhousingcost_usdperkglive ,axis=1)
   OUTPUT_DF['ideal_laborcost_usdperkglive'] = OUTPUT_DF.apply(calc_ideal_laborcost_usdperkglive ,axis=1)
   OUTPUT_DF['ideal_medcost_usdperkglive'] = OUTPUT_DF.apply(calc_ideal_medcost_usdperkglive ,axis=1)
   OUTPUT_DF['ideal_othercost_usdperkglive'] = OUTPUT_DF.apply(calc_ideal_othercost_usdperkglive ,axis=1)

   return OUTPUT_DF

def calc_bod_master_swine(
      INPUT_DF
      ,BREED_DF_MASTER           # Data frame with breed reference information. Must contain columns 'dayonfeed', 'bodyweight_g', and 'cml_feedintake_kg'.
      ,AVG_CARC_YIELD_MASTER     # Float [0, 1]: average carcass yield as proportion of live weight
      ,FEEDPRICE_USDPERTONNE_MASTER    # Float
      ,IDEAL_FCR_LIVE_MASTER           # Float: ideal FCR per kg live weight

      # Alternatives for calculating breed standard weight
      # These get default=None. The first one specified will determine the calculation used.
      ,AVG_DOF_MASTER=None            # Integer [1, 176]: Average days on feed. Will lookup breed standard weight for this day on feed.
      ,AVG_FEEDINT_KG_MASTER=None     # Float: average feed intake in kg per head

      # Alternatives for calculating suboptimal growth
      # These get default=None. The first one specified will determine the calculation used.
      ,ACHIEVABLE_PCT_MASTER=None     # Integer [0, 120]: proportion of ideal production that is achievable without disease, i.e. efficiency of feed, medications, and practices
      ,ACHIEVABLE_WT_KG_MASTER=None   # Float: achievable weight without disease. For use with function calc_bod_subopt_fromwt_tonnes().
      ):
   funcname = inspect.currentframe().f_code.co_name

   OUTPUT_DF = INPUT_DF.copy()     # Create copy of input data frame

   # Apply BOD calculations. Each one adds a column to the data frame.
   # Order matters as some rely on variables created by others!!!
   if AVG_DOF_MASTER:
      OUTPUT_DF['bod_breedstdwt_kg'] = OUTPUT_DF.apply(calc_bod_breedstdwt_kg_fromdays_swine ,axis=1
          ,BREED_DF=BREED_DF_MASTER
          ,AVG_DOF=AVG_DOF_MASTER
      )
      OUTPUT_DF['bod_dof_used'] = AVG_DOF_MASTER   # Add column for display
   elif AVG_FEEDINT_KG_MASTER:
      OUTPUT_DF['bod_breedstdwt_kg'] = OUTPUT_DF.apply(calc_bod_breedstdwt_kg_fromfeed_swine ,axis=1
         ,BREED_DF=BREED_DF_MASTER
         ,AVG_FEEDINT_KG=AVG_FEEDINT_KG_MASTER
      )
      OUTPUT_DF['bod_feedint_used'] = AVG_FEEDINT_KG_MASTER   # Add column for display
   else:
      print(f"<{funcname}> Error: missing required argument: either AVG_DOF_MASTER or AVG_FEEDINT_KG_MASTER.")

   if AVG_CARC_YIELD_MASTER:
      OUTPUT_DF['bod_breedstdyield_prpn'] = AVG_CARC_YIELD_MASTER
   else:   # For swine, there is no breed standard lookup for yield
      print(f"<{funcname}> Error: missing required argument: AVG_CARC_YIELD_MASTER.")

   OUTPUT_DF['bod_breedstdcarcwt_kg'] = OUTPUT_DF.apply(calc_bod_breedstdcarcwt_kg ,axis=1)
   OUTPUT_DF['bod_referenceproduction_tonnes'] = OUTPUT_DF.apply(calc_bod_referenceproduction_tonnes ,axis=1)

   if ACHIEVABLE_PCT_MASTER:
      OUTPUT_DF['bod_efficiency_tonnes'] = OUTPUT_DF.apply(calc_bod_efficiency_tonnes_frompct ,axis=1
          ,ACHIEVABLE_PCT=ACHIEVABLE_PCT_MASTER
      )
   elif ACHIEVABLE_WT_KG_MASTER:
      OUTPUT_DF['bod_efficiency_tonnes'] = OUTPUT_DF.apply(calc_bod_efficiency_tonnes_fromwt ,axis=1
          ,ACHIEVABLE_WT_KG=ACHIEVABLE_WT_KG_MASTER
      )
   else:
      print(f"<{funcname}> Error: missing required argument for calculating suboptimal growth.")

   OUTPUT_DF['bod_gmax_tonnes'] = OUTPUT_DF.apply(calc_bod_gmax_tonnes ,axis=1)
   OUTPUT_DF['bod_realizedproduction_tonnes'] = OUTPUT_DF.apply(calc_bod_realizedproduction_tonnes ,axis=1)
   OUTPUT_DF['bod_deathloss_tonnes'] = OUTPUT_DF.apply(calc_bod_deathloss_tonnes ,axis=1)
   OUTPUT_DF['bod_totalburden_tonnes'] = OUTPUT_DF.apply(calc_bod_totalburden_tonnes ,axis=1)
   OUTPUT_DF['bod_morbidity_tonnes'] = OUTPUT_DF.apply(calc_bod_morbidity_tonnes ,axis=1)

   # Adjustments & Corrections
   # If user selected an achievable proportion too low, morbidity will be the wrong sign
   # For these, set morbidity = 0 and add reduced growth to effect of feed
   rows_with_wrongsign_morbidity = (OUTPUT_DF['bod_morbidity_tonnes'] > 0)
   OUTPUT_DF.loc[rows_with_wrongsign_morbidity] = OUTPUT_DF.loc[rows_with_wrongsign_morbidity].eval(
       '''
       bod_efficiency_tonnes = bod_efficiency_tonnes + bod_morbidity_tonnes
       bod_morbidity_tonnes = 0
       bod_totalburden_tonnes = bod_deathloss_tonnes
       '''
   )

   # Ideal Costs
   OUTPUT_DF['adjusted_feedcost_usdperkgcarc'] = OUTPUT_DF.apply(calc_adjusted_feedcost_usdperkgcarc ,axis=1
         ,FEEDPRICE_USDPERTONNE=FEEDPRICE_USDPERTONNE_MASTER
      )
   OUTPUT_DF['ideal_headplaced'] = OUTPUT_DF.apply(calc_ideal_headplaced ,axis=1)
   OUTPUT_DF['ideal_fcr'] = IDEAL_FCR_LIVE_MASTER
   OUTPUT_DF[['ideal_feed_tonnes' ,'ideal_feedcost_usdperkgcarc']] = \
      OUTPUT_DF.apply(
         calc_ideal_feedcost_usdperkgcarc ,axis=1
         ,IDEAL_FCR_LIVE=IDEAL_FCR_LIVE_MASTER
         ,FEEDPRICE_USDPERTONNE=FEEDPRICE_USDPERTONNE_MASTER
      )
   OUTPUT_DF['ideal_nonfeedvariablecost_usdperkgcarc'] = OUTPUT_DF.apply(calc_ideal_nonfeedvariablecost_usdperkgcarc ,axis=1)
   OUTPUT_DF['ideal_landhousingcost_usdperkgcarc'] = OUTPUT_DF.apply(calc_ideal_landhousingcost_usdperkgcarc ,axis=1)
   OUTPUT_DF['ideal_laborcost_usdperkgcarc'] = OUTPUT_DF.apply(calc_ideal_laborcost_usdperkgcarc ,axis=1)

   return OUTPUT_DF

#%% Production

# =============================================================================
#### Common
# =============================================================================
def calc_bod_referenceproduction_tonnes(
      INPUT_ROW
      ):
   # (Animals placed) x (Breed Std. Live Weight @ Avg. Days on Feed) x (Carcass Yield)
   OUTPUT = INPUT_ROW['acc_headplaced'] * INPUT_ROW['bod_breedstdwt_kg'] * INPUT_ROW['bod_breedstdyield_prpn'] / 1000
   return OUTPUT

def calc_bod_efficiency_tonnes_frompct(
      INPUT_ROW
      ,ACHIEVABLE_PCT   # Integer [0+]: proportion of ideal production that is achievable without disease, i.e. efficiency of feed, medications, and practices. Can be > 100.
      ):
   OUTPUT = (INPUT_ROW['bod_referenceproduction_tonnes'] * (1 - (ACHIEVABLE_PCT/100))) * (-1)  # If ACHIEVABLE_PCT < 100, want result to be negative.
   return OUTPUT

def calc_bod_efficiency_tonnes_fromwt(
      INPUT_ROW
      ,ACHIEVABLE_WT_KG   # Float: achievable weight without disease
      ):
   OUTPUT = (INPUT_ROW['bod_referenceproduction_tonnes'] - (INPUT_ROW['acc_headplaced'] * ACHIEVABLE_WT_KG * INPUT_ROW['bod_breedstdyield_prpn'] / 1000)) * (-1)  # If ACHIEVABLE_WT_KG < reference production, want result to be negative.
   return OUTPUT

def calc_bod_gmax_tonnes(INPUT_ROW):
    OUTPUT = INPUT_ROW['bod_referenceproduction_tonnes'] + INPUT_ROW['bod_efficiency_tonnes']
    return OUTPUT

def calc_bod_realizedproduction_tonnes(INPUT_ROW):
   OUTPUT = INPUT_ROW['acc_totalcarcweight_tonnes']
   return OUTPUT

def calc_bod_deathloss_tonnes(INPUT_ROW):
   # Total shortfall in head count. All-cause mortality.
   # Convert to weight by multiplying by avg. carcass weight of those that lived
   OUTPUT = (INPUT_ROW['acc_headplaced'] - INPUT_ROW['acc_headslaughtered']) \
       * INPUT_ROW['acc_avgcarcweight_kg'] / 1000 * (-1)  # Want result to be negative
   # Alternative: multiply by breed standard weight
   # I don't think we want to do this, because it muddles the losses due to morbidity vs. mortality
   # OUTPUT = (INPUT_ROW['acc_headplaced'] - INPUT_ROW['acc_headslaughtered']) \
   #     * INPUT_ROW['bod_breedstdwt_kg'] / 1000 * (-1)  # Want result to be negative
   return OUTPUT

# Alternative 2: multiply by breed standard weight and adjust for achievable percent
# Like the alternative using breed standard weight, this muddles morbidity and mortality. Not using.
# def calc_bod_deathloss_tonnes_frompct(
#       INPUT_ROW
#       ,ACHIEVABLE_PCT   # Integer [0+]: proportion of ideal production that is achievable without disease, i.e. efficiency of feed, medications, and practices. Can be > 100.
#       ):
#    OUTPUT = (INPUT_ROW['acc_headplaced'] - INPUT_ROW['acc_headslaughtered']) \
#       * (INPUT_ROW['bod_breedstdwt_kg'] * (ACHIEVABLE_PCT/100)) / 1000 * (-1)  # Want result to be negative
#    return OUTPUT

# def calc_bod_deathloss_tonnes_fromwt(
#       INPUT_ROW
#       ,ACHIEVABLE_WT_KG   # Float: achievable weight without disease
#       ):
#    OUTPUT = (INPUT_ROW['acc_headplaced'] - INPUT_ROW['acc_headslaughtered']) \
#       * (ACHIEVABLE_WT_KG * INPUT_ROW['bod_breedstdyield_prpn']) / 1000 * (-1)  # Want result to be negative
#    return OUTPUT

def calc_bod_totalburden_tonnes(INPUT_ROW):
   OUTPUT = (INPUT_ROW['bod_gmax_tonnes'] - INPUT_ROW['bod_realizedproduction_tonnes']) * (-1)  # Want result to be negative
   return OUTPUT

def calc_bod_morbidity_tonnes(INPUT_ROW):
   OUTPUT = (INPUT_ROW['bod_totalburden_tonnes'] - INPUT_ROW['bod_deathloss_tonnes'])
   return OUTPUT

def calc_bod_breedstdcarcwt_kg(INPUT_ROW):
   OUTPUT = INPUT_ROW['bod_breedstdwt_kg'] * INPUT_ROW['bod_breedstdyield_prpn']
   return OUTPUT

# =============================================================================
#### Poultry
# =============================================================================
def calc_bod_breedstdwt_kg_fromdays_poultry(
      INPUT_ROW
      ,BREED_DF       # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_g'.
      ,AVG_DOF        # Integer (0, 60]: Average days on feed. Will lookup breed standard weight for this day on feed.
      ):
   # Could limit breed choice based on country
      # India: Vencobb400
      # Others: Cobb500, Ross308, or Ross708
   _select_dof = (BREED_DF['dayonfeed'] == AVG_DOF)
   breedstdwt_kg = BREED_DF.loc[_select_dof ,'bodyweight_g'] / 1000
   OUTPUT = breedstdwt_kg
   return OUTPUT

def calc_bod_breedstdyield_prpn_poultry(
      INPUT_ROW
      ,BREED_DF       # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'pct_yield'.
      ,AVG_DOF        # Integer (0, 60]: Average days on feed. Will lookup breed standard yield for this day on feed.
      ):
   _select_dof = (BREED_DF['dayonfeed'] == AVG_DOF)
   breedstdyield_prpn = BREED_DF.loc[_select_dof ,'pct_yield'] / 100
   OUTPUT = breedstdyield_prpn
   return OUTPUT

# =============================================================================
#### Swine
# =============================================================================
def calc_bod_breedstdwt_kg_fromdays_swine(
      INPUT_ROW
      ,BREED_DF       # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_kg'.
      ,AVG_DOF        # Integer [1, 176]: Average days on feed. Will lookup breed standard weight for this day on feed.
      ):
   _select_dof = (BREED_DF['dayonfeed'] == AVG_DOF)
   breedstdwt_kg = BREED_DF.loc[_select_dof ,'bodyweight_kg']
   OUTPUT = breedstdwt_kg
   return OUTPUT

def calc_bod_breedstdwt_kg_fromfeed_swine(
      INPUT_ROW
      ,BREED_DF         # Data frame with breed reference information. Must contain columns 'bodyweight_kg' and 'cml_feedintake_kg'.
      ,AVG_FEEDINT_KG   # Float: average feed intake in kg per head
      ):
   # Create interpolator from breed standard
   interp_weight_from_feed = scipy.interpolate.interp1d(
      BREED_DF['cml_feedintake_kg']
      ,BREED_DF['bodyweight_kg']
   )
   # Apply interpolator
   OUTPUT = interp_weight_from_feed(AVG_FEEDINT_KG) * 1   # Multiply by one: trick to convert array to number
   return OUTPUT

#%% Costs

# =============================================================================
#### Common
# =============================================================================
# Zero mortality and zero morbidity means all head placed would survive to
# slaughter and achieve breed standard weight PLUS effect of feed and practices
# for given country. Calculate number of head needed under these conditions to
# get same total production.

# TRICK: Gmax already includes logic for breed standard weight and effect of
# feed and practices to tell us what could be achieved by head placed. So find
# head placed that makes gmax = realized production.
def calc_ideal_headplaced(INPUT_ROW):
   # Calculate actual production as proporion of gmax
   realized_prpn_gmax = INPUT_ROW['bod_realizedproduction_tonnes'] / INPUT_ROW['bod_gmax_tonnes']

   # Reduce head placed by this proportion
   ideal_headplaced = round(INPUT_ROW['acc_headplaced'] * realized_prpn_gmax ,0)
   OUTPUT = ideal_headplaced
   return OUTPUT

# =============================================================================
#### Poultry
# Swine costs are per kg CARCASS weight while poultry are per kg LIVE weight
# =============================================================================
# We have data on actual feed price for some countries and years but we also
# allow the user to specify a feed price with a slider.
# Calculate an adjusted actual feed cost based on the slider.
def calc_adjusted_feedcost_usdperkglive(
      INPUT_ROW
      ,FEEDPRICE_USDPERTONNE
      ):
   # Get feed price slider as proportion of actual
   if pd.notnull(INPUT_ROW['acc_feedprice_usdpertonne']):   # If actual feed price is not missing
      feedprice_slider_prpn = FEEDPRICE_USDPERTONNE / INPUT_ROW['acc_feedprice_usdpertonne']
   else:
      feedprice_slider_prpn = 1

   # Adjust feed cost in same proportion
   adjusted_feedcost_usdperkglive = INPUT_ROW['acc_feedcost_usdperkglive'] * feedprice_slider_prpn
   OUTPUT = adjusted_feedcost_usdperkglive
   return OUTPUT

# Calculate feed required to reach same production under ideal FCR
def calc_ideal_feedcost_usdperkglive(
      INPUT_ROW
      ,IDEAL_FCR_LIVE   # Float: ideal FCR (kg feed per kg live weight)
      ,FEEDPRICE_USDPERTONNE
      ):
   # Back-calculate realized live weight from production and carcass yield
   required_live_weight_tonnes = INPUT_ROW['bod_realizedproduction_tonnes'] / INPUT_ROW['bod_breedstdyield_prpn']

   # Calculate ideal feed required
   ideal_feed_tonnes = required_live_weight_tonnes * IDEAL_FCR_LIVE

   # Calculate feed cost
   # Using feed price from data
   ideal_feedcost_usdperkglive = (ideal_feed_tonnes * INPUT_ROW['acc_feedprice_usdpertonne']) / (required_live_weight_tonnes * 1000)
   # Using feed price input parameter
   ideal_feedcost_whatif_usdperkglive = (ideal_feed_tonnes * FEEDPRICE_USDPERTONNE) / (required_live_weight_tonnes * 1000)

   OUTPUT = pd.Series([ideal_feed_tonnes ,ideal_feedcost_whatif_usdperkglive])
   return OUTPUT

def calc_ideal_chickcost_usdperkglive(INPUT_ROW):
   # Reduce in proportion to head placed
   ideal_headplaced_prpn = INPUT_ROW['ideal_headplaced'] / INPUT_ROW['acc_headplaced']
   ideal_chickcost_usdperkglive = INPUT_ROW['acc_chickcost_usdperkglive'] * ideal_headplaced_prpn
   OUTPUT = ideal_chickcost_usdperkglive
   return OUTPUT

def calc_ideal_landhousingcost_usdperkglive(INPUT_ROW):
   # Reduce in proportion to head placed
   ideal_headplaced_prpn = INPUT_ROW['ideal_headplaced'] / INPUT_ROW['acc_headplaced']
   ideal_landhousingcost_usdperkglive = INPUT_ROW['acc_landhousingcost_usdperkglive'] * ideal_headplaced_prpn
   OUTPUT = ideal_landhousingcost_usdperkglive
   return OUTPUT

def calc_ideal_laborcost_usdperkglive(INPUT_ROW):
   # Reduce in proportion to land & facilities costs
   ideal_financecost_prpn = INPUT_ROW['ideal_landhousingcost_usdperkglive'] / INPUT_ROW['acc_landhousingcost_usdperkglive']
   ideal_laborcost_usdperkglive = INPUT_ROW['acc_laborcost_usdperkglive'] * ideal_financecost_prpn
   OUTPUT = ideal_laborcost_usdperkglive
   return OUTPUT

def calc_ideal_medcost_usdperkglive(INPUT_ROW):
   # Reduce in proportion to head placed
   ideal_headplaced_prpn = INPUT_ROW['ideal_headplaced'] / INPUT_ROW['acc_headplaced']
   ideal_medcost_usdperkglive = INPUT_ROW['acc_medcost_usdperkglive'] * ideal_headplaced_prpn
   OUTPUT = ideal_medcost_usdperkglive
   return OUTPUT

def calc_ideal_othercost_usdperkglive(INPUT_ROW):
   # Reduce in proportion to head placed
   ideal_headplaced_prpn = INPUT_ROW['ideal_headplaced'] / INPUT_ROW['acc_headplaced']
   ideal_othercost_usdperkglive = INPUT_ROW['acc_othercost_usdperkglive'] * ideal_headplaced_prpn
   OUTPUT = ideal_othercost_usdperkglive
   return OUTPUT

# =============================================================================
#### Swine
# Swine costs are per kg CARCASS weight while poultry are per kg LIVE weight
# =============================================================================
# We have data on actual feed price for some countries and years but we also
# allow the user to specify a feed price with a slider.
# Calculate an adjusted actual feed cost based on the slider.
def calc_adjusted_feedcost_usdperkgcarc(
      INPUT_ROW
      ,FEEDPRICE_USDPERTONNE
      ):
   # Get feed price slider as proportion of actual price
   feedprice_slider_prpn = FEEDPRICE_USDPERTONNE / INPUT_ROW['acc_feedprice_usdpertonne']

   # Adjust feed cost in same proportion
   adjusted_feedcost_usdperkgcarc = INPUT_ROW['acc_feedcost_usdperkgcarc'] * feedprice_slider_prpn
   OUTPUT = adjusted_feedcost_usdperkgcarc
   return OUTPUT

# Calculate feed required to reach same production under ideal FCR
def calc_ideal_feedcost_usdperkgcarc(
      INPUT_ROW
      ,FEEDPRICE_USDPERTONNE
      ,IDEAL_FCR_LIVE   # Float: ideal FCR (kg feed per kg live weight)
      ):
   # Back-calculate realized live weight from production and carcass yield
   required_live_weight_tonnes = INPUT_ROW['bod_realizedproduction_tonnes'] / INPUT_ROW['bod_breedstdyield_prpn']

   # Calculate ideal feed required
   ideal_feed_tonnes = required_live_weight_tonnes * IDEAL_FCR_LIVE

   # Calculate feed cost
   # Using feed price from data
   ideal_feedcost_usdperkgcarc = (ideal_feed_tonnes * INPUT_ROW['acc_feedprice_usdpertonne']) / (INPUT_ROW['bod_realizedproduction_tonnes'] * 1000)
   # Using feed price from input parameter
   ideal_feedcost_whatif_usdperkgcarc = (ideal_feed_tonnes * FEEDPRICE_USDPERTONNE) / (INPUT_ROW['bod_realizedproduction_tonnes'] * 1000)

   OUTPUT = pd.Series([ideal_feed_tonnes ,ideal_feedcost_usdperkgcarc])
   return OUTPUT

def calc_ideal_nonfeedvariablecost_usdperkgcarc(INPUT_ROW):
   # Reduce in proportion to head placed
   ideal_headplaced_prpn = INPUT_ROW['ideal_headplaced'] / INPUT_ROW['acc_headplaced']
   ideal_nonfeedvariablecost_usdperkgcarc = INPUT_ROW['acc_nonfeedvariablecost_usdperkgcarc'] * ideal_headplaced_prpn
   OUTPUT = ideal_nonfeedvariablecost_usdperkgcarc
   return OUTPUT

def calc_ideal_landhousingcost_usdperkgcarc(INPUT_ROW):
   # Reduce in proportion to head placed
   ideal_headplaced_prpn = INPUT_ROW['ideal_headplaced'] / INPUT_ROW['acc_headplaced']
   ideal_landhousingcost_usdperkgcarc = INPUT_ROW['acc_landhousingcost_usdperkgcarc'] * ideal_headplaced_prpn
   OUTPUT = ideal_landhousingcost_usdperkgcarc
   return OUTPUT

def calc_ideal_laborcost_usdperkgcarc(INPUT_ROW):
   # Reduce in proportion to land & facilities costs
   ideal_financecost_prpn = INPUT_ROW['ideal_landhousingcost_usdperkgcarc'] / INPUT_ROW['acc_landhousingcost_usdperkgcarc']
   ideal_laborcost_usdperkgcarc = INPUT_ROW['acc_laborcost_usdperkgcarc'] * ideal_financecost_prpn
   OUTPUT = ideal_laborcost_usdperkgcarc
   return OUTPUT
