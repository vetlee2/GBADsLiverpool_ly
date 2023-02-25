#%% About
'''
Experimenting with uncertainty around AM Usage and price
'''
#%% Functions

# Translate a PERT distribution to the equivalent Beta
# Output a dataframe with samples generated from the distribution and a histogram
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

#%% Do it

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

     ,"amu_eurospertonne_min":[20476 ,20476 ,20476 ,np.nan ,20476]
     ,"amu_eurospertonne_mostlikely":[176992 ,82775.5 ,108806 ,145075 ,108806]
     ,"amu_eurospertonne_max":[206007 ,145075 ,123314 ,np.nan ,123314]
     ,"amu_eurospertonne_distr":['Modified pert; Ƴ=2.5' ,'Uniform' ,'Modified pert; Ƴ=2.5' ,'' ,'Modified pert; Ƴ=2.5']
     }
)

# Merge in biomass data
amu_uncertainty_data = pd.merge(
    left=amu_uncertainty_data
    ,right=amu2018_biomass.query("segment == 'Total Region'")[['region' ,'biomass_total_terr_kg']]
    ,on='region'
    ,how='left'
)

# =============================================================================
#### Add confidence intervals for usage
# =============================================================================
def add_ci_tonnes(INPUT_ROW):
    if INPUT_ROW['amu_terrestrial_tonnes_distr'].upper() == 'PERT':
        # Get Beta distribution and calculate CI
        beta_distr = pert_to_beta(
            INPUT_ROW['amu_terrestrial_tonnes_min']
            ,INPUT_ROW['amu_terrestrial_tonnes_mostlikely']
            ,INPUT_ROW['amu_terrestrial_tonnes_max']
        )
        beta_distr_ci95 = beta_distr.interval(0.95)

        # Rescale CI to match original Pert
        ci95_low = (beta_distr_ci95[0] * (INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min'])) + INPUT_ROW['amu_terrestrial_tonnes_min']   # Translate from (0,1) to scale of PERT
        ci95_high = (beta_distr_ci95[1] * (INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min'])) + INPUT_ROW['amu_terrestrial_tonnes_min']   # Translate from (0,1) to scale of PERT
    elif INPUT_ROW['amu_terrestrial_tonnes_distr'].upper() == 'UNIFORM':
        ci95_low = 0.025*(INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min']) + INPUT_ROW['amu_terrestrial_tonnes_min']
        ci95_high = 0.975*(INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min']) + INPUT_ROW['amu_terrestrial_tonnes_min']
    else:
        ci95_low = None
        ci95_high = None
    return pd.Series([ci95_low ,ci95_high])

amu_uncertainty_data[['tonnes_ci95_low' ,'tonnes_ci95_high']] = amu_uncertainty_data.apply(add_ci_tonnes ,axis=1)

#??? Should intervals be centered on the MOST LIKELY value or the MEAN?
amu_uncertainty_data = amu_uncertainty_data.eval(
    '''
    amu_terrestrial_tonnes_errorlow = amu_terrestrial_tonnes_mostlikely - tonnes_ci95_low
    amu_terrestrial_tonnes_errorhigh = tonnes_ci95_high - amu_terrestrial_tonnes_mostlikely
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
amu_uncertainty_data.to_csv(os.path.join(DASH_DATA_FOLDER, "amu_uncertainty_data.csv"))
