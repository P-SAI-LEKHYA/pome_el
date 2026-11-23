import json, requests, pandas as pd
from config import AZURE_SKUS, AZURE_REGION, HOURS_PER_MONTH

# Tiers mapping in GiB
TIER_GIB = {
    "P1": 4, "P2": 8, "P3": 16, "P4": 32, "P6": 64, "P10": 128,
    "P15": 256, "P20": 512, "P30": 1024, "P40": 2048, "P50": 4096,
    "P60": 8192, "P70": 16384, "P80": 32768
}

def fetch(filter_str):
    url = "https://prices.azure.com/api/retail/prices"
    params = {"api-version": "2023-01-01-preview", "currencyCode": "USD", "$filter": filter_str}
    rows = []
    while url:
        data = requests.get(url, params=params, timeout=60).json()
        rows += data.get("Items", [])
        url, params = data.get("NextPageLink"), None
    return pd.DataFrame(rows)

out = {
    "compute_ondemand_monthly_usd": {},
    "compute_1yr_monthly_usd": {},
    "storage_provisioned_tiers": [],
    "egress_tiers": [],
    "egress_product": "Microsoft Global Network (Standard Data Transfer Out, Zone 2)"
}

# 1. Compute
for wl, sku in AZURE_SKUS.items():
    df = fetch(f"serviceName eq 'Virtual Machines' and armRegionName eq '{AZURE_REGION}' and armSkuName eq '{sku}'")
    if df.empty:
        continue
    df = df[~df["productName"].str.contains("Windows", case=False)]
    df = df[~df["skuName"].str.contains("Spot|Low Priority", case=False)]
    od = df[df["type"] == "Consumption"]
    ri = df.iloc[0:0]
    if "reservationTerm" in df.columns:
        ri = df[(df["type"] == "Reservation") & (df["reservationTerm"] == "1 Year")]
    if not od.empty:
        out["compute_ondemand_monthly_usd"][wl] = float(od.iloc[0]["retailPrice"]) * HOURS_PER_MONTH
    if not ri.empty:
        out["compute_1yr_monthly_usd"][wl] = float(ri.iloc[0]["retailPrice"]) / 12

# 2. Storage: Query actual LRS managed disks in centralindia
st = fetch(f"serviceName eq 'Storage' and armRegionName eq '{AZURE_REGION}' and contains(productName, 'Premium SSD Managed Disks')")
lrs_disks = st[(st["type"] == "Consumption") & (st["meterName"].str.endswith(" LRS Disk")) & (~st["meterName"].str.contains("Mount|Burst"))]
for _, r in lrs_disks.iterrows():
    sku = r["skuName"].replace(" LRS", "").strip()
    if sku in TIER_GIB:
        out["storage_provisioned_tiers"].append({
            "tier": sku,
            "gib": TIER_GIB[sku],
            "price_usd": float(r["retailPrice"])
        })
out["storage_provisioned_tiers"].sort(key=lambda x: x["gib"])

# 3. Egress: Microsoft Global Network (MGN)
bw = fetch("serviceName eq 'Bandwidth'")
text = bw[["productName", "skuName", "meterName", "location", "armRegionName"]].astype(str).agg(" ".join, axis=1)
zone2 = text.str.contains(f"Zone 2|{AZURE_REGION}", case=False)
outbound = text.str.contains("Data Transfer Out|Outbound", case=False)
cand = bw[zone2 & outbound & (bw["type"] == "Consumption") & bw["unitOfMeasure"].str.contains("GB")]

# Filter specifically for MGN and Standard Data Transfer Out
mgn = cand[(cand["productName"] == "Rtn Preference: MGN") & (cand["meterName"] == "Standard Data Transfer Out")]
mgn = mgn.sort_values("tierMinimumUnits").drop_duplicates("tierMinimumUnits")
starts = mgn["tierMinimumUnits"].astype(float).tolist()
prices = mgn["retailPrice"].astype(float).tolist()
for i, s in enumerate(starts):
    end = starts[i + 1] if i + 1 < len(starts) else None
    out["egress_tiers"].append([s, end, prices[i]])

print("Storage tiers count:", len(out["storage_provisioned_tiers"]))
print("First 3 storage tiers:", out["storage_provisioned_tiers"][:3])
print("Egress tiers count:", len(out["egress_tiers"]))
print("Egress tiers:", out["egress_tiers"])
