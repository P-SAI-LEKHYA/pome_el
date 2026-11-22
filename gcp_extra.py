import json, requests, pandas as pd
from config import WORKLOADS, GCP_SERVICE_ID, HOURS_PER_MONTH, GCP_EGRESS_DESCRIPTION

API_KEY = "your_key"   # keep private, never put it in your report

url = f"https://cloudbilling.googleapis.com/v1/services/{GCP_SERVICE_ID}/skus"
params = {"key": API_KEY, "pageSize": 5000}   # USD by default
skus = []
while True:
    data = requests.get(url, params=params, timeout=60).json()
    if "skus" not in data:
        print("API problem:", data)
        raise SystemExit
    skus += data["skus"]
    if not data.get("nextPageToken"):
        break
    params["pageToken"] = data["nextPageToken"]
print("SKUs downloaded:", len(skus))

def money(u):
    return int(u.get("units", 0)) + u.get("nanos", 0) / 1e9

def tiers_of(s):
    t = s["pricingInfo"][0]["pricingExpression"]["tieredRates"]
    res = []
    for i, x in enumerate(t):
        start = float(x.get("startUsageAmount", 0))
        end = float(t[i + 1].get("startUsageAmount", 0)) if i + 1 < len(t) else None
        res.append([start, end, money(x["unitPrice"])])
    return res

def find(pred):
    return [s for s in skus if pred(s)]

def show(label, rows):
    print(f"\n{label}: {len(rows)} match(es)")
    for s in rows:
        t = tiers_of(s)
        p = t[0][2] if t else "N/A"
        print("  ", s["description"], "|", p, s["pricingInfo"][0]["pricingExpression"]["usageUnit"])

out = {"compute_ondemand_monthly_usd": {}, "compute_1yr_monthly_usd": {},
       "storage_gb_month_usd": None, "egress_tiers": [], "egress_basis": ""}

core = find(lambda s: s["description"] == "N2 Instance Core running in Mumbai" and s["category"]["usageType"] == "OnDemand")
ram = find(lambda s: s["description"] == "N2 Instance Ram running in Mumbai" and s["category"]["usageType"] == "OnDemand")
cud_core = find(lambda s: all(k in s["description"].lower() for k in ["commitment", "n2 cpu", "mumbai", "1 year"]) and "sole" not in s["description"].lower())
cud_ram = find(lambda s: all(k in s["description"].lower() for k in ["commitment", "n2 ram", "mumbai", "1 year"]) and "sole" not in s["description"].lower())
show("N2 core on-demand", core); show("N2 RAM on-demand", ram)
show("N2 core 1-year commitment", cud_core); show("N2 RAM 1-year commitment", cud_ram)

if core and ram:
    c, r = tiers_of(core[0])[0][2], tiers_of(ram[0])[0][2]
    for wl, sp in WORKLOADS.items():
        out["compute_ondemand_monthly_usd"][wl] = (sp["vcpu"] * c + sp["ram_gb"] * r) * HOURS_PER_MONTH
if cud_core and cud_ram:
    c, r = tiers_of(cud_core[0])[0][2], tiers_of(cud_ram[0])[0][2]
    for wl, sp in WORKLOADS.items():
        out["compute_1yr_monthly_usd"][wl] = (sp["vcpu"] * c + sp["ram_gb"] * r) * HOURS_PER_MONTH

disk = find(lambda s: s["description"].startswith("Balanced PD Capacity") and "Mumbai" in s["description"])
show("Balanced PD storage", disk)
if disk:
    out["storage_gb_month_usd"] = tiers_of(disk[0])[0][2]

# egress: Standard Tier SKU has a known name; Premium Tier candidates are saved for you to choose from
cands = find(lambda s: "Mumbai" in s["description"] and "Data Transfer Out" in s["description"] and "Internet" in s["description"]
             and not any(k in s["description"] for k in ["Inter Region", "Vpn", "Interconnect", "Carrier", "CDN", "Standard", "Google Services"]))
pd.DataFrame([{"description": s["description"], "first_tier_price": tiers_of(s)[0][2] if tiers_of(s) else None} for s in cands]).to_csv("gcp_egress_candidates.csv", index=False)
show("Premium-tier egress candidates (saved to gcp_egress_candidates.csv)", cands)

target = GCP_EGRESS_DESCRIPTION or "Network Standard Data Transfer Out to Internet from Mumbai"
eg = find(lambda s: s["description"] == target)
show("Egress SKU used", eg)
if eg:
    out["egress_tiers"] = tiers_of(eg[0])
    out["egress_basis"] = target

with open("gcp_extra.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nsaved gcp_extra.json")