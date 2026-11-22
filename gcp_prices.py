import requests, pandas as pd

API_KEY = "AIzaSyAZlKO10utCVCQpzV3J1D9UBCP2daZDILk"
SERVICE_ID = "6F81-5844-456A"  # Compute Engine
REGION = "asia-south1"         # Mumbai
MACHINES = {"A_Startup": (2, 8), "B_Midsize": (8, 32), "C_DataHeavy": (16, 64)}  # (vCPU, RAM GB), n2-standard shape

url = f"https://cloudbilling.googleapis.com/v1/services/{SERVICE_ID}/skus"
params = {"key": API_KEY, "currencyCode": "INR", "pageSize": 5000}
skus = []
while True:
    data = requests.get(url, params=params, timeout=60).json()
    skus += data.get("skus", [])
    if not data.get("nextPageToken"):
        break
    params["pageToken"] = data["nextPageToken"]

rows = []
for s in skus:
    d = s["description"]
    if REGION not in s.get("serviceRegions", []):
        continue
    if not (d.startswith("N2 Instance Core running in") or d.startswith("N2 Instance Ram running in")):
        continue
    if any(x in d for x in ["Custom", "Spot", "Preemptible", "Sole"]):
        continue
    tr = s["pricingInfo"][0]["pricingExpression"]["tieredRates"][0]["unitPrice"]
    rows.append({
        "description": d, "usage_type": s["category"]["usageType"],
        "unit": s["pricingInfo"][0]["pricingExpression"]["usageUnit"],
        "price_inr": int(tr.get("units", 0)) + tr.get("nanos", 0) / 1e9,
        "effective": s["pricingInfo"][0]["effectiveTime"],
    })

df = pd.DataFrame(rows)
print("rows matched:", len(df))
print(df.to_string())
df.to_csv("gcp_prices.csv", index=False)

# Quick estimate for on-demand: hourly = vCPU * core price + RAM * ram price
od = df[df["usage_type"] == "OnDemand"]
core = od[od["description"].str.contains("Core")]["price_inr"].iloc[0]
ram = od[od["description"].str.contains("Ram")]["price_inr"].iloc[0]
for w, (cpu, gb) in MACHINES.items():
    print(w, "monthly INR (730h):", round((cpu * core + gb * ram) * 730, 2))