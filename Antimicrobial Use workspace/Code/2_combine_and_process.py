#%% About
'''
'''
#%% Functions

# Translate a PERT distribution to the equivalent Beta
# Output a dataframe with samples generated from the distribution and a histogram
# Usage: pert_samples = generate_pert(10000, 1, 8, 10)
def generate_pert(N_SAMPLES ,MIN ,MODE ,MAX ,LAMBDA=4):
    funcname = inspect.currentframe().f_code.co_name

    mean = (MIN + (LAMBDA * MODE) + MAX) / (LAMBDA + 2)
    alpha = (mean - MIN) * (2*MODE - MIN - MAX) / ((MODE - mean) * (MAX - MIN))
    beta = alpha * (MAX - mean) / (mean - MIN)

    print(f"<{funcname}> PERT distribution: ({MIN}, {MODE}, {MAX}) with lambda={LAMBDA}")
    print(f"<{funcname}> Equivalent Beta distribution: {alpha=:.3f}, {beta=:.3f}")

    # Generate samples
    beta_distr = sps.beta(alpha ,beta)
    generated_df = pd.DataFrame(index=range(N_SAMPLES))
    generated_df['rand_beta'] = beta_distr.rvs(size=generated_df.shape[0])      # Generate random numbers from Beta distribution (on scale 0,1)
    generated_df['rand_pert'] = (generated_df['rand_beta'] * (MAX - MIN)) + MIN   # Translate from (0,1) to scale of PERT

    # Plot
    snplt = sns.displot(
    	data=generated_df
    	,x='rand_pert'
    	,kind='hist'
        ,stat='probability'
        ,bins=20
    )
    plt.title(f"PERT({MIN}, {MODE}, {MAX}) with lambda={LAMBDA}\n Recreated as Beta({alpha:.2f}, {beta:.2f})\n {N_SAMPLES:,} samples")

    return generated_df

pert_samples = generate_pert(10000, 1, 8, 10)

# Translate a PERT distribution to the equivalent Beta
# Output the beta distribution object for further processing
def pert_to_beta(MIN ,MODE ,MAX ,LAMBDA=4):
    funcname = inspect.currentframe().f_code.co_name

    mean = (MIN + (LAMBDA * MODE) + MAX) / (LAMBDA + 2)
    alpha = (mean - MIN) * (2*MODE - MIN - MAX) / ((MODE - mean) * (MAX - MIN))
    beta = alpha * (MAX - mean) / (mean - MIN)
    beta_distr = sps.beta(alpha ,beta)

    print(f"<{funcname}> PERT distribution: ({MIN}, {MODE}, {MAX}) with lambda={LAMBDA}")
    print(f"<{funcname}> Equivalent Beta distribution: {alpha=:.3f}, {beta=:.3f}")

    return beta_distr

beta_distr = pert_to_beta(1, 8, 10)

# Endpoints of the range that contains alpha percent of the distribution
beta_distr_ci95 = beta_distr.interval(0.95)
pert_distr_ci95_low = (beta_distr_ci95[0] * (10 - 1)) + 1   # Translate from (0,1) to scale of PERT
pert_distr_ci95_high = (beta_distr_ci95[1] * (10 - 1)) + 1   # Translate from (0,1) to scale of PERT

#%% Structure: one row per region & antimicrobial

# =============================================================================
#### Prepare AM usage
# =============================================================================
amu2018_m_tomerge = amu2018_m.copy()

# =============================================================================
#### Add importance
# =============================================================================
# Modify antimicrobial names in importance data to match
amu_importance_tomerge = amu_importance.copy()

# Remove special characters from class names
amu_importance_tomerge['antimicrobial_class'] = amu_importance_tomerge['antimicrobial_class'].str.lower() \
   .str.strip().str.replace(' ' ,'_' ,regex=False) \
   .str.replace('/' ,'_' ,regex=False).str.replace('\\' ,'_' ,regex=False) \
   .str.replace('(' ,'_' ,regex=False).str.replace(')' ,'_' ,regex=False) \
   .str.replace('-' ,'_' ,regex=False).str.replace('+' ,'_' ,regex=False) \
   .str.replace('.' ,'_' ,regex=False).str.replace(',' ,'_' ,regex=False) \

# Recode classes to match AMU data
recode_classes = {
    'cephalosporins__all_generations_':'cephalosporins__all_generations'
    ,'sulfonamids':'sulfonamides__including_trimethoprim'
    }
amu_importance_tomerge['antimicrobial_class'] = amu_importance_tomerge['antimicrobial_class'].replace(recode_classes)

datainfo(amu_importance_tomerge)

# Merge with AMU
amu2018_combined_tall = pd.merge(
    left=amu2018_m_tomerge.query("antimicrobial_class != 'total_antimicrobials'").query("region != 'Global'")
    ,right=amu_importance_tomerge[['antimicrobial_class' ,'who_importance_ctg' ,'woah_importance_ctg' ,'onehealth_importance_ctg']]
    ,on='antimicrobial_class'
    ,how='left'
)

# Fill missing importance with "Unknown"
amu2018_combined_tall['who_importance_ctg'] = amu2018_combined_tall['who_importance_ctg'].fillna('D: Unknown')
amu2018_combined_tall['woah_importance_ctg'] = amu2018_combined_tall['woah_importance_ctg'].fillna('D: Unknown')
amu2018_combined_tall['onehealth_importance_ctg'] = amu2018_combined_tall['onehealth_importance_ctg'].fillna('Unknown')

