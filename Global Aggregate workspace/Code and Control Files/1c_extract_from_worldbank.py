#%% About
'''
This imports CPI and exchange rate data from the World Bank, which is not available
in the GBADs data portal.
'''
#%% Import

wb_infl_exchg = pd.read_csv(os.path.join(RAWDATA_FOLDER
                                         ,'worldbank_cpi_exchg_2000_2021'
                                         ,'598d23ae-3692-40f3-a27b-394e568cb82a_Data.csv'
                                         )
                            )
cleancolnames(wb_infl_exchg)

# Rename
rename_cols = {
    'country_name':'country'
    ,'country_code':'iso3'
    ,'time':'year'
    ,'time_code':'time_code'
    ,'consumer_price_index__2010__eq__100___fp_cpi_totl_':'cpi_2010idx'
    ,'inflation__gdp_deflator__annual__pct____ny_gdp_defl_kd_zg_':'inflation_pct_gdpdef'
    ,'inflation__gdp_deflator:_linked_series__annual__pct____ny_gdp_defl_kd_zg_ad_':'inflation_pct_gdpdef_lnk'
    ,'inflation__consumer_prices__annual__pct____fp_cpi_totl_zg_':'inflation_pct_cp'
    ,'official_exchange_rate__lcu_per_us_dol___period_average___pa_nus_fcrf_':'exchg_lcuperusd'
}
wb_infl_exchg = wb_infl_exchg.rename(columns=rename_cols)

# Change columns to numeric
convert_cols_to_numeric = [
    'cpi_2010idx'
    ,'inflation_pct_gdpdef'
    ,'inflation_pct_gdpdef_lnk'
    ,'inflation_pct_cp'
    ,'exchg_lcuperusd'
]
for COL in convert_cols_to_numeric:
    wb_infl_exchg[COL] = pd.to_numeric(wb_infl_exchg[COL] ,errors='coerce')  # Use to_numeric to handle remaining values like ':'

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(wb_infl_exchg)

wb_infl_exchg.to_csv(os.path.join(PRODATA_FOLDER ,'wb_infl_exchg.csv'))
wb_infl_exchg.to_pickle(os.path.join(PRODATA_FOLDER ,'wb_infl_exchg.pkl.gz'))
