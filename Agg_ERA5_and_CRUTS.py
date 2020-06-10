# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Comparing ERA5 and CRU-TS

import xarray as xr
import scipy
import numpy as np
from pathlib import Path

# ERA5 monthly data are about 1.1 GB compressed, so it should be fine to load it all together.
# The CRU-TS gridded data are also on the GB scale.

# +
# # Load the CRU-TS observation data
# cruts_obs_path = Path("/badc/cru/data/cru_ts/cru_ts_4.04/observations/")
# cruts_obs_path_tmp = cruts_observation_path / "tmp.2004011744.clean.dtb"

# with open(cruts_obs_path_tmp, 'r') as f:
#     for line in f:
#         # some lines contain the locations
#         if line.isupper() or line.islower():
#             words = line.split(' ')
#             station_id = words[0]
#             latitude = words[1]
#             longitude = words[3]
#             elevation = words[4]
#             name = ' '.join(words[5:-2])
#             min_year = words[-2]
#             max_year = words[-1]
            
# #             print(station_id,
# #                 latitude,
# #                 longitude,
# #                 elevation,
# #                 name,
# #                 min_year,
# #                 max_year)
#         else:
#             # other lines 
#             pass


# +
# Load the CRU-TS gridded data
cruts_grid_path = Path("data/")
cruts_grid_tmp_path = cruts_grid_path / "cru_ts4.04.1901.2019.tmp.dat.nc"

cruts_grid_tmp = xr.open_dataset(cruts_grid_tmp_path)
cruts_grid_tmp

# +
# Load the CRU-TS gridded data
cruts_grid_path = Path("data/")
cruts_grid_tmx_path = cruts_grid_path / "cru_ts4.04.1901.2019.tmx.dat.nc"

cruts_grid_tmx = xr.open_dataset(cruts_grid_tmx_path)
cruts_grid_tmx

# +
# cruts_grid_tmp.sel(time='2000-06').stn.plot()

# +
# cruts_grid_tmp.sel(time='1950-06').stn.plot()

# +
# load the ERA5 data
era5_direc = Path("/gws/nopw/j04/bas_climate/data/ecmwf/era5/")
era5_t2m_path = era5_direc / "monthly" / "t2m"
era5_t2m_glob = era5_t2m_path.glob("*.nc")

era5_t2m = xr.open_mfdataset(era5_t2m_glob, combine="nested", concat_dim="time")

era5_t2m
# -

# select overlapping time period
min_time = np.maximum(era5_t2m.time.min(), cruts_grid_tmp.time.min())
max_time = np.minimum(era5_t2m.time.max(), cruts_grid_tmp.time.max())
print (min_time.values, max_time.values)

era5_t2m

cruts_grid_tmp

# select matching data periods
cruts_tmp_sel = cruts_grid_tmp.sel(time=slice(min_time, max_time))
era5_t2m_sel = era5_t2m.sel(time=slice(min_time, max_time))

# rename lat/lon in era5
era5_t2m_sel = era5_t2m_sel.rename({"latitude": "lat", "longitude": "lon"})

# align the era5 longitude
era5_t2m_sel = era5_t2m_sel.assign_coords(lon=(((era5_t2m_sel.lon + 180) % 360) - 180))

# +
# make latitude ascending in era5
#era5_t2m_sel = era5_t2m_sel.sortby([era5_t2m_sel.lon, era5_t2m_sel.lat, era5_t2m_sel.time])

# +
# # take a location slice
# region = {"lat": slice(8, 38), "lon": slice(68,99)}
# cruts_tmp_sel = cruts_tmp_sel.sel(**region)
# era5_t2m_sel = era5_t2m_sel.sel(**region)
# -

cruts_tmp_sel

era5_t2m_sel

# get the monthly averages
cruts_tmp_months = cruts_tmp_sel.groupby("time.month").mean()

era5_t2m_months = era5_t2m_sel.groupby("time.month").mean()

# +
# get the difference between the models
# difference = era5_t2m_months['t2m'] - cruts_tmp_months['tmp']

# +
# because the previous computation steps are lazy, this is the step that will do the computation, possibly making it slow.
# difference.to_netcdf(Path("data") / "difference.nc")
# -

era5_t2m_months.to_netcdf("data/era5_mavg.nc")

cruts_tmp_months.to_netcdf("data/cruts_mavg.nc")