# =============================================================================
#### Create antimicrobial class groupings
# =============================================================================
# Group the AM classes that individually make up less than 2% of the global total usage
# Groupings must still respect importance categories
amu_total_byclass = amu2018_m_tomerge.query("antimicrobial_class != 'total_antimicrobials'").query("region == 'Global'").query("scope == 'All'")
amu_total_byclass['usage_rank_lowis1'] = amu_total_byclass['amu_tonnes'].rank()
amu_total_byclass['usage_rank_highis1'] = amu_total_byclass['amu_tonnes'].rank(ascending=False)

global_total_amu_tonnes = amu_total_byclass['amu_tonnes'].sum()
low_volume_classes = list(amu_total_byclass.query(f"amu_tonnes < {global_total_amu_tonnes} * 0.02")['antimicrobial_class'])

def define_class_group(INPUT_ROW):
	if INPUT_ROW['antimicrobial_class'] in low_volume_classes:
		if 'Important' in INPUT_ROW['onehealth_importance_ctg']:
			OUTPUT = 'other_important'
		else:
			OUTPUT = 'other'
	else:
		OUTPUT = INPUT_ROW['antimicrobial_class']
	return OUTPUT
amu2018_combined_tall['antimicrobial_class_group'] = amu2018_combined_tall.apply(define_class_group ,axis=1)

# Further grouping: top 3 classes by global usage vs. everything else
# Regardless of importance category
top3_globally = list(amu_total_byclass.query(f"usage_rank_highis1 <= 3 ")['antimicrobial_class'])
amu2018_combined_tall['antimicrobial_class_group2'] = 'others'
amu2018_combined_tall.loc[amu2018_combined_tall['antimicrobial_class'].isin(top3_globally) ,'antimicrobial_class_group2'] = \
    amu2018_combined_tall['antimicrobial_class']

# =============================================================================
#### Add biomass data
# =============================================================================
# Pivot Biomass to get countries reporting and total region into columns
# Keep total biomass and terrestrial biomass
amu2018_biomass_p = amu2018_biomass.query("region != 'Global'").pivot(
    index='region'
    ,columns='segment'
    ,values=['biomass_total_kg' ,'biomass_total_terr_kg']
)
amu2018_biomass_p = colnames_from_index(amu2018_biomass_p) 	# If multi-indexed columns were created, flatten index
cleancolnames(amu2018_biomass_p)
amu2018_biomass_p = amu2018_biomass_p.reset_index()           # Pivoting will change columns to indexes. Change them back.
amu2018_biomass_p = amu2018_biomass_p.rename(
    columns={
        "biomass_total_kg_countries_reporting_amu_data":"biomass_total_kg_reporting"
        ,"biomass_total_kg_total_region":"biomass_total_kg_region"
        ,"biomass_total_terr_kg_countries_reporting_amu_data":"biomass_terr_kg_reporting"
        ,"biomass_total_terr_kg_total_region":"biomass_terr_kg_region"
        }
)
datainfo(amu2018_biomass_p)

# Merge
amu2018_combined_tall = pd.merge(
    left=amu2018_combined_tall
    # ,right=amu2018_biomass.query("segment == 'Countries reporting AMU data'")[['region' ,'biomass_total_kg' ,'biomass_total_terr_kg']]
    ,right=amu2018_biomass_p
    ,on='region'
    ,how='left'
)

# Apply appropriate biomass to each row based on scope
def biomass_for_scope(INPUT_ROW):
    if INPUT_ROW['scope'].upper() == 'ALL':
        reporting = INPUT_ROW['biomass_total_kg_reporting']
        region = INPUT_ROW['biomass_total_kg_region']
    elif INPUT_ROW['scope'].upper() == 'TERRESTRIAL FOOD PRODUCING':
        reporting = INPUT_ROW['biomass_terr_kg_reporting']
        region = INPUT_ROW['biomass_terr_kg_region']
    else:
        reporting = np.nan
        region = np.nan
    return pd.Series([reporting ,region])
amu2018_combined_tall[['biomass_total_kg_reporting' ,'biomass_total_kg_region']] = amu2018_combined_tall.apply(biomass_for_scope ,axis=1)
amu2018_combined_tall = amu2018_combined_tall.drop(columns=['biomass_terr_kg_reporting' ,'biomass_terr_kg_region'])

amu2018_combined_tall['biomass_prpn_reporting'] = amu2018_combined_tall['biomass_total_kg_reporting'] / amu2018_combined_tall['biomass_total_kg_region']

# Calculate AMU per kg biomass
amu2018_combined_tall['amu_mg_perkgbiomass'] = (amu2018_combined_tall['amu_tonnes'] / amu2018_combined_tall['biomass_total_kg_reporting']) * 1e9

# =============================================================================
#### Export
# =============================================================================
datainfo(amu2018_combined_tall)

amu2018_combined_tall.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_combined_tall.csv') ,index=False)
amu2018_combined_tall.to_csv(os.path.join(DASH_DATA_FOLDER ,'amu2018_combined_tall.csv') ,index=False)

#%% Structure: one row per region

# =============================================================================
#### Combine biomass and AM usage
# =============================================================================
# Pivot Biomass to get countries reporting and total region into columns
# Keep total biomass and terrestrial biomass
amu2018_biomass_p = amu2018_biomass.query("region != 'Global'").pivot(
    index='region'
    ,columns='segment'
    ,values=['biomass_total_kg' ,'biomass_total_terr_kg']
)
amu2018_biomass_p = colnames_from_index(amu2018_biomass_p) 	# If multi-indexed columns were created, flatten index
cleancolnames(amu2018_biomass_p)
amu2018_biomass_p = amu2018_biomass_p.reset_index()           # Pivoting will change columns to indexes. Change them back.

