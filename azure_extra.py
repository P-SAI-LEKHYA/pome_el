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

# storage: Premium SSD P30 (1024 GiB) divided by 1024 = per GB-month
st = fetch(f"serviceName eq 'Storage' and armRegionName eq '{AZURE_REGION}' and "
           f"contains(productName, 'Premium SSD Managed Disks') and contains(skuName, 'P30')")
if st.empty:
    print("NO storage rows for P30. Try contains(meterName,'P30') in the filter.")
else:
    print(st[["productName", "skuName", "meterName", "unitOfMeasure", "retailPrice", "type"]].to_string())
    m = st[(st["type"] == "Consumption") & (st["skuName"] == "P30 LRS") &
           (st["unitOfMeasure"].str.contains("Month"))]
    if not m.empty:
        out["storage_gb_month_usd"] = float(m.iloc[0]["retailPrice"]) / 1024

# egress: Central India is in Azure bandwidth Zone 2
bw = fetch("serviceName eq 'Bandwidth'")
if bw.empty:
    print("No bandwidth rows returned.")
else:
    text = bw[["productName", "skuName", "meterName", "location", "armRegionName"]].astype(str).agg(" ".join, axis=1)
    zone2 = text.str.contains(f"Zone 2|{AZURE_REGION}", case=False)
    outbound = text.str.contains("Data Transfer Out|Outbound", case=False)
    cand = bw[zone2 & outbound & (bw["type"] == "Consumption") & bw["unitOfMeasure"].str.contains("GB")]
    cand.to_csv("azure_bandwidth_candidates.csv", index=False)
    combos = cand[["productName", "meterName"]].drop_duplicates()
    print("\nEgress candidates (Zone 2):")
    print(combos.to_string())
    pick = None
    if AZURE_EGRESS_METER:
        pick = cand[cand["meterName"] == AZURE_EGRESS_METER]
    elif len(combos) == 1:
        pick = cand
    else:
        p = cand[cand["meterName"].str.contains("Standard Data Transfer Out", case=False)]
        pick = p if not p.empty else None
    if pick is None or pick.empty:
        print("\nCould not decide. If nothing printed above, check the zone text; otherwise copy the right")
        print("meterName into AZURE_EGRESS_METER in config.py and rerun.")
    else:
        pick = pick.sort_values("tierMinimumUnits").drop_duplicates("tierMinimumUnits")
        starts = pick["tierMinimumUnits"].astype(float).tolist()
        prices = pick["retailPrice"].astype(float).tolist()
        for i, s in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else None
            out["egress_tiers"].append([s, end, prices[i]])
        print("\nEgress tiers used:", out["egress_tiers"])

with open("azure_extra.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nsaved azure_extra.json")