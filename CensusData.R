library(tidyverse)
library(tidycensus)
library(sf)
library(kableExtra)
library(tmap)
library(tmaptools)




census_api_key("a681da13d473295bc7084fc43072d06e091d9dda", overwrite = TRUE) 


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
workers_commute_25min29min = B08303_007E
workers_commute_30_34min = B08303_008E
workers_commute_35_39min = B08303_009E
workers_commute_40_44min = B08303_010E
workers_commute_45_59min = B08303_011E
workers_commute_60_89min = B08303_012E
workers_commute_90min = B08303_013E




SFtracts19 <- 
  get_acs(geography = "tract", variables = c("B25026_001E","B02001_002E","B15001_050E",
                                             "B15001_009E","B19013_001E","B25058_001E",
                                             "B06012_002E", "B08301_003E", "B08301_010E", "B08301_016E", "B08301_018E", "B08301_021E", "B08007_001E", "B11016_001E", "B25044_003E", "B15003_022E", "B01003_001E", "B08301_019E", "B08301_017E", "B08301_020E", "B08301_004E", "B08135_001E", "B08303_001E", "B08303_002E", "B08303_003E", "B08303_004E", "B08303_005E", "B08303_006E", "B08303_007E", "B08303_008E", "B08303_009E", "B08303_010E", "B08303_011E", "B08303_012E", "B08303_013E", "B08301_018E", "B15003_022E"), 
          year=2019, state=06, county=075, geometry=T, output="wide") %>%
  st_transform('ESRI:102241') %>%
  rename(total_households = B11016_001E,
         workforce_16 = B08007_001E, 
         drove_to_work = B08301_003E,
         public_transport_to_work = B08301_010E, 
         taxi_to_work = B08301_016E,
         worked_from_home = B08301_021E,
         Num_Vehicles = B06012_002E,
         House_holds_no_vehicles = B25044_003E,
         total_population = B01003_001E,
         walked_to_work = B08301_019E,
         motorcycle_to_work = B08301_017E,
         other_commute_to_work = B08301_020E,
         carpooled_to_work = B08301_004E,
         work_commute_minutes = B08135_001E,
         workers_commute_time_total = B08303_001E,
         workers_commute_less5min = B08303_002E,
         workers_commute_5min9min = B08303_003E,
         workers_commute_10min14min = B08303_004E,
         workers_commute_15min19min = B08303_005E,
         workers_commute_20min24min = B08303_006E,
         workers_commute_25min29min = B08303_007E,
         workers_commute_30_34min = B08303_008E,
         workers_commute_35_39min = B08303_009E,
         workers_commute_40_44min = B08303_010E,
         workers_commute_45_59min = B08303_011E,
         workers_commute_60_89min = B08303_012E,
         workers_commute_90min = B08303_013E,
         ) %>%
  dplyr::select(-NAME, -starts_with("B")) %>%
  mutate(Percent_Drive_Work = (drove_to_work/workforce_16)*100)%>%
  mutate(Percent_PublicTransport_work = (public_transport_to_work/workforce_16)*100)%>%
  mutate(Percent_taxi_work = (taxi_to_work/workforce_16)*100)%>%
  mutate(Percent_work_home = (worked_from_home/workforce_16)*100)%>%
  mutate(Percent_walk_work = (walked_to_work/workforce_16)*100)%>%
  mutate(Percent_motorcycle_work = (motorcycle_to_work/workforce_16)*100)%>%
  mutate(Percent_other_way_work = (other_commute_to_work/workforce_16)*100)%>%
  mutate(Percent_carpool_work = (carpooled_to_work/workforce_16)*100)%>%
  mutate(Percent_households_car = (Num_Vehicles/total_households)*100)%>%
  mutate(Percent_households_NOcar = (House_holds_no_vehicles/total_households)*100)
         

