#%% About
'''
'''
#%% Merge

un_geo_codes

# =============================================================================
#### Prep Base table: biomass
# =============================================================================
# Add country iso code
biomass_iso = pd.merge(
    left=biomass
    ,right=un_geo_codes[['shortname' ,'iso3']]
    ,left_on='country'
    ,right_on='shortname'
    ,how='left'
    )

# =============================================================================
#### Prep FAO tables
# =============================================================================
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

datainfo(fao_combo)

# Add country iso code
fao_combo_iso = pd.merge(
    left=fao_combo
    ,right=un_geo_codes[['shortname' ,'iso3']]
    ,left_on='country'
    ,right_on='shortname'
    ,how='left'
    )

# =============================================================================
#### Prep World Bank tables
# =============================================================================
# Combine World Bank tables
wb_combo = pd.merge(
    left=wb_income
    ,right=wb_region
    ,on='iso3'
    ,how='outer'
    ,indicator='_merge_wb'
    )
wb_combo['_merge_wb'].value_counts()

# =============================================================================
#### Merge
# =============================================================================
# FAO onto Biomass
world_ahle_abt = pd.merge(
    left=biomass_iso
    ,right=fao_combo_iso
    ,on=['iso3' ,'year']
    ,how='outer'
    ,indicator='_merge_1'
    )
world_ahle_abt['_merge_1'].value_counts()

# World Bank
world_ahle_abt = pd.merge(
    left=world_ahle_abt
    ,right=wb_combo
    ,on=['iso3' ,'year']
    ,how='outer'
    ,indicator='_merge_2'
    )
world_ahle_abt['_merge_2'].value_counts()

datainfo(world_ahle_abt)

# Export
world_ahle_abt.to_csv(os.path.join(RAWDATA_FOLDER ,'world_ahle_abt.csv'))
world_ahle_abt.to_pickle(os.path.join(RAWDATA_FOLDER ,'world_ahle_abt.pkl.gz'))
