# generate_pakistan_250k.py
# Generates ~250,000 realistic hybrid records:
# 50 districts × 20 diseases × 250 timepoints evenly spread from 2015-01-01 to 2025-12-31
# Saves file: pakpulse_250k_realistic.csv

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ---------------------------
# 50 districts with approx coords
# ---------------------------
district_coords = {
    "Lahore": (31.5497, 74.3436), "Rawalpindi": (33.6167, 73.0667),
    "Faisalabad": (31.4181, 73.0798), "Multan": (30.1575, 71.5249),
    "Gujranwala": (32.1877, 74.1945), "Sialkot": (32.4945, 74.5229),
    "Sargodha": (32.0836, 72.6711), "Bahawalpur": (29.3956, 71.6833),
    "Sheikhupura": (31.7131, 73.9783), "Kasur": (31.1167, 74.4500),
    "Rahim Yar Khan": (28.4200, 70.3000), "Dera Ghazi Khan": (30.0561, 70.6347),
    "Muzaffargarh": (30.0700, 71.1850), "Khanewal": (30.3000, 71.9333),
    "Okara": (30.8100, 73.4500), "Jhang": (31.2686, 72.3269),
    "Vehari": (30.0458, 72.3500), "Mianwali": (32.5833, 71.5333),
    "Attock": (33.7667, 72.3667), "Chakwal": (32.9333, 72.8500),

    "Karachi East": (24.9056, 67.0822), "Karachi West": (24.8783, 66.9936),
    "Karachi South": (24.8090, 66.9910), "Karachi Central": (24.9387, 67.0614),
    "Hyderabad": (25.3960, 68.3578), "Sukkur": (27.7050, 68.8570),
    "Larkana": (27.5600, 68.2100), "Shaheed Benazirabad": (26.2460, 68.4100),
    "Mirpurkhas": (25.5275, 69.0100), "Tharparkar": (25.9842, 70.2488),

    "Peshawar": (34.0151, 71.5805), "Mardan": (34.1975, 72.0406),
    "Swat": (35.2167, 72.4258), "Nowshera": (33.9936, 71.8750),
    "Charsadda": (34.1500, 71.7400), "Abbottabad": (34.1460, 73.2116),
    "Mansehra": (34.3333, 73.2000), "Kohat": (33.5811, 71.4497),
    "Dera Ismail Khan": (31.8328, 70.9020), "Bannu": (32.9864, 70.6069),

    "Quetta": (30.1798, 66.9750), "Gwadar": (25.1214, 62.3256),
    "Kech": (26.0043, 63.0488), "Khuzdar": (27.8147, 66.6117),
    "Sibi": (29.5441, 67.8776), "Nasirabad": (28.9850, 68.1000),
    "Zhob": (31.3400, 69.4489), "Qila Abdullah": (30.8724, 66.4404),
    "Lasbela": (25.7500, 66.5833), "Jaffarabad": (28.3167, 68.2167)
}

# ---------------------------
# 20 common diseases
# ---------------------------
diseases = [
    "Dengue","Malaria","Cholera","Influenza","COVID-19","Typhoid","Hepatitis A","Hepatitis E",
    "Pneumonia","Tuberculosis","Measles","Polio","Diarrhea","Whooping Cough","Mumps",
    "Heatstroke","Skin Infection","Eye Infection","Food Poisoning","Rotavirus"
]

# ---------------------------
# Create 250 timepoints evenly from 2015-01-01 to 2025-12-31
# (keeps long trend but caps dataset size)
# ---------------------------
start = datetime(2015,1,1)
end = datetime(2025,12,31)
total_days = (end - start).days
# sample 250 evenly spaced days across range
indices = np.linspace(0, total_days, 250, dtype=int)
timepoints = [start + timedelta(days=int(i)) for i in indices]

# ---------------------------
# District-level socio-demographics (population_density & sanitation_index)
# Urban districts higher density, better sanitation on average
# ---------------------------
district_meta = {}
for d in district_coords:
    lat, lon = district_coords[d]
    if any(city in d for city in ["Karachi","Lahore","Islamabad","Rawalpindi","Faisalabad","Peshawar"]):
        popdens = int(abs(np.random.normal(8000, 2500))) + 2000      # urban bias
        sanitation = int(np.clip(np.random.normal(75,10), 40, 95))
    elif any(city in d for city in ["Quetta","Gwadar","Khuzdar","Sukkur","Multan"]):
        popdens = int(abs(np.random.normal(3000, 1500))) + 800
        sanitation = int(np.clip(np.random.normal(60,12), 30, 90))
    else:
        popdens = int(abs(np.random.normal(1200, 800))) + 300       # rural-ish
        sanitation = int(np.clip(np.random.normal(50,15), 20, 90))
    district_meta[d] = {"lat": lat, "lon": lon, "population_density": popdens, "sanitation_index": sanitation}

