# =================================================================
# Top-level program parameters
# =================================================================
cmd_n_samples <- 1000 				# Number of samples to take from distribution

# -----------------------------------------------------------------
# Set manually
# -----------------------------------------------------------------
cmd_input_ahle <- 'Attribution function input - example AHLE.csv'					# First argument: full path to AHLE estimates file (csv)
cmd_input_expert <- 'Attribution function input - expert opinions.csv' 				# Second argument: full path to expert opinion attribution file (csv)
cmd_output_file <- 'attribution_summary.csv' 		# Third argument: output file for saving results

# -----------------------------------------------------------------
# Get from command line arguments
# -----------------------------------------------------------------
# Only look for command arguments if this was invoked from the command line
if (grepl('Rterm.exe', paste(commandArgs(), collapse=" "), ignore.case = TRUE, fixed = TRUE))
{
	cmd_args <- commandArgs(trailingOnly=TRUE)	# Fetch command line arguments
	cmd_input_ahle <- cmd_args[1] 					# First argument: full path to AHLE estimates file (csv)
	cmd_input_expert <- cmd_args[2] 					# Second argument: full path to expert opinion attribution file (csv)
	cmd_output_file <- cmd_args[3] 					# Third argument: full path to output file (csv)
}

# -----------------------------------------------------------------
# Show in console
# -----------------------------------------------------------------
print('Using the following program parameters:')
print('   Input files')
print(cmd_input_ahle)
print(cmd_input_expert)
print('   Output file')
print(cmd_output_file)

# =================================================================
# Define functions
# =================================================================
#> Attribution function
attribute <- function(ahle_estimates, expert_attribution, num_sample){
  n = num_sample
  #> Split AHLE data and take samples from each AHLE, system, age group
  LA <- split(ahle_estimates, seq(nrow(ahle_estimates)))
  
  RA <- lapply(LA, function(x) rnorm(n, mean=x[[5]], sd=x[[6]])) %>%
    do.call(rbind,.) %>%
    cbind(select(ahle_estimates,!5:6),.)
  
  #> Average expert min, avg, and max values. Take samples from this distribution
  a <- select(expert_attribution,!Expert) %>%
    mutate(min = min/100,
           avg = avg/100,
           max = max/100) %>%
    group_by(.[1:4]) %>% 
    summarise(., across(.cols=min:max, .fns = mean), .groups="keep") %>%
    ungroup()
  
  La <- split(a, seq(nrow(a)))
  
  Ra <- lapply(La, function(x) rpert(n, x[[5]], x[[6]], x[[7]])) %>% 
    do.call(rbind,.) %>% 
    cbind(select(a,!5:7),.)
  
  #> Scale samples of attributable fractions so each set sum to one.
  Ras <- Ra %>% 
    group_by(.[1:3]) %>%
    mutate(across(.cols='1':'1000', ~ .x/sum(.x))) %>%
    ungroup()
  
  #> Sum sheep and goat samples, multiply by scaled attributable fraction samples
  tmp1 <- RA %>%
    group_by(.[2:4]) %>%
    summarise(., across(.cols='1':'1000', .fns = sum), .groups="keep") %>%
    melt(id.vars = c("AHLE", "Production system", "Age class"), variable.name = "Sample", value.name = "Group_value")
  
  tmp2 <- Ras %>% melt(id.vars = c("AHLE", "Production system", "Age class", "Cause"), variable.name = "Sample", value.name="AFp") 
  
  j <- left_join(tmp2, tmp1, by=c("AHLE", "Production system", "Age class", "Sample")) %>%
    mutate(value = Group_value * AFp, .keep="unused")
  
  #> Summarise
  s <- j %>%
    group_by(.[1:4]) %>% 
    summarise(., .groups = "keep", 
              median=median(value),
              mean=mean(value), 
              sd=sd(value)) %>%
    mutate(lower95 = mean - (qnorm(0.975)*sd/sqrt(n)),
           upper95 = mean + (qnorm(0.975)*sd/sqrt(n)))
  
  return(list(s, j))
}

# =================================================================
# Preliminaries
# =================================================================
# Load pkgs
pA <- c("tidyverse", "readxl", "mc2d", "reshape2")
lapply(pA, require, character.only = T)

#> Set random seed
set.seed(123)

#> Read AHLE and Attribution sheets
AHLE <- read_csv(cmd_input_ahle)
Att <- read_csv(cmd_input_expert)

# =================================================================
# Run attribution
# =================================================================
#> Run function
Ethiopia <- attribute(AHLE, Att, cmd_n_samples)

print('First object returned:')
Ethiopia[[1]] #> is summary of n
print('Second object returned:')
Ethiopia[[2]] #> is a long data frame of n samples

attribution_summary <- Ethiopia[[1]]

# =================================================================
# Process results
# =================================================================
#> Treemap example
#tm <- treemap(Ethiopia[[1]], index = c("Age class", "Cause"), vSize = "mean", type="index",
#               title="Attribution of small ruminant health loss in Ethiopia",
#               fontsize.labels=c(18,12), align.labels = list(c("centre", "top"),c("centre","centre")),
#               fontcolor.labels="black", palette = "Set3")

# Write to file
write.csv(attribution_summary, cmd_output_file, row.names=FALSE)
