import json, requests, pandas as pd
from config import AZURE_SKUS, AZURE_REGION, HOURS_PER_MONTH, AZURE_EGRESS_METER

def fetch(filter_str):
    url = "https://prices.azure.com/api/retail/prices"
    params = {"api-version": "2023-01-01-preview", "currencyCode": "USD", "$filter": filter_str}
    rows = []
    while url:
        data = requests.get(url, params=params, timeout=60).json()
        rows += data.get("Items", [])
        url, params = data.get("NextPageLink"), None
    return pd.DataFrame(rows)

out = {"compute_ondemand_monthly_usd": {}, "compute_1yr_monthly_usd": {},
       "storage_gb_month_usd": None, "egress_tiers": []}

# compute: on-demand and 1-year reservation (reservation price is for the whole term, so /12)
for wl, sku in AZURE_SKUS.items():
    df = fetch(f"serviceName eq 'Virtual Machines' and armRegionName eq '{AZURE_REGION}' and armSkuName eq '{sku}'")
    if df.empty:
        print("NO ROWS for", sku)
        continue
    df = df[~df["productName"].str.contains("Windows", case=False)]
    df = df[~df["skuName"].str.contains("Spot|Low Priority", case=False)]
    od = df[df["type"] == "Consumption"]
    ri = df.iloc[0:0]
    if "reservationTerm" in df.columns:
        ri = df[(df["type"] == "Reservation") & (df["reservationTerm"] == "1 Year")]
    print(wl, sku, "| on-demand rows:", len(od), "| 1-year rows:", len(ri))
    if not od.empty:
        out["compute_ondemand_monthly_usd"][wl] = float(od.iloc[0]["retailPrice"]) * HOURS_PER_MONTH
    if not ri.empty:
        out["compute_1yr_monthly_usd"][wl] = float(ri.iloc[0]["retailPrice"]) / 12

# storage: Azure Premium SSD Managed Disks (Provisioned Tiers P1 to P80)
TIER_GIB = {
    "P1": 4, "P2": 8, "P3": 16, "P4": 32, "P6": 64, "P10": 128,
    "P15": 256, "P20": 512, "P30": 1024, "P40": 2048, "P50": 4096,
    "P60": 8192, "P70": 16384, "P80": 32768
}

out["storage_provisioned_tiers"] = []
st = fetch(f"serviceName eq 'Storage' and armRegionName eq '{AZURE_REGION}' and "
           f"contains(productName, 'Premium SSD Managed Disks')")
if st.empty:
    print("NO storage rows found for Premium SSD Managed Disks.")
else:
    lrs = st[(st["type"] == "Consumption") & (st["meterName"].str.endswith(" LRS Disk")) &
             (~st["meterName"].str.contains("Mount|Burst"))]
    for _, r in lrs.iterrows():
        sku = r["skuName"].replace(" LRS", "").strip()
        if sku in TIER_GIB:
            out["storage_provisioned_tiers"].append({
                "tier": sku,
                "gib": TIER_GIB[sku],
                "price_usd": float(r["retailPrice"])
            })
    out["storage_provisioned_tiers"].sort(key=lambda x: x["gib"])
    # Reference per-GB rate for P30 (1024 GiB) kept for backward compatibility/reference
    p30_match = [t for t in out["storage_provisioned_tiers"] if t["tier"] == "P30"]
    out["storage_gb_month_usd"] = (p30_match[0]["price_usd"] / 1024) if p30_match else 0.13200195
    print("Ingested provisioned disk tiers:", len(out["storage_provisioned_tiers"]))
    for t in out["storage_provisioned_tiers"][:7]:
        print(f"  {t['tier']} ({t['gib']} GiB): ${t['price_usd']:.2f}/mo")

# egress: Central India (Zone 2) - Microsoft Global Network (Standard Default)
bw = fetch("serviceName eq 'Bandwidth'")
if bw.empty:
    print("No bandwidth rows returned.")
else:
    text = bw[["productName", "skuName", "meterName", "location", "armRegionName"]].astype(str).agg(" ".join, axis=1)
    zone2 = text.str.contains(f"Zone 2|{AZURE_REGION}", case=False)
    outbound = text.str.contains("Data Transfer Out|Outbound", case=False)
    cand = bw[zone2 & outbound & (bw["type"] == "Consumption") & bw["unitOfMeasure"].str.contains("GB")]
    cand.to_csv("azure_bandwidth_candidates.csv", index=False)
    
    # Filter strictly for Microsoft Global Network (MGN) and Standard Data Transfer Out
    # to avoid mixing with Routing Preference: Internet (Transit ISP)
    mgn = cand[(cand["productName"] == "Rtn Preference: MGN") & (cand["meterName"] == "Standard Data Transfer Out")]
    if mgn.empty:
        print("WARNING: No exact match for Rtn Preference: MGN. Inspect azure_bandwidth_candidates.csv")
    else:
        mgn = mgn.sort_values("tierMinimumUnits").drop_duplicates("tierMinimumUnits")
        starts = mgn["tierMinimumUnits"].astype(float).tolist()
        prices = mgn["retailPrice"].astype(float).tolist()
        out["egress_tiers"] = []
        for i, s in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else None
            out["egress_tiers"].append([s, end, prices[i]])
        print("\nClean Azure MGN egress tiers used:", out["egress_tiers"])

with open("azure_extra.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nsaved azure_extra.json")