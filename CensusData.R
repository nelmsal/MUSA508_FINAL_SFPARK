library(tidyverse)
library(tidycensus)
library(sf)
library(kableExtra)
library(tmap)
library(tmaptools)




census_api_key("a681da13d473295bc7084fc43072d06e091d9dda", install = TRUE) 


#B08007_001E -> workforce 16+
#B08301_003E->drove to work
#B08301_010E-> public transport to work
#B08301_016E-> taxi to work
#B08301_018E -> biked to work
#B08301_021E -> worked from home
#B11016_001E-> total households
#aggregate number of vehicles available -> B25046_001E
#households with no vehicles -> B25044_003E
#B01003_001E -> total population 5+
#population with bachelor's degree -> B15003_022E
#walked to work -> B08301_019E
#motorcycle to work -> B08301_017E
#other transport ways to work -> B08301_020E
#carpooled to work --> B08301_004E
#aggregate commute to work in minutes -> B08135_001E

#workers commute to work total -> B08303_001E
#workers commute time <5 min -> B08303_002E
#workers commute time 5-9 min ->B08303_003E
#workers commute time 10-14 min ->B08303_004E
#workers commute time 15-19 min ->B08303_005E
#workers commute time 20-24 min ->B08303_006E
#workers commute time 25-29 min ->B08303_007E
#workers commute time 30-34 min ->B08303_008E
#workers commute time 35-39 min ->B08303_009E
#workers commute time 40-44 min ->B08303_010E
#workers commute time 45-59 min ->B08303_011E
#workers commute time 60-89 min ->B08303_012E
#workers commute time 90+ min ->B08303_013E




SFtracts19 <- 
  get_acs(geography = "tract", variables = c("B25026_001E","B02001_002E","B15001_050E",
                                             "B15001_009E","B19013_001E","B25058_001E",
                                             "B06012_002E", "B08301_003E", "B08301_010E", "B08301_016E", "B08301_018E", "B08301_021E
", "B08007_001E", "B11016_001E", "B25044_003E", "B15003_022E", "B01003_001E", "B08301_019E", "B08301_017E", "B08301_020E", "B08301_004E", "B08135_001E", "B08303_001E", "B08303_002E", "B08303_003E", "B08303_004E", "B08303_005E", "B08303_006E", "B08303_007E", "B08303_008E", "B08303_009E", "B08303_010E", "B08303_011E", "B08303_012E", "B08303_013E"      ), 
          year=2019, state=06, county=075, geometry=T, output="wide") %>%
  st_transform('ESRI:102685') %>%
  rename(TotalPop = B25026_001E, 
         Whites = B02001_002E,
         FemaleBachelors = B15001_050E, 
         MaleBachelors = B15001_009E,
         MedHHInc = B19013_001E, 
         MedRent = B25058_001E,
         TotalPoverty = B06012_002E) %>%
  dplyr::select(-NAME, -starts_with("B")) %>%
  mutate(pctWhite = ifelse(TotalPop > 0, Whites / TotalPop,0),
         pctBachelors = ifelse(TotalPop > 0, ((FemaleBachelors + MaleBachelors) / TotalPop),0),
         pctPoverty = ifelse(TotalPop > 0, TotalPoverty / TotalPop, 0),
         year = "2019") %>%
  dplyr::select(-Whites, -FemaleBachelors, -MaleBachelors, -TotalPoverty)
