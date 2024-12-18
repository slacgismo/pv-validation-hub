# -*- coding: utf-8 -*-
"""
PVWatts v5 modeled energy using real az-tilt vs predicted az-tilt
"""

import pvlib
import pandas as pd

# Read in the metadata, which contains the ground-truth az-tilt estimates
metadata = pd.read_csv("./data/system_metadata.csv")

for index, row in metadata.iterrows():
    sys_id = row["system_id"]
    tilt = row["tilt"]
    az = row["azimuth"]
    latitude = row["latitude"]
    longitude = row["longitude"]
    # Read in TMY from NSRDB (one year only so we're consistent??)

    location = pvlib.location.Location(latitude, longitude)

    tracker_data = pvlib.tracking.singleaxis(
        solar_position["apparent_zenith"],
        solar_position["azimuth"],
        axis_azimuth=180,
    )
    tilt = tracker_data["surface_tilt"].fillna(0)
    azimuth = tracker_data["surface_azimuth"].fillna(0)

    df_poa_tracker = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=df_tmy["DNI"],
        ghi=df_tmy["GHI"],
        dhi=df_tmy["DHI"],
        solar_zenith=solar_position["apparent_zenith"],
        solar_azimuth=solar_position["azimuth"],
    )
    tracker_poa = df_poa_tracker["poa_global"]

    parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"][
        "open_rack_glass_polymer"
    ]
    cell_temperature = pvlib.temperature.sapm_cell(
        tracker_poa, df_tmy["DryBulb"], df_tmy["Wspd"], **parameters
    )

    pvlib.pvsystem.pvwatts_dc(
        g_poa_effective, temp_cell, pdc0, gamma_pdc, temp_ref=25.0
    )

    pvlib.inverter.pvwatts(pdc, pdc0, eta_inv_nom=0.96, eta_inv_ref=0.9637)
