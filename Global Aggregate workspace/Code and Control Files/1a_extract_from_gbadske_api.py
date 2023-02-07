#%% About
'''
We will prefer to get data from the Informatics team API.
For documentation see http://gbadske.org:9000/dataportal/
'''

#%% Packages and functions

import requests as req         # For sending HTTP requests
import inspect
import io
import pandas as pd

# To clean up column names in a dataframe
def cleancolnames(INPUT_DF):
   # Comments inside the statement create errors. Putting all comments at the top.
   # Convert to lowercase
   # Strip leading and trailing spaces, then replace spaces with underscore
   # Replace slashes, parenthesis, and brackets with underscore
   # Replace some special characters with underscore
   # Replace other special characters with words
   INPUT_DF.columns = INPUT_DF.columns.str.lower() \
      .str.strip().str.replace(' ' ,'_' ,regex=False) \
      .str.replace('/' ,'_' ,regex=False).str.replace('\\' ,'_' ,regex=False) \
      .str.replace('(' ,'_' ,regex=False).str.replace(')' ,'_' ,regex=False) \
      .str.replace('[' ,'_' ,regex=False).str.replace(']' ,'_' ,regex=False) \
      .str.replace('{' ,'_' ,regex=False).str.replace('}' ,'_' ,regex=False) \
      .str.replace('!' ,'_' ,regex=False).str.replace('?' ,'_' ,regex=False) \
      .str.replace('-' ,'_' ,regex=False).str.replace('+' ,'_' ,regex=False) \
      .str.replace('^' ,'_' ,regex=False).str.replace('*' ,'_' ,regex=False) \
      .str.replace('.' ,'_' ,regex=False).str.replace(',' ,'_' ,regex=False) \
      .str.replace('|' ,'_' ,regex=False).str.replace('#' ,'_' ,regex=False) \
      .str.replace('>' ,'_gt_' ,regex=False) \
      .str.replace('<' ,'_lt_' ,regex=False) \
      .str.replace('=' ,'_eq_' ,regex=False) \
      .str.replace('@' ,'_at_' ,regex=False) \
      .str.replace('$' ,'_dol_' ,regex=False) \
      .str.replace('%' ,'_pct_' ,regex=False) \
      .str.replace('&' ,'_and_' ,regex=False)
   return None

# To print df.info() with header for readability, and optionally write data info to text file
def datainfo(
      INPUT_DF
      ,OUTFOLDER=None     # String (opt): folder to output {dataname}_info.txt. If None, no file will be created.
   ):
   funcname = inspect.currentframe().f_code.co_name
   dataname = [x for x in globals() if globals()[x] is INPUT_DF][0]
   rowcount = INPUT_DF.shape[0]
   colcount = INPUT_DF.shape[1]
   idxcols = str(list(INPUT_DF.index.names))
   header = f"Data name: {dataname :>26s}\nRows:      {rowcount :>26,}\nColumns:   {colcount :>26,}\nIndex:     {idxcols :>26s}\n"
   divider = ('-'*26) + ('-'*11) + '\n'
   bigdivider = ('='*26) + ('='*11) + '\n'
   print(bigdivider + header + divider)
   INPUT_DF.info()
   print(divider + f"End:       {dataname:>26s}\n" + bigdivider)

   if OUTFOLDER:     # If something has been passed to OUTFOLDER parameter
      filename = f"{dataname}_info"
      print(f"\n<{funcname}> Creating file {OUTFOLDER}\{filename}.txt")
      datetimestamp = 'Created on ' + time.strftime('%Y-%m-%d %X', time.gmtime()) + ' UTC' + '\n'
      buffer = io.StringIO()
      INPUT_DF.info(buf=buffer, max_cols=colcount)
      filecontents = header + divider + datetimestamp + buffer.getvalue()
      tofile = os.path.join(OUTFOLDER, f"{filename}.txt")
      with open(tofile, 'w', encoding='utf-8') as f: f.write(filecontents)
      print(f"<{funcname}> ...done.")
   return None

#%% View tables and field names

# =============================================================================
#### Get list of all available tables
# =============================================================================
gbadske_tablelist_uri = 'http://gbadske.org:9000/GBADsTables/public?format=text'
gbadske_tablelist = req.get(gbadske_tablelist_uri).text.split(',')   # Get table list and convert to list

# ----------------------------------------------------------------------------
# Lookup the column names in a specific table
# ----------------------------------------------------------------------------
gbadske_fieldnames_uri = 'http://gbadske.org:9000/GBADsTable/public'

