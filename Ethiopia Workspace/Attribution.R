# =================================================================
# Top-level program parameters
# =================================================================
# -----------------------------------------------------------------
# Set manually
# -----------------------------------------------------------------
# Folder location of input files (AHLE.xlsx and data.xlsx)
cmd_input_directory <- '.'

# Folder location for saving output files
cmd_output_directory <- '.'

#> Set number of samples to take from distribution
cmd_n_samples = 1000

# -----------------------------------------------------------------
# Get from command line arguments
# -----------------------------------------------------------------
# Only look for command arguments if this was invoked from the command line
if (grepl('Rterm.exe', paste(commandArgs(), collapse=" "), ignore.case = TRUE, fixed = TRUE))
{
	cmd_args <- commandArgs(trailingOnly=TRUE)	# Fetch command line arguments
	cmd_input_directory <- cmd_args[1] 				# First argument: folder location of input files (AHLE.xlsx and data.xlsx)
	cmd_output_directory <- cmd_args[2] 			# Second argument: folder location for saving output files
	cmd_n_samples <- as.numeric(cmd_args[3]) 		# Third argument: number of samples to take from distribution
}

# -----------------------------------------------------------------
# Show in console
# -----------------------------------------------------------------
print('Using the following program parameters:')
print('   Input directory')
print(cmd_input_directory)
print('   Output directory')
print(cmd_output_directory)

# =================================================================
# Define functions
# =================================================================
#> Attribution function
attribute <- function(AHLE, Att, num_sample){
  n = num_sample
  #> Split AHLE data and take samples from each AHLE, system, age group
  LA <- split(AHLE, seq(nrow(AHLE)))
  
  RA <- lapply(LA, function(x) rnorm(n, mean=x[[5]], sd=x[[6]])) %>%
    do.call(rbind,.) %>%
    cbind(select(AHLE,!5:6),.)
  
  #> Average expert min, avg, and max values. Take samples from this distribution
  a <- select(Att,!Expert) %>%
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
# Prep
# =================================================================
# Load pkgs
pA <- c("tidyverse", "readxl", "mc2d", "reshape2")
lapply(pA, require, character.only = T)

#> Set random seed
set.seed(123)

#> Read AHLE and Attribution sheets
AHLE <- read_xlsx(file.path(cmd_input_directory, "AHLE.xlsx"), sheet = 2)
Att <- read_xlsx(file.path(cmd_input_directory, "data.xlsx"), sheet = 5)

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
write.csv(attribution_summary, file.path(cmd_output_directory, 'attribution_summary.csv'), row.names=FALSE)