amu2018_biomass_p = amu2018_biomass_p.rename(
    columns={
        "biomass_total_kg_countries_reporting_amu_data":"biomass_total_kg_reporting"
        ,"biomass_total_kg_total_region":"biomass_total_kg_region"
        ,"biomass_total_terr_kg_countries_reporting_amu_data":"biomass_terr_kg_reporting"
        ,"biomass_total_terr_kg_total_region":"biomass_terr_kg_region"
        }
)
datainfo(amu2018_biomass_p)

# Merge usage and biomass
# Keep total usage, drop antimicrobial-specific usage
amu_combined_regional = pd.merge(
    left=amu2018.query("scope == 'All'").query("region != 'Global'")[['region' ,'number_of_countries' ,'total_antimicrobials_tonnes']]
    ,right=amu2018_biomass_p
    ,on='region'
    ,how='left'
)

# -----------------------------------------------------------------------------
# Find proportion of AM usage going to terrestrial food producing animals
# -----------------------------------------------------------------------------
# Calculate proportion of biomass
amu_combined_regional['biomass_terr_prpn_reporting'] = amu_combined_regional['biomass_terr_kg_reporting'] / amu_combined_regional['biomass_total_kg_reporting']
amu_combined_regional['terr_amu_tonnes_reporting'] = amu_combined_regional['total_antimicrobials_tonnes'] * amu_combined_regional['biomass_terr_prpn_reporting']

# -----------------------------------------------------------------------------
# Adjust for 2020
# -----------------------------------------------------------------------------
# Based on 2016-2018 trends
# Source: https://www.woah.org/app/uploads/2022/06/a-sixth-annual-report-amu-final-1.pdf
# "All OIE Regions presented a decrease as follows:
#    13% in Africa; 28% in the Americas; 30% in Asia, Far East and Oceania; and 18% in Europe."
# No regional trend available for Middle East. Using global average of 27% decrease.
amu_2020_adjustment = pd.DataFrame(
    {"region":['Africa' ,'Americas' ,'Asia, Far East and Oceania' ,'Europe' ,'Middle East']
     ,"prpn_change_2018to2020":[-0.13 ,-0.28 ,-0.30 ,-0.18 ,-0.27]
     }
)
amu_combined_regional = pd.merge(
    left=amu_combined_regional
    ,right=amu_2020_adjustment
    ,on='region'
    ,how='left'
)
amu_combined_regional['terr_amu_tonnes_reporting_2020'] = \
    amu_combined_regional['terr_amu_tonnes_reporting'] * (1 + amu_combined_regional['prpn_change_2018to2020'])
datainfo(amu_combined_regional)

# -----------------------------------------------------------------------------
# Add estimate of region-total AMU by extrapolating from the countries reporting
# -----------------------------------------------------------------------------
# Terrestrial biomass among countries reporting as proportion of whole region
amu_combined_regional['biomass_terr_reporting_prpnofregion'] =\
    amu_combined_regional['biomass_terr_kg_reporting'] / amu_combined_regional['biomass_terr_kg_region']

amu_combined_regional['terr_amu_tonnes_region_2020'] =\
    amu_combined_regional['terr_amu_tonnes_reporting_2020'] / amu_combined_regional['biomass_terr_reporting_prpnofregion']

# All species
amu_combined_regional['biomass_total_reporting_prpnofregion'] =\
    amu_combined_regional['biomass_total_kg_reporting'] / amu_combined_regional['biomass_total_kg_region']

amu_combined_regional['total_antimicrobials_tonnes_region'] =\
    amu_combined_regional['total_antimicrobials_tonnes'] / amu_combined_regional['biomass_total_reporting_prpnofregion']

datainfo(amu_combined_regional)

# =============================================================================
#### Add Mulchandani data
# =============================================================================
# Sum Mulchandani to region level
amu_mulch_regional = amu_mulch_withrgn.pivot_table(
    index='woah_region'
# 	,values=['tonnes2020' ,'tonnes2030' ,'pcu__kg__2020' ,'pcu__kg__2030']
	,values='tonnes2020'
	,aggfunc='sum'
)

# Recalculate usage per PCU
# amu_mulch_regional['mgpcu_2020'] = amu_mulch_regional['tonnes2020'] * 1e9 / amu_mulch_regional['pcu__kg__2020']
# amu_mulch_regional['mgpcu_2030'] = amu_mulch_regional['tonnes2030'] * 1e9 / amu_mulch_regional['pcu__kg__2030']

amu_mulch_regional = amu_mulch_regional.rename(
    columns={
        "tonnes2020":"terr_amu_tonnes_mulch_2020"
        }
)
datainfo(amu_mulch_regional)

# Merge
amu_combined_regional = pd.merge(
    left=amu_combined_regional
    ,right=amu_mulch_regional
    ,left_on='region'
    ,right_on='woah_region'
    ,how='left'
)
datainfo(amu_combined_regional)

# =============================================================================
#### Add prices
# =============================================================================
amu_combined_regional = pd.merge(
    left=amu_combined_regional
    ,right=amu_prices
    ,on='region'
    ,how='left'
)
datainfo(amu_combined_regional)

# =============================================================================
#### Add AMR
# =============================================================================
# -----------------------------------------------------------------------------
# DEV: Calculating weighted average for each class
# Next I'll do this after combining classes to match the AMU data
# -----------------------------------------------------------------------------
# amr_full_withrgn_working = amr_full_withrgn.copy()
# datainfo(amr_full_withrgn_working)

# # Add resistance weighted by number of isolates for each pathogen
# amr_full_withrgn_working['nisolates_resistant'] = amr_full_withrgn_working['rescom'] * amr_full_withrgn_working['nisolates']