# ---------------------------
# Disease seasonality multipliers (per month 1..12)
# Multipliers based on literature-informed patterns
# ---------------------------
seasonality = {}
# create multipliers arrays for each disease
for dis in diseases:
    if dis == "Dengue":
        seasonality[dis] = np.array([0.2,0.2,0.4,0.6,0.8,1.2,2.0,2.2,1.5,0.8,0.4,0.2])
    elif dis == "Malaria":
        seasonality[dis] = np.array([0.3,0.3,0.5,0.8,1.1,1.5,1.8,1.9,1.2,0.7,0.4,0.3])
    elif dis == "Cholera":
        seasonality[dis] = np.array([0.5,0.6,0.8,1.0,1.3,1.9,2.1,2.0,1.6,1.0,0.7,0.5])
    elif dis == "Influenza":
        seasonality[dis] = np.array([2.0,1.8,1.2,0.8,0.6,0.5,0.4,0.4,0.6,1.0,1.5,2.0])
    elif dis == "COVID-19":
        # multiple waves allowed: mostly year-independent baseline with moderate seasonality
        seasonality[dis] = np.array([1.0,1.0,1.0,1.0,0.95,0.95,1.05,1.1,1.0,1.05,1.1,1.05])
    elif dis in ["Typhoid","Hepatitis A","Hepatitis E","Rotavirus","Diarrhea","Food Poisoning"]:
        seasonality[dis] = np.array([0.8,0.9,1.0,1.1,1.2,1.6,1.9,1.7,1.2,1.0,0.9,0.8])
    elif dis in ["Pneumonia","Tuberculosis","Influenza","Measles","Mumps","Whooping Cough"]:
        seasonality[dis] = np.array([1.8,1.6,1.2,0.9,0.6,0.5,0.4,0.5,0.8,1.2,1.6,1.9])
    else:
        seasonality[dis] = np.ones(12) * 1.0  # default mild seasonality

# ---------------------------
# Long-term trend factors per disease (2015->2025)
# small linear trend multiplier per year (could be + or -)
# ---------------------------
disease_trends = {}
for dis in diseases:
    # random small trend between -3% and +5% per year
    per_year = random.uniform(-0.03, 0.05)
    # create factor for each timepoint based on year offset
    disease_trends[dis] = per_year

# ---------------------------
# Weather model (temp/humidity/rainfall) mean by month (simple)
# We will use sinusoidal functions with district offset to vary climates.
# ---------------------------
def climate_for_date_and_district(date_obj, district):
    # base temp by month approximations (°C) adapted for Pakistan
    month = date_obj.month
    # district latitude influences amplitude: northern districts slightly colder
    lat = district_meta[district]["lat"]
    lat_factor = (lat - 24.5) / 10.0  # approx 0..~1 for N regions
    # temperature: sinusoidal around 25 with amplitude ~12, adjusted by lat
    doy = date_obj.timetuple().tm_yday
    temp = 25 + 12 * np.sin(2*np.pi * (doy/365) - 0.5) - lat_factor*3 + np.random.normal(0,2)
    # rainfall: monsoon peak mid-year, small elsewhere; scale by district (coastal vs inland)
    base_rain = max(0, 40 * np.sin(2*np.pi * ((doy/365) - 0.15)))  # peaks ~monsoon
    # coastal districts (e.g. Karachi, Gwadar) have different rainfall scaling
    coastal = any(c in district for c in ["Karachi","Gwadar","Lasbela"])
    rain = max(0, base_rain * (0.8 if coastal else 1.0) + np.random.normal(0,5))
    # humidity correlates with rainfall and temp
    humidity = np.clip(50 + (rain/5) - (temp-25)/3 + np.random.normal(0,5), 15, 98)
    return round(temp,2), round(humidity,2), round(rain,2)