# Return the column names for a table
# Usage: table_columns = gbadske_get_column_names(table)
def gbadske_get_column_names(
        TABLE_NAME          # String: name of table
        ,RESP_TYPE='list'   # String: 'list' returns a list, 'string' returns a string
    ):
    fieldnames_params = {
       'table_name':TABLE_NAME
       ,'format':'text'
       }
    fieldnames_str = req.get(gbadske_fieldnames_uri , params=fieldnames_params).text
    fieldnames_list = req.get(gbadske_fieldnames_uri , params=fieldnames_params).text.split(',')
    if RESP_TYPE == 'list':
        return fieldnames_list
    elif RESP_TYPE == 'string':
        return fieldnames_str

#%% Retrieve a table

gbadske_query_uri = 'http://gbadske.org:9000/GBADsPublicQuery/'

# -----------------------------------------------------------------------------
# Pieces
# -----------------------------------------------------------------------------
# gbadske_query_table_name = 'livestock_countries_biomass'
# gbadske_query_params = {
#     'fields':gbadske_get_column_names(gbadske_query_table_name ,'string')   # All columns in table
#     ,'query':"year=2017 AND member_country='Australia'"     # Note character column value must be in SINGLE QUOTES (double quotes don't work)
#     ,'format':'file'
#     }
# gbadske_query_resp = req.get(gbadske_query_uri + gbadske_query_table_name , params=gbadske_query_params)

# # Read table into pandas dataframe
# gbadske_query_df = pd.read_csv(io.StringIO(gbadske_query_resp.text))

# -----------------------------------------------------------------------------
# Function
# -----------------------------------------------------------------------------
# Return a table as a pandas dataframe
# Usage: table_df = gbadske_import_to_pandas(tablename)
def gbadske_import_to_pandas(
        TABLE_NAME      # String: name of table
        ,QUERY=""       # String (optional): data query in DOUBLE QUOTES. Values for character columns value must be in SINGLE QUOTES e.g. QUERY="year=2017 AND member_country='Australia'".
    ):
    funcname = inspect.currentframe().f_code.co_name
    query_params = {
        'fields':gbadske_get_column_names(TABLE_NAME ,'string')
        ,'query':QUERY
        ,'format':'file'
        }
    query_resp = req.get(gbadske_query_uri + TABLE_NAME , params=query_params)

    if query_resp.status_code == 200:
        query_df = pd.read_csv(io.StringIO(query_resp.text))    # Read table into pandas dataframe
    else:
        print(f'<{funcname}> HTTP query error.')
        query_df = pd.DataFrame()

    return query_df

#%% Get tables needed for AHLE

get_years = range(2000 ,2022)

# =============================================================================
#### livestock_countries_biomass
# 2022-8-4: Guelph says this is the correct table to use
# =============================================================================
# Get data for range of years
livestock_countries_biomass_cols = gbadske_get_column_names('livestock_countries_biomass')
livestock_countries_biomass = pd.DataFrame()    # Initialize
for i in get_years:
    single_year = gbadske_import_to_pandas('livestock_countries_biomass' ,QUERY=f"year={i}")
    livestock_countries_biomass = pd.concat([livestock_countries_biomass ,single_year] ,ignore_index=True)

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
# Change columns to numeric
convert_cols_to_numeric = ['year' ,'population' ,'biomass']
for COL in convert_cols_to_numeric:
    livestock_countries_biomass[COL] = pd.to_numeric(livestock_countries_biomass[COL] ,errors='coerce')  # Use to_numeric to handle remaining values like ':'

# For Ducks, liveweight is in grams. Change to kg.
_row_selection = (livestock_countries_biomass['species'].str.upper() == 'DUCKS') & (livestock_countries_biomass['liveweight'] > 1000)
print(f"> Selected {_row_selection.sum(): ,} rows.")
livestock_countries_biomass.loc[_row_selection ,'liveweight'] = livestock_countries_biomass.loc[_row_selection ,'liveweight'] / 1000

# Recalculate biomass as population * liveweight
livestock_countries_biomass.loc[_row_selection ,'biomass'] = \
    livestock_countries_biomass.loc[_row_selection ,'liveweight'] * livestock_countries_biomass.loc[_row_selection ,'population']

# Remove duplicates (country-species-year combinations that appear twice)
csy_counts = livestock_countries_biomass[['country' ,'species' ,'year']].value_counts()
biomass_countries = list(livestock_countries_biomass['country'].unique())
livestock_countries_biomass = livestock_countries_biomass.drop_duplicates(
   subset=['country' ,'species' ,'year']          # List (opt): only consider these columns when identifying duplicates. If None, consider all columns.
   ,keep='first'                   # String: which occurrence to keep, 'first' or 'last'
)

