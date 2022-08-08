#%% About
'''
'''
#%% Merge

# =============================================================================
#### Prep Base table: biomass
# =============================================================================
try:
   biomass.shape
except NameError:
   biomass = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))

try:
   un_geo_codes.shape
except NameError:
   un_geo_codes = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'un_geo_codes.pkl.gz'))

un_geo_codes = un_geo_codes.rename(columns={'shortname':'country'})

# Add country iso code
biomass_iso = pd.merge(
    left=biomass
    ,right=un_geo_codes[['country' ,'iso3']]
    ,on='country'
    ,how='left'
    )
datainfo(biomass_iso)

# =============================================================================
#### Prep FAO tables
# =============================================================================
try:
   fao_production_p.shape
except NameError:
   fao_production_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_production_p.pkl.gz'))

try:
   fao_producerprice_p.shape
except NameError:
   fao_producerprice_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_producerprice_p.pkl.gz'))

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

# Add country iso code
fao_combo_iso = pd.merge(
    left=fao_combo
    ,right=un_geo_codes[['country' ,'iso3']]
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

# =============================================================================
#### Merge
# =============================================================================
# FAO onto Biomass
world_ahle_abt = pd.merge(
    left=biomass_iso
    ,right=fao_combo_iso
    ,on=['iso3' ,'year']
    ,how='left'
    ,indicator='_merge_1'
    )
world_ahle_abt['_merge_1'].value_counts()

# World Bank
world_ahle_abt = pd.merge(
    left=world_ahle_abt
    ,right=wb_combo
    ,on=['iso3' ,'year']
    ,how='left'
    ,indicator='_merge_2'
    )
world_ahle_abt['_merge_2'].value_counts()

# Rename
world_ahle_abt = world_ahle_abt.drop(columns=['country' ,'country_y' ,'time_code'])
world_ahle_abt = world_ahle_abt.rename(columns={'country_x':'country' ,'flag_x':'flag_biomass' ,'flag_y':'flag_wb'})

datainfo(world_ahle_abt)

# Export
world_ahle_abt.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.csv'))
world_ahle_abt.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.pkl.gz'))
