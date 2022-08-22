#%% About
'''
'''
#%% Import FAO tables

# =============================================================================
#### Crops and Livestock Products
# https://www.fao.org/faostat/en/#data/QCL
# =============================================================================
# ----------------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------------
fao_production = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'FAOSTAT_livestock_products_stocks_slaughter_2000_2020.csv'))
cleancolnames(fao_production)
datainfo(fao_production)

# ----------------------------------------------------------------------------
# Reshape so each element_item_unit is its own column
# ----------------------------------------------------------------------------
fao_production_element_items = fao_production[['element' ,'item' ,'unit']].value_counts()

fao_production_p = fao_production.pivot(
    index=['area_code__iso3_' ,'area' ,'year']          # Column(s) to make new index. If blank, uses existing index.
    ,columns=['element' ,'item' ,'unit']       # Column(s) to make new columns
    ,values='value'        # Column to populate rows. Can pass a list, but will create multi-indexed columns.
)
fao_production_p = indextocolumns(fao_production_p)
fao_production_p = colnames_from_index(fao_production_p)
cleancolnames(fao_production_p)

# Adjust column names
fao_production_p.columns = fao_production_p.columns.str.replace('__' ,'_')
fao_production_p.columns = fao_production_p.columns.str.replace('area' ,'country')

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(fao_production_p)
# datadesc(fao_production_p ,PRODATA_FOLDER)

fao_production_p.to_csv(os.path.join(PRODATA_FOLDER ,'fao_production_p.csv'))
fao_production_p.to_pickle(os.path.join(PRODATA_FOLDER ,'fao_production.pkl.gz'))

# =============================================================================
#### Live Animal Imports and Exports
# https://www.fao.org/faostat/en/#data/TCL
# =============================================================================
# ----------------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------------
fao_impexp = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'FAOSTAT_liveanimals_import_export_2000_2020.csv'))
cleancolnames(fao_impexp)
datainfo(fao_impexp)

# ----------------------------------------------------------------------------
# Reshape so each element_item_unit is its own column
# ----------------------------------------------------------------------------
fao_impexp_element_items = fao_impexp[['element' ,'item' ,'unit']].value_counts()

fao_impexp_p = fao_impexp.pivot(
    index=['area_code__iso3_' ,'area' ,'year']          # Column(s) to make new index. If blank, uses existing index.
    ,columns=['element' ,'item' ,'unit']       # Column(s) to make new columns
    ,values='value'        # Column to populate rows. Can pass a list, but will create multi-indexed columns.
)
fao_impexp_p = indextocolumns(fao_impexp_p)
fao_impexp_p = colnames_from_index(fao_impexp_p)
cleancolnames(fao_impexp_p)

# Adjust column names
fao_impexp_p.columns = fao_impexp_p.columns.str.replace('__' ,'_')
fao_impexp_p.columns = fao_impexp_p.columns.str.replace('area' ,'country')

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(fao_impexp_p)

fao_impexp_p.to_csv(os.path.join(PRODATA_FOLDER ,'fao_impexp_p.csv'))
fao_impexp_p.to_pickle(os.path.join(PRODATA_FOLDER ,'fao_impexp_p.pkl.gz'))

# =============================================================================
#### Producer Prices
# https://www.fao.org/faostat/en/#data/PP
# =============================================================================
# ----------------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------------
fao_producerprice_imp = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'FAOSTAT_producer_prices_2000_2021.csv'))
cleancolnames(fao_producerprice_imp)
datainfo(fao_producerprice_imp)

# ----------------------------------------------------------------------------
# Reshape so each element_item_unit is its own column
# ----------------------------------------------------------------------------
fao_producerprice_element_items = fao_producerprice_imp[['element' ,'item' ,'unit']].value_counts()

fao_producerprice_p = fao_producerprice_imp.pivot(
    index=['area' ,'year']          # Column(s) to make new index. If blank, uses existing index.
    ,columns=['element' ,'item' ,'unit']       # Column(s) to make new columns
    ,values='value'        # Column to populate rows. Can pass a list, but will create multi-indexed columns.
    )
fao_producerprice_p = fao_producerprice_p.reset_index(drop=False)
fao_producerprice_p = colnames_from_index(fao_producerprice_p)
cleancolnames(fao_producerprice_p)

# Adjust column names
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('__' ,'_')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('area_' ,'country')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('year_' ,'year')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('_lcu_tonne_' ,'_')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('_slc_tonne_' ,'_')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('_usd_tonne_' ,'_')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('_lcu' ,'_lcupertonne')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('_slc' ,'_slcpertonne')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('_usd' ,'_usdpertonne')
fao_producerprice_p.columns = fao_producerprice_p.columns.str.replace('live_weight' ,'livewt')

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(fao_producerprice_p)
# datadesc(fao_producerprice_p ,RAWDATA_FOLDER)

fao_producerprice_p.to_csv(os.path.join(PRODATA_FOLDER ,'fao_producerprice.csv'))
fao_producerprice_p.to_pickle(os.path.join(PRODATA_FOLDER ,'fao_producerprice.pkl.gz'))
