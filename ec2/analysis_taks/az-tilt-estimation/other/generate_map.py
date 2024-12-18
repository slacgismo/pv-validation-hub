import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import rioxarray
import numpy as np
import pandas as pd

# written for:
# - cartopy==0.18.0
# - rioxarray==0.13.4
# - matplotlib==3.4.3

# example locations.  replace these with your coordinates
df = pd.read_csv("./data/system_metadata.csv")
lats = df["latitude"]
lons = df["longitude"]

# read PSM3 raster file
# download rasters from: https://www.nrel.gov/gis/solar-resource-maps.html
# this uses the annual file
fn = "./data/nsrdb3_ghi.tif"
psm3 = rioxarray.open_rasterio(fn)

psm3 = psm3.squeeze("band")  # drop useless `band` dimension
psm3 = psm3.where(psm3 > 0, np.nan)  # replace zero values w/ nan (ocean)
psm3 = psm3.sel(x=slice(-130, -60), y=slice(55, 24))  # bounds order matters

# %%

fig = plt.figure(figsize=(6.5, 3), dpi=225)
ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertConformal())
ax.set_extent([-120, -72, 23, 49.5], ccrs.Geodetic())

ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES, linewidth=0.25)

psm3.plot.pcolormesh(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="YlOrRd",
    cbar_kwargs=dict(label="Average GHI [kWh/m$^2$/day]"),
)
ax.set_title(None)  # hide irksome xarray default title

ax.scatter(
    lons,
    lats,
    transform=ccrs.PlateCarree(),
    zorder=100,
    c="white",
    edgecolors="black",
    s=50,
)

# gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, linestyle=':', color='black')
# gl.top_labels = False
# gl.right_labels = False

# gl.xlabel_style = {'rotation': 0}
# gl.ylabel_style = {'rotation': 0}

# # hide irksome label on the right side:
# plt.pause(1)
# gl.bottom_label_artists[-1].set_text('')

fig.savefig("./results/validation_location_resource_map.png")