datainfo(livestock_countries_biomass)

lcb_years = livestock_countries_biomass['year'].value_counts()

# Profile
# profile = livestock_countries_biomass.profile_report()
# profile.to_file(os.path.join(RAWDATA_FOLDER ,'livestock_countries_biomass_profile.html'))

# Export
livestock_countries_biomass.to_csv(os.path.join(RAWDATA_FOLDER ,'livestock_countries_biomass.csv') ,index=False)
livestock_countries_biomass.to_pickle(os.path.join(PRODATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))

# =============================================================================
#### livestock_countries_biomass_oie
# 2023-1-9: Liverpool wants to use the WOAH/OIE biomass numbers
# =============================================================================
# Get data for range of years
livestock_countries_biomass_oie_cols = gbadske_get_column_names('livestock_countries_biomass_oie')
livestock_countries_biomass_oie = pd.DataFrame()    # Initialize
for i in get_years:
    single_year = gbadske_import_to_pandas('livestock_countries_biomass_oie' ,QUERY=f"year={i}")
    livestock_countries_biomass_oie = pd.concat([livestock_countries_biomass_oie ,single_year] ,ignore_index=True)

lcbo_years = livestock_countries_biomass_oie['year'].value_counts()

# =============================================================================
#### biomass_oie
# 2023-1-9: Liverpool wants to use the WOAH/OIE biomass numbers
# =============================================================================
# Get data for range of years
biomass_oie_cols = gbadske_get_column_names('biomass_oie')
biomass_oie = pd.DataFrame()    # Initialize
for i in get_years:
    single_year = gbadske_import_to_pandas('biomass_oie' ,QUERY=f"year={i}")
    biomass_oie = pd.concat([biomass_oie ,single_year] ,ignore_index=True)

bo_years = biomass_oie['year'].value_counts()

# Describe frequency of sources by year
bo_sources = biomass_oie[['animal_category', 'year', 'source_data']].value_counts()

# =============================================================================
#### biomass_live_weight_fao
# This update to the biomass data has been downloaded from an Informatics team
# repository containing data that has not yet been added to the public API.
# https://github.com/GBADsInformatics/PPSTheme
# =============================================================================
biomass_live_weight_fao = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'20230116_biomass_live_weight_fao.csv'))
biomass_live_weight_fao = biomass_live_weight_fao.rename(columns={"country_x":"country" ,"live_weight":"liveweight"})

# Limit to same years as other tables
biomass_live_weight_fao = biomass_live_weight_fao.loc[biomass_live_weight_fao['year'].isin(get_years)]

datainfo(biomass_live_weight_fao)

# Compare to livestock_countries_biomass
check_lcb_vs_blw = pd.merge(
    left=livestock_countries_biomass
    ,right=biomass_live_weight_fao
    ,on=['iso3' ,'species' ,'year']
    ,how='outer'
    ,indicator=True
)
datainfo(check_lcb_vs_blw)

check_lcb_vs_blw['_merge'].value_counts()

check_lcb_vs_blw_specyear = check_lcb_vs_blw.pivot_table(
    index=['species' ,'year']
    ,values=['biomass_x' ,'biomass_y']
    ,aggfunc=['count' ,'sum']
    )

# Export
biomass_live_weight_fao.to_csv(os.path.join(RAWDATA_FOLDER ,'biomass_live_weight_fao.csv') ,index=False)
biomass_live_weight_fao.to_pickle(os.path.join(PRODATA_FOLDER ,'biomass_live_weight_fao.pkl.gz'))

# =============================================================================
#### livestock_national_population_biomass_faostat
# 2022-8-4: Guelph says this is out of date
# =============================================================================
# Get data for range of years
# biomass_faostat_cols = gbadske_get_column_names('livestock_national_population_biomass_faostat')
# biomass_faostat = pd.DataFrame()    # Initialize
# for i in get_years:
#     single_year = gbadske_import_to_pandas('livestock_national_population_biomass_faostat' ,QUERY=f"year={i}")
#     biomass_faostat = pd.concat([biomass_faostat ,single_year] ,ignore_index=True)

# Profile
# profile = biomass_faostat.profile_report()
# profile.to_file(os.path.join(RAWDATA_FOLDER ,'biomass_faostat_profile.html'))

# Export
# biomass_faostat.to_csv(os.path.join(RAWDATA_FOLDER ,'livestock_national_population_biomass_faostat.csv') ,index=False)
# biomass_faostat.to_pickle(os.path.join(PRODATA_FOLDER ,'biomass_faostat.pkl.gz'))

# =============================================================================
#### World Bank
# =============================================================================
wb_income = pd.DataFrame()    # Initialize
for i in get_years:
    single_year = gbadske_import_to_pandas('countries_incomegroups_worldbank' ,QUERY=f"year={i}")
    wb_income = pd.concat([wb_income ,single_year] ,ignore_index=True)

datainfo(wb_income)

wb_region = gbadske_import_to_pandas('regions_worldbank')
datainfo(wb_region)

# Export
wb_income.to_csv(os.path.join(RAWDATA_FOLDER ,'wb_income.csv') ,index=False)
wb_income.to_pickle(os.path.join(PRODATA_FOLDER ,'wb_income.pkl.gz'))

wb_region.to_csv(os.path.join(RAWDATA_FOLDER ,'wb_region.csv') ,index=False)
wb_region.to_pickle(os.path.join(PRODATA_FOLDER ,'wb_region.pkl.gz'))

# =============================================================================
#### Geo codes
# =============================================================================
un_geo_codes = gbadske_import_to_pandas('un_geo_codes')
datainfo(un_geo_codes)

# Export
un_geo_codes.to_csv(os.path.join(RAWDATA_FOLDER ,'un_geo_codes.csv') ,index=False)
un_geo_codes.to_pickle(os.path.join(PRODATA_FOLDER ,'un_geo_codes.pkl.gz'))

# =============================================================================
#### countries_adminunits_iso
# =============================================================================
# check_admin = gbadske_import_to_pandas('countries_adminunits_iso')

gbadske_query_table_name = 'countries_adminunits_iso'
gbadske_query_params = {
    'fields':gbadske_get_column_names(gbadske_query_table_name ,'string')   # All columns in table
    ,'query':""     # Note character column value must be in SINGLE QUOTES (double quotes don't work)
    ,'format':'file'
    }
gbadske_query_resp = req.get(gbadske_query_uri + gbadske_query_table_name , params=gbadske_query_params)

# =============================================================================
#### Check others
# =============================================================================
# check_faoprod = gbadske_import_to_pandas('livestock_production_faostat' ,"year=2019")
# check_faoprodanimals = gbadske_import_to_pandas('prodanimals_national_faostat' ,"year=2019")
# check_idtable = gbadske_import_to_pandas('idtable')
# check_country_info = gbadske_import_to_pandas('country_info')

#%% Create summaries

# =============================================================================
#### Write table list to Excel
# =============================================================================
# timerstart('Table and column lists')
# with pd.ExcelWriter(os.path.join(RAWDATA_FOLDER ,'gbadske_tables_20220801.xlsx')) as writer:
#     # First sheet: table list
#     gbadske_tablelist_df = pd.DataFrame({'table_name':gbadske_tablelist})
#     gbadske_tablelist_df.to_excel(writer ,sheet_name='Table List' ,index=False)

#     # Subsequent sheets: column list for each table
#     for table in gbadske_tablelist:
#         print(f'> Processing table {table}')
#         collist = gbadske_get_column_names(table)
#         collist_df = pd.DataFrame({'column_name':collist})
#         sheetname = table.replace('population' ,'pop')
#         sheetname_short = sheetname[0:31]     # Sheet name must be <= 31 characters
#         collist_df.to_excel(writer, sheet_name=sheetname_short ,index=False)

# del collist ,collist_df
# timerstop()

# =============================================================================
#### Write sample of each table to Excel
#!!! Run time 3 hours!!
# When run without a table query (e.g. year=2018), the gbadske API takes a long time to respond
# =============================================================================
# timerstart('Sample of rows from each table')
# with pd.ExcelWriter(os.path.join(RAWDATA_FOLDER ,'gbadske_tables_100rows_20220801.xlsx')) as writer:
#     for table in gbadske_tablelist:
#         print(f'> Processing table {table}')
#         if 'eth' not in table:      # Exclude Ethiopia-specific tables
#             try:
#                 table_df = gbadske_import_to_pandas(table).head(100)
#             except:
#                 table_df = pd.DataFrame({'Status':'Error reading table'} ,index=[0])
#             sheetname = table.replace('population' ,'pop')
#             sheetname_short = sheetname[0:31]     # Sheet name must be <= 31 characters
#             table_df.to_excel(writer, sheet_name=sheetname_short ,index=False)

# del table_df
# timerstop()