# # Aggregate to region, year, pathogen, antimicrobial class level
# amr_full_regional = amr_full_withrgn_working.pivot_table(
#     index=['woah_region' ,'reporting_year' ,'pathogen' ,'antibiotic_class']
#     ,values=['nisolates_resistant' ,'nisolates']
#     ,aggfunc='sum'
# )
# amr_full_regional = amr_full_regional.add_suffix('_sum')
# amr_full_regional = amr_full_regional.reset_index()
# amr_full_regional['rescom_wtavg'] = amr_full_regional['nisolates_resistant_sum'] / amr_full_regional['nisolates_sum']

# -----------------------------------------------------------------------------
# Get resistance of each antibiotic class in each region
# - Problem: Drugs in AMR data are not a strict subset of drugs in AMU
# - E.g. Polymyxins, Carbapenems appear in AMR but not AMU. We don’t know what proportion of usage these make up.
# -- For now, assume these are in "Other"
# - What about Aminopenicillins in AMR data?
# -- Include in Penicillins in AMU
# -----------------------------------------------------------------------------
amr_full_withrgn_working = amr_full_withrgn.copy()

# Add resistance weighted by number of isolates for each pathogen
amr_full_withrgn_working['nisolates_resistant'] = amr_full_withrgn_working['rescom'] * amr_full_withrgn_working['nisolates']

# Rename classes in AMR data to match AMU
amr_full_withrgn_working['antibiotic_class'].unique()
rename_amr_classes = {
    '1st Generation Cephalosporin':'cephalosporins__all_generations'
    ,'2nd Generation Cephalosporin':'cephalosporins__all_generations'
    ,'Third generation cephalosporins':'cephalosporins__all_generations'
    ,'Fourth generation cephalosporins':'cephalosporins__all_generations'
    ,'5th Generation Cephalosporin':'cephalosporins__all_generations'

    ,'Amidinopenicillins':'penicillins'
    ,'Aminocyclitols':'others'
    ,'Aminoglycosides':'aminoglycosides'
    ,'Aminopenicillins with beta-lactamase inhibitors':'penicillins'
    ,'Aminopenicillins with Penicillins':'penicillins'
    ,'Aminopenicillins':'penicillins'
    ,'Amphenicols':'amphenicols'
    ,'Ansamycins':'others'
    ,'Carbapenems':'others'
    ,'Cephamycin':'others'
    ,'Cyclic Polypeptides':'polypeptides'
    ,'Fluoroquinolones':'fluoroquinolones'
    ,'Glycopeptides':'glycopeptides'
    ,'Glycylcyclines':'others'
    ,'Ionophore':'others'
    ,'Lincosamides':'lincosamides'
    ,'Lipopeptides':'others'
    ,'Macrolides':'macrolides'
    ,'Monobactams':'others'
    ,'Nitrofurans':'nitrofurans'
    ,'Nitroimidazoles':'others'
    ,'Oxazolidinones':'others'
    ,'Penicillins (Anti-Staphylococcal)':'penicillins'
    ,'Penicillins (Narrow Spectrum)':'penicillins'
    ,'Penicillins':'penicillins'
    ,'Phosphonic acid derivatives':'others'
    ,'Polymyxins':'others'
    ,'Pseudomonic Acids':'others'
    ,'Quinolones':'other_quinolones'
    ,'Steroid Antibacterials':'others'
    ,'Streptogramins':'streptogramins'
    ,'Sulfonamides, Trimethoprim and Combinations':'sulfonamides__including_trimethoprim'
    ,'Tetracyclines':'tetracyclines'
}
amr_full_withrgn_working['antibiotic_class'] = amr_full_withrgn_working['antibiotic_class'].replace(rename_amr_classes)

# Calculate class-level average resistance for classes to match AMU
amr_full_p1 = amr_full_withrgn_working.pivot_table(
    index=['woah_region' ,'reporting_year' ,'pathogen' ,'antibiotic_class']
    ,values=['nisolates_resistant' ,'nisolates']
    ,aggfunc='sum'
)
amr_full_p1 = amr_full_p1.add_suffix('_sum')
amr_full_p1 = amr_full_p1.reset_index()
amr_full_p1['resistance_rate'] = amr_full_p1['nisolates_resistant_sum'] / amr_full_p1['nisolates_sum']

# -----------------------------------------------------------------------------
# Lookup frequency of use of each antibiotic_class as proportion of region total AMU
# -----------------------------------------------------------------------------
amu2018_m_classprev = amu2018_m.query("scope == 'All'").query("antimicrobial_class != 'total_antimicrobials'").copy()

# Combine classes in AMU to make the best use of data (e.g. combine all cephalosporins into cephalosporins__all_generations)
combine_amu_classes = {
    '1_2_gen__cephalosporins':'cephalosporins__all_generations'
    ,'3_4_gen_cephalosporins':'cephalosporins__all_generations'
}
amu2018_m_classprev['antimicrobial_class'] = amu2018_m_classprev['antimicrobial_class'].replace(combine_amu_classes)
amu2018_m_classprev['antimicrobial_class'].unique()

# Sum usage at combined class level
amu2018_m_classprev = amu2018_m_classprev.groupby(['region' ,'scope' ,'number_of_countries' ,'antimicrobial_class'])['amu_tonnes'].sum().reset_index()

# Add region total AMU as a column and calculate usage of each class as proportion of total
amu2018_m_classprev['region_total_amu_tonnes'] = amu2018_m_classprev.groupby('region')['amu_tonnes'].transform('sum')
amu2018_m_classprev['region_prpn_amu'] = amu2018_m_classprev['amu_tonnes'] / amu2018_m_classprev['region_total_amu_tonnes']

# Merge onto AMR
amr_full_p1_classprpn = pd.merge(
    left=amr_full_p1
    ,right=amu2018_m_classprev[['region' ,'antimicrobial_class' ,'region_prpn_amu']]
    ,left_on=['woah_region' ,'antibiotic_class']
    ,right_on=['region' ,'antimicrobial_class']
    ,how='left'
)

