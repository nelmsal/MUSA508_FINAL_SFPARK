
``` {r meters}

path = "C:/Users/nelms/Documents/Penn/MUSA-508/MUSA508_FINAL_SFPARK/data/Parking Meters.geojson"
park.meters = st_read(path) %>%
  st_drop_geometry() %>%
  select(blockface_id, pm_district_id) %>%
  transmute(
    id.block = blockface_id %>% 
      as.integer() %>% as.character(),
    id.district = pm_district_id %>% 
      as.integer() %>% as.character()
  ) %>%
  distinct() %>% 
  filter(
    !(id.block==443003&id.district==14)
  )

park.import %>%
  select(-dist_id) %>%
  left_join(
    .,
    park.meters %>%
      rename(
        block_id = id.block,
        dist_id = id.district
        ),
    on = 'block_id'
  ) %>%
  write_parquet(
    'C:/Users/nelms/Documents/Penn/MUSA-508/MUSA508_FINAL_SFPARK/data/block_count_occ.parquet'
  )

```


if madi:
  give.smooch()
  if horny:
    bonk <- boobers
  else:
    if dirt:
      run gravel_smooch
    elif wooorm:
      dig_in_coochie
  if cute_night & 'Dec_23_2021':
    snug & watch_coot_movie
    return (wrap gift)
if not madi:
    kill