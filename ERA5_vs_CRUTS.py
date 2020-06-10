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

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Load my monthly averaged data - see 'Agg_ERA5_and_CRUTS.ipynb'
da_era5 = xr.open_dataset("data/era5_mavg.nc")
da_cruts = xr.open_dataset("data/cruts_mavg.nc")

# get the ERA5 land-sea mask
era5_lsm = xr.open_dataset("/gws/nopw/j04/bas_climate/data/ecmwf/era5/invariant/era5_invariant_lsm.nc")

# make the lsm match the data
era5_lsm = era5_lsm.squeeze().drop("time").rename({"latitude": "lat", "longitude": "lon"})

# realign the data to be centered on 0 longitude
if da_era5.lon.min() >= 0:
    da_era5 = da_era5.assign_coords(lon=(((da_era5.lon + 180) % 360) - 180))
if era5_lsm.lon.min() >= 0:
    era5_lsm = era5_lsm.assign_coords(lon=(((era5_lsm.lon + 180) % 360) - 180))

# re-sort the axes
da_era5 = da_era5.sortby(['lon', 'lat', 'month'])
era5_lsm = era5_lsm.sortby(['lon', 'lat'])

# drop ocean
da_era5 = da_era5.where(era5_lsm["lsm"])

# take the difference between ERA5 and CRU-TS
da_diff = (da_era5["t2m"] - 273.15 - da_cruts["tmp"])

# map the difference - taking the maximum across months
fig = plt.figure(figsize=(20,8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
da_diff.max("month").plot(ax=ax)

da_diff

da_diff.plot(bins=np.linspace(-15, 15, 30))

da_cruts

fig, ax = plt.subplots(2,1, figsize=(10,15))
(da_era5["t2m"] - 273.15).sel(month=6).plot(ax=ax[0], label="ERA5")
da_cruts["tmp"].sel(month=6).plot(ax=ax[1], label="CRU-TS")

da_coast.where(da_diff<-2).max("month").plot()

# quickly identify cells that are coastal
da_coast = np.logical_or(era5_lsm["lsm"].differentiate("lat")!=0, era5_lsm["lsm"].differentiate("lon")!=0)

fig = plt.figure(figsize=(20,8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
da_coast.plot()

bins=np.linspace(-10,10,40)
da_diff.where(da_coast>0).plot(density=True, label="Coast", bins=bins)
da_diff.where(da_coast==0).plot(density=True, alpha=0.5, label="Not coast", bins=bins)
plt.legend()

fig = plt.figure(figsize=(20,8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
da_diff.where(da_coast>0).min("month").plot()

# NB this is not a proper area average
da_diff.where(da_coast>0).mean(["lat", "lon"]).plot(label="Coast")
da_diff.where(da_coast==0).mean(["lat", "lon"]).plot(alpha=0.5, label="Not coast")
plt.legend()

# NB this is not a proper area average
da_diff.where(da_coast>0).mean("month").plot(label="Coast")