# -----------------------------------------------------------------------------
# Calculate regional resistance for each pathogen over all classes
# -----------------------------------------------------------------------------
# For each class*pathogen, calculate resistance x proportion of use
# Based on Laxminarayan paper (BMJ Open 2011;1:e000135. doi: 10.1136/bmjopen-2011-000135)
amr_full_p1_classprpn['resistancerate_x_classprpn'] = amr_full_p1_classprpn['resistance_rate'] * amr_full_p1_classprpn['region_prpn_amu']

amr_full_p2 = amr_full_p1_classprpn.pivot_table(
    index=['region' ,'pathogen' ,'reporting_year']
    ,values=['nisolates_sum' ,'nisolates_resistant_sum' ,'resistancerate_x_classprpn']
    ,aggfunc='sum'
)
amr_full_p2 = amr_full_p2.add_suffix('_sum')
amr_full_p2 = amr_full_p2.reset_index()
amr_full_p2['resistance_rate_wtavg'] = amr_full_p2['nisolates_resistant_sum_sum'] / amr_full_p2['nisolates_sum_sum']

# -----------------------------------------------------------------------------
# Merge with AMU and calculate drug resistance index
# -----------------------------------------------------------------------------
# Using E.coli as indicator, same as EFSA paper (https://www.efsa.europa.eu/en/efsajournal/pub/5017)
amr_full_p2_tomerge = amr_full_p2.query("pathogen == 'E. coli'").copy()

# Keep a single year for each region
# Select the last year with good representation, preferring consistency across regions
# Check record count by country and year
check_amr_years = amr_full_withrgn_working[['woah_region' ,'reporting_year' ,'pathogen']].value_counts().reset_index()
keep_years_byregion = {
    "AFRICA":2015
    ,"AMERICAS":2018
    ,"ASIA, FAR EAST AND OCEANIA":2018
    ,"EUROPE":2018
    ,"MIDDLE EAST":2015
    }
amr_full_p2_tomerge['keep_year'] = \
    amr_full_p2_tomerge['region'].str.upper().apply(lookup_from_dictionary ,DICT=keep_years_byregion)
amr_full_p2_tomerge = amr_full_p2_tomerge.query("reporting_year == keep_year")

rename_cols = {
    'resistancerate_x_classprpn_sum':'drug_resistance_index'
}
amr_full_p2_tomerge = amr_full_p2_tomerge.rename(columns=rename_cols)

amu_combined_regional = pd.merge(
    left=amu_combined_regional
    ,right=amr_full_p2_tomerge[['region' ,'resistance_rate_wtavg' ,'drug_resistance_index']]
    ,on='region'
    ,how='left'
)
datainfo(amu_combined_regional)

# -----------------------------------------------------------------------------
# Calculate drug resistance index
# First try - before calculating with proportion of antimicrobial classes
# -----------------------------------------------------------------------------
# # Simple index from Agunos paper (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6509235/#B18)
# # Resistance x biomass
# amu_combined_regional['amr_index_agunos'] = \
#     amu_combined_regional['amr_prevalence'] * amu_combined_regional['biomass_total_kg_region'] \
#         / 1e9   # Adjust downward

# # Multiplying by usage
# amu_combined_regional['amr_index_agunos_usage'] = \
#     amu_combined_regional['amr_index_agunos'] * amu_combined_regional['total_antimicrobials_tonnes_region']

# # Approximating index from Laxminarayan paper
# # Find proportion of total AMU for each region represented by antimicrobial classes in AMR data
# # Using same subset as for merging: E.coli for a specific year
# amr_classes = amr_full_withrgn[['woah_region' ,'reporting_year' ,'pathogen' ,'antibiotic_class']].drop_duplicates()
# amr_classes_included = pd.merge(
#     left=amr_full_p2_tomerge
#     ,right=amr_classes
#     ,left_on=['region' ,'reporting_year' ,'pathogen']
#     ,right_on=['woah_region' ,'reporting_year' ,'pathogen']
#     ,how='left'
# )

# =============================================================================
#### Export
# =============================================================================
datainfo(amu_combined_regional)

amu_combined_regional.to_csv(os.path.join(PRODATA_FOLDER ,'amu_combined_regional.csv') ,index=False)
amu_combined_regional.to_csv(os.path.join(DASH_DATA_FOLDER ,'amu_combined_regional.csv') ,index=False)

#%% Prep Resistance data for plotting at the country-level
'''
This will be used to allow users to explore the AMR data in detail, so retains the full
granularity: country, year, antimicrobial class, and pathogen.
'''

amr_withrgn_working = amr_withrgn.copy()

# Add prevalence weighted by isolates
amr_withrgn_working['overall_prev_x_isolates'] = amr_withrgn_working['overall_prev'] * amr_withrgn_working['sum_isolates']

# =============================================================================
#### Add summary rows for plotting
# =============================================================================
# Antimicrobial = ALL for a given country, year, and pathogen
# Reporting the average prevalence across all antimicrobials, weighted by sum_isolates.
amr_pivot_bypathogen = amr_withrgn_working.pivot_table(
    index=['location_name' ,'map_id' ,'reporting_year' ,'woah_region' ,'pathogen']
    ,aggfunc={
        'overall_prev_x_isolates':['sum' ,'count']
        ,'sum_isolates':'sum'
    }
)
amr_pivot_bypathogen = colnames_from_index(amr_pivot_bypathogen) 	# If multiple aggregate functions specified, will create multi-indexed columns. Flatten.
amr_pivot_bypathogen = amr_pivot_bypathogen.reset_index()         # Pivoting will change columns to indexes. Change them back.

amr_pivot_bypathogen['antimicrobial_class'] = 'All'
amr_pivot_bypathogen['overall_prev'] = amr_pivot_bypathogen['overall_prev_x_isolates_sum'] / amr_pivot_bypathogen['sum_isolates_sum']
amr_pivot_bypathogen = amr_pivot_bypathogen.rename(columns={'sum_isolates_sum':'sum_isolates'})     # Rename to keep after concatenating

# Pathogen = ALL for a given country, year, and antimicrobial
# Reporting the average prevalence across all pathogens, weighted by sum_isolates.
amr_pivot_byantimicrobial = amr_withrgn_working.pivot_table(
    index=['location_name' ,'map_id' ,'reporting_year' ,'woah_region' ,'antimicrobial_class']
    ,aggfunc={
        'overall_prev_x_isolates':['sum' ,'count']
        ,'sum_isolates':'sum'
    }
)
amr_pivot_byantimicrobial = colnames_from_index(amr_pivot_byantimicrobial) 	# If multiple aggregate functions specified, will create multi-indexed columns. Flatten.
amr_pivot_byantimicrobial = amr_pivot_byantimicrobial.reset_index()         # Pivoting will change columns to indexes. Change them back.

amr_pivot_byantimicrobial['pathogen'] = 'All'
amr_pivot_byantimicrobial['overall_prev'] = amr_pivot_byantimicrobial['overall_prev_x_isolates_sum'] / amr_pivot_byantimicrobial['sum_isolates_sum']
amr_pivot_byantimicrobial = amr_pivot_byantimicrobial.rename(columns={'sum_isolates_sum':'sum_isolates'})     # Rename to keep after concatenating

# Concatenate with original data
amr_withsmry = pd.concat(
    [amr_withrgn ,amr_pivot_bypathogen ,amr_pivot_byantimicrobial]
    ,axis=0
    ,join='inner'   # Keep only common columns
    ,ignore_index=True
)

# =============================================================================
#### Cleanup and Export
# =============================================================================
# We do not intend to show yearly data in the dashboard
# Filter to the year with most representation for each region
amr_withsmry['keep_year'] = \
    amr_withsmry['woah_region'].str.upper().apply(lookup_from_dictionary ,DICT=keep_years_byregion)
amr_withsmry = amr_withsmry.query("reporting_year == keep_year")

datainfo(amr_withsmry)
amr_withsmry.to_csv(os.path.join(PRODATA_FOLDER ,'amr_withsmry.csv') ,index=False)
amr_withsmry.to_csv(os.path.join(DASH_DATA_FOLDER ,'amr_withsmry.csv') ,index=False)

#%% Illustrate AM Usage and Price with uncertainty

# =============================================================================
#### Create data based on spreadsheet from Sara
# =============================================================================
amu_uncertainty_data = pd.DataFrame(
    {"region":['Africa' ,'Americas' ,'Asia, Far East and Oceania' ,'Europe' ,'Middle East']
     ,"n_countries":[24 ,19 ,22 ,41 ,3]

     ,"amu_terrestrial_tonnes_min":[1403 ,18753 ,33387 ,7314 ,34]
     ,"amu_terrestrial_tonnes_mostlikely":[2806 ,29000 ,50080 ,7679.5 ,198]
     ,"amu_terrestrial_tonnes_max":[3086 ,31900 ,55088 ,8045 ,218]
     ,"amu_terrestrial_tonnes_distr":['Pert' ,'Pert' ,'Pert' ,'Uniform' ,'Pert']
     ,"amu_terrestrial_tonnes_distr_lambda":[np.nan ,np.nan ,np.nan ,np.nan ,np.nan]

     ,"amu_eurospertonne_min":[20476 ,20476 ,20476 ,np.nan ,20476]
     ,"amu_eurospertonne_mostlikely":[176992 ,82775.5 ,108806 ,145075 ,108806]
     ,"amu_eurospertonne_max":[206007 ,145075 ,123314 ,np.nan ,123314]
     ,"amu_eurospertonne_distr":['Modified pert; Ƴ=2.5' ,'Uniform' ,'Modified pert; Ƴ=2.5' ,'' ,'Modified pert; Ƴ=2.5']
     ,"amu_eurospertonne_distr_lambda":[2.5 ,np.nan ,2.5 ,np.nan ,2.5]
     }
)

# Merge in biomass data
amu_uncertainty_data = pd.merge(
    left=amu_uncertainty_data
    ,right=amu2018_biomass.query("segment == 'Countries reporting AMU data'")[['region' ,'biomass_total_kg' ,'biomass_total_terr_kg']]
    ,on='region'
    ,how='left'
)

datainfo(amu_uncertainty_data)

usage_cols = ['amu_terrestrial_tonnes_min' ,'amu_terrestrial_tonnes_mostlikely' ,'amu_terrestrial_tonnes_max']
price_cols = ['amu_eurospertonne_min' ,'amu_eurospertonne_mostlikely' ,'amu_eurospertonne_max']

amu_uncertainty_data_toplot_usage = amu_uncertainty_data.copy()
amu_uncertainty_data_toplot_usage[price_cols] = np.nan

amu_uncertainty_data_toplot_price = amu_uncertainty_data.copy()
amu_uncertainty_data_toplot_price[usage_cols] = np.nan
amu_uncertainty_data_toplot_price['region'] = amu_uncertainty_data_toplot_price['region'] + '_price'

amu_uncertainty_data_toplot = pd.concat([amu_uncertainty_data_toplot_usage ,amu_uncertainty_data_toplot_price] ,axis=0 ,ignore_index=True)
amu_uncertainty_data_toplot = amu_uncertainty_data_toplot.sort_values(by='region')

# =============================================================================
#### Add confidence intervals for usage
# =============================================================================
def add_ci(INPUT_ROW):
    # Usage
    if 'PERT' in INPUT_ROW['amu_terrestrial_tonnes_distr'].upper():
        # Get Beta distribution and calculate CI
        if pd.notnull(INPUT_ROW['amu_terrestrial_tonnes_distr_lambda']):
            beta_distr_tonnes = pert_to_beta(
                INPUT_ROW['amu_terrestrial_tonnes_min']
                ,INPUT_ROW['amu_terrestrial_tonnes_mostlikely']
                ,INPUT_ROW['amu_terrestrial_tonnes_max']
                ,INPUT_ROW['amu_terrestrial_tonnes_distr_lambda']
            )
        else:
            beta_distr_tonnes = pert_to_beta(
                INPUT_ROW['amu_terrestrial_tonnes_min']
                ,INPUT_ROW['amu_terrestrial_tonnes_mostlikely']
                ,INPUT_ROW['amu_terrestrial_tonnes_max']
            )

        beta_distr_tonnes_ci95 = beta_distr_tonnes.interval(0.95)

        # Rescale CI to match original Pert
        tonnes_ci95_low = (beta_distr_tonnes_ci95[0] * (INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min'])) + INPUT_ROW['amu_terrestrial_tonnes_min']   # Translate from (0,1) to scale of PERT
        tonnes_ci95_high = (beta_distr_tonnes_ci95[1] * (INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min'])) + INPUT_ROW['amu_terrestrial_tonnes_min']   # Translate from (0,1) to scale of PERT
    elif INPUT_ROW['amu_terrestrial_tonnes_distr'].upper() == 'UNIFORM':
        tonnes_ci95_low = 0.025*(INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min']) + INPUT_ROW['amu_terrestrial_tonnes_min']
        tonnes_ci95_high = 0.975*(INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min']) + INPUT_ROW['amu_terrestrial_tonnes_min']
    else:
        tonnes_ci95_low = None
        tonnes_ci95_high = None

    # Price
    if 'PERT' in INPUT_ROW['amu_eurospertonne_distr'].upper():
        # Get Beta distribution and calculate CI
        if pd.notnull(INPUT_ROW['amu_eurospertonne_distr_lambda']):
            beta_distr_price = pert_to_beta(
                INPUT_ROW['amu_eurospertonne_min']
                ,INPUT_ROW['amu_eurospertonne_mostlikely']
                ,INPUT_ROW['amu_eurospertonne_max']
                ,INPUT_ROW['amu_eurospertonne_distr_lambda']
            )
        else:
            beta_distr_price = pert_to_beta(
                INPUT_ROW['amu_eurospertonne_min']
                ,INPUT_ROW['amu_eurospertonne_mostlikely']
                ,INPUT_ROW['amu_eurospertonne_max']
            )

        beta_distr_price_ci95 = beta_distr_price.interval(0.95)

        # Rescale CI to match original Pert
        price_ci95_low = (beta_distr_price_ci95[0] * (INPUT_ROW['amu_eurospertonne_max'] - INPUT_ROW['amu_eurospertonne_min'])) + INPUT_ROW['amu_eurospertonne_min']   # Translate from (0,1) to scale of PERT
        price_ci95_high = (beta_distr_price_ci95[1] * (INPUT_ROW['amu_eurospertonne_max'] - INPUT_ROW['amu_eurospertonne_min'])) + INPUT_ROW['amu_eurospertonne_min']   # Translate from (0,1) to scale of PERT
    elif INPUT_ROW['amu_eurospertonne_distr'].upper() == 'UNIFORM':
        price_ci95_low = 0.025*(INPUT_ROW['amu_eurospertonne_max'] - INPUT_ROW['amu_eurospertonne_min']) + INPUT_ROW['amu_eurospertonne_min']
        price_ci95_high = 0.975*(INPUT_ROW['amu_eurospertonne_max'] - INPUT_ROW['amu_eurospertonne_min']) + INPUT_ROW['amu_eurospertonne_min']
    else:
        price_ci95_low = None
        price_ci95_high = None

    return pd.Series([tonnes_ci95_low ,tonnes_ci95_high ,price_ci95_low ,price_ci95_high])

amu_uncertainty_data[['tonnes_ci95_low' ,'tonnes_ci95_high' ,'price_ci95_low' ,'price_ci95_high']] = amu_uncertainty_data.apply(add_ci ,axis=1)

#??? Should intervals be centered on the MOST LIKELY value or the MEAN?
amu_uncertainty_data = amu_uncertainty_data.eval(
    '''
    amu_terrestrial_tonnes_errorlow = amu_terrestrial_tonnes_mostlikely - tonnes_ci95_low
    amu_terrestrial_tonnes_errorhigh = tonnes_ci95_high - amu_terrestrial_tonnes_mostlikely

    amu_eurospertonne_errorlow = amu_eurospertonne_mostlikely - price_ci95_low
    amu_eurospertonne_errorhigh = price_ci95_high - amu_eurospertonne_mostlikely
    '''
)

# =============================================================================
#### Generate distribution of total expenditure
# =============================================================================
# For each region, resample from Usage and Price distributions and multiply to get expenditure
resample_n = 10000

expenditure_africa = pd.DataFrame(index=range(resample_n))
expenditure_africa['resampled_usage'] = generate_pert(resample_n, 1403, 2806, 3086)['rand_pert']
expenditure_africa['resampled_price'] = generate_pert(resample_n, 20476, 176992, 206007 ,2.5)['rand_pert']
expenditure_africa['resampled_expenditure'] = expenditure_africa['resampled_usage'] * expenditure_africa['resampled_price']
expenditure_africa['expenditure_pctile'] = expenditure_africa['resampled_expenditure'].rank(pct=True)

expenditure_americas = pd.DataFrame(index=range(resample_n))
expenditure_americas['resampled_usage'] = generate_pert(resample_n, 18753, 29000, 31900)['rand_pert']
expenditure_americas['resampled_price'] = sps.uniform.rvs(loc=20476 ,scale=145075 ,size=resample_n)
expenditure_americas['resampled_expenditure'] = expenditure_americas['resampled_usage'] * expenditure_americas['resampled_price']
expenditure_americas['expenditure_pctile'] = expenditure_americas['resampled_expenditure'].rank(pct=True)

expenditure_asia = pd.DataFrame(index=range(resample_n))
expenditure_asia['resampled_usage'] = generate_pert(resample_n, 33387, 50080, 55088)['rand_pert']
expenditure_asia['resampled_price'] = generate_pert(resample_n, 20476, 108806, 123314 ,2.5)['rand_pert']
expenditure_asia['resampled_expenditure'] = expenditure_asia['resampled_usage'] * expenditure_asia['resampled_price']
expenditure_asia['expenditure_pctile'] = expenditure_asia['resampled_expenditure'].rank(pct=True)

expenditure_europe = pd.DataFrame(index=range(resample_n))
expenditure_europe['resampled_usage'] = sps.uniform.rvs(loc=7314 ,scale=8045 ,size=resample_n)
expenditure_europe['resampled_price'] = 145075
expenditure_europe['resampled_expenditure'] = expenditure_europe['resampled_usage'] * expenditure_europe['resampled_price']
expenditure_europe['expenditure_pctile'] = expenditure_europe['resampled_expenditure'].rank(pct=True)

expenditure_mideast = pd.DataFrame(index=range(resample_n))
expenditure_mideast['resampled_usage'] = generate_pert(resample_n, 34, 198, 218)['rand_pert']
expenditure_mideast['resampled_price'] = generate_pert(resample_n, 20476, 108806, 123314 ,2.5)['rand_pert']
expenditure_mideast['resampled_expenditure'] = expenditure_mideast['resampled_usage'] * expenditure_mideast['resampled_price']
expenditure_mideast['expenditure_pctile'] = expenditure_mideast['resampled_expenditure'].rank(pct=True)

# Plot
snplt = sns.displot(
	data=expenditure_mideast
	,x='resampled_expenditure'
	,kind='hist'
    ,stat='probability'
    ,bins=20
)

# Get CI for expenditure from percentiles of the resampled distribution
def add_expenditure_ci(REGION):
    if REGION.upper() == 'AFRICA':
        ci_low = expenditure_africa.query("expenditure_pctile == 0.025")['resampled_expenditure'].values[0]
        ci_mid = expenditure_africa.query("expenditure_pctile == 0.5")['resampled_expenditure'].values[0]
        ci_high = expenditure_africa.query("expenditure_pctile == 0.975")['resampled_expenditure'].values[0]
    elif REGION.upper() == 'AMERICAS':
        ci_low = expenditure_americas.query("expenditure_pctile == 0.025")['resampled_expenditure'].values[0]
        ci_mid = expenditure_americas.query("expenditure_pctile == 0.5")['resampled_expenditure'].values[0]
        ci_high = expenditure_americas.query("expenditure_pctile == 0.975")['resampled_expenditure'].values[0]
    elif 'ASIA' in REGION.upper():
        ci_low = expenditure_asia.query("expenditure_pctile == 0.025")['resampled_expenditure'].values[0]
        ci_mid = expenditure_asia.query("expenditure_pctile == 0.5")['resampled_expenditure'].values[0]
        ci_high = expenditure_asia.query("expenditure_pctile == 0.975")['resampled_expenditure'].values[0]
    elif REGION.upper() == 'EUROPE':
        ci_low = expenditure_europe.query("expenditure_pctile == 0.025")['resampled_expenditure'].values[0]
        ci_mid = expenditure_europe.query("expenditure_pctile == 0.5")['resampled_expenditure'].values[0]
        ci_high = expenditure_europe.query("expenditure_pctile == 0.975")['resampled_expenditure'].values[0]
    elif REGION.upper() == 'MIDDLE EAST':
        ci_low = expenditure_mideast.query("expenditure_pctile == 0.025")['resampled_expenditure'].values[0]
        ci_mid = expenditure_mideast.query("expenditure_pctile == 0.5")['resampled_expenditure'].values[0]
        ci_high = expenditure_mideast.query("expenditure_pctile == 0.975")['resampled_expenditure'].values[0]
    else:
        ci_low = np.nan
        ci_mid = np.nan
        ci_high = np.nan
    return pd.Series([ci_low ,ci_mid ,ci_high])
amu_uncertainty_data[['expenditure_ci95_low' ,'expenditure_ci95_mid' ,'expenditure_ci95_high']] = amu_uncertainty_data['region'].apply(add_expenditure_ci)

amu_uncertainty_data = amu_uncertainty_data.eval(
    '''
    amu_terrestrial_expenditure_midpoint = expenditure_ci95_mid
    amu_terrestrial_expenditure_errorlow = amu_terrestrial_expenditure_midpoint - expenditure_ci95_low
    amu_terrestrial_expenditure_errorhigh = expenditure_ci95_high - amu_terrestrial_expenditure_midpoint
    '''
)

# =============================================================================
#### Export
# =============================================================================
datainfo(amu_uncertainty_data)

amu_uncertainty_data.to_csv(os.path.join(DASH_DATA_FOLDER, "amu_uncertainty_data.csv"))
