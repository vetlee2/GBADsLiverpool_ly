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

# Load pkgs
pA <- c("tidyverse", "readxl", "mc2d", "reshape2")
lapply(pA, require, character.only = T)
#> Set random seed
set.seed(123)

#> Read AHLE and Attribution sheets
AHLE <- read_xlsx("AHLE.xlsx", sheet = 2)
Att <- read_xlsx("data.xlsx", sheet = 5)
#> Set number of samples to take from distribution
n = 1000
#> Run function
Ethiopia <- attribute(AHLE, Att, n)
Ethiopia[[1]] #> is summary of n
Ethiopia[[2]] #> is a long data frame of n samples

#> Treemap example
tm <- treemap(Ethiopia[[1]], index = c("Age class", "Cause"), vSize = "mean", type="index",
               title="Attribution of small ruminant health loss in Ethiopia",
               fontsize.labels=c(18,12), align.labels = list(c("centre", "top"),c("centre","centre")),
               fontcolor.labels="black", palette = "Set3")