# ---------------------------
# Core generation loop (build exactly 250 timepoints × 50 × 20 = 250,000 rows)
# ---------------------------
records = []
timepoint_count = len(timepoints)  # should be 250
print(f"Generating dataset: {len(district_coords)} districts × {len(diseases)} diseases × {timepoint_count} timepoints = {len(district_coords)*len(diseases)*timepoint_count} rows")

for district in district_coords.keys():
    meta = district_meta[district]
    pop_density = meta["population_density"]
    sanitation = meta["sanitation_index"]
    # district risk multiplier from socioeconomics
    # higher density and lower sanitation → higher baseline case multiplier
    district_risk = (pop_density / 10000.0) * (1 + (50 - sanitation)/100.0)  # ~0.0..>1.0

    for disease in diseases:
        # baseline incidence rate per disease (cases per timepoint for a standard district)
        # set per-disease base to reflect commonality
        if disease in ["Dengue","Malaria","Influenza","COVID-19","Typhoid","Pneumonia","Tuberculosis"]:
            base_rate = random.uniform(5, 20)
        elif disease in ["Cholera","Diarrhea","Rotavirus","Food Poisoning","Hepatitis A","Hepatitis E"]:
            base_rate = random.uniform(2, 12)
        else:
            base_rate = random.uniform(1, 8)

        # apply small disease-specific trend per year
        per_year_trend = disease_trends[disease]

        for t_idx, date_obj in enumerate(timepoints):
            month = date_obj.month
            # climate
            temp, humidity, rainfall = climate_for_date_and_district(date_obj, district)

            # seasonality factor (based on disease & month)
            seasonal = seasonality[disease][month-1]

            # years since 2015 to compute long-term trend
            years_since_2015 = (date_obj.year - 2015)
            trend_mult = 1.0 + per_year_trend * years_since_2015

            # random shock events (rare) - simulate occasional spikes
            shock = 1.0
            if random.random() < 0.002:  # 0.2% chance of local spike at any (district,disease,time)
                shock = random.uniform(1.8, 4.0)

            # environmental amplification: e.g., high rainfall amplifies vector/waterborne diseases
            env_amp = 1.0
            if disease in ["Dengue","Malaria"]:
                env_amp *= (1.0 + min(rainfall/100.0, 2.0))
                env_amp *= (1.0 + max(0, (humidity-60)/100.0))
            if disease in ["Cholera","Diarrhea","Rotavirus"]:
                env_amp *= (1.0 + min(rainfall/80.0, 2.5))

            # compute expected cases (float)
            expected = base_rate * seasonal * trend_mult * (1.0 + district_risk) * env_amp * (pop_density/3000.0)

            # add stochastic noise
            cases = np.random.negative_binomial(n=max(1,int(expected+1)), p=0.5) if expected>5 else max(0, int(np.random.poisson(max(0.1, expected))))
            # small smoothing to avoid zero everywhere
            if cases < 0:
                cases = 0
            # cap to avoid unrealistic extremes
            cases = int(min(cases, 5000))

            records.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "district": district,
                "lat": meta["lat"],
                "lon": meta["lon"],
                "disease": disease,
                "cases": cases,
                "temperature": temp,
                "humidity": humidity,
                "rainfall": rainfall,
                "population_density": pop_density,
                "sanitation_index": sanitation
            })

# ---------------------------
# Build DataFrame & compute lags
# ---------------------------
df = pd.DataFrame.from_records(records)
# sort and compute lag_1/2/3 per district+disease ordered by date (timepoints are monotonic)
df = df.sort_values(['district','disease','date']).reset_index(drop=True)

# compute lag columns (previous 1,2,3 timepoints for same district+disease)
df['lag_1'] = df.groupby(['district','disease'])['cases'].shift(1).fillna(0).astype(int)
df['lag_2'] = df.groupby(['district','disease'])['cases'].shift(2).fillna(0).astype(int)
df['lag_3'] = df.groupby(['district','disease'])['cases'].shift(3).fillna(0).astype(int)

# reorder columns
cols = ["date","district","lat","lon","disease","cases","lag_1","lag_2","lag_3",
        "temperature","humidity","rainfall","population_density","sanitation_index"]
df = df[cols]

# ---------------------------
# Save CSV and print path
# ---------------------------
OUTPUT = "pakpulse_250k_realistic.csv"
df.to_csv(OUTPUT, index=False)
print("Saved dataset to:", os.path.abspath(OUTPUT))
print("Total rows:", len(df))
print(df.head(10))
