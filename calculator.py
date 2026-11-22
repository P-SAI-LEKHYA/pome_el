import json
import pandas as pd
from config import WORKLOADS, SUPPORT_MONTHLY_USD, FREE_EGRESS_GB, USD_INR, FX_DATE

def load(p):
    with open(f"{p}_extra.json") as f:
        return json.load(f)

DATA = {"AWS": load("aws"), "Azure": load("azure"), "GCP": load("gcp")}

def egress_cost(tiers, gb, free_gb=0):
    billable = max(0.0, gb - free_gb)
    cost = 0.0
    for start, end, price in sorted(tiers, key=lambda t: t[0]):
        if billable <= start:
            break
        upper = billable if end is None else min(billable, end)
        cost += (upper - start) * price
    return cost

rows, warn = [], set()
for prov, d in DATA.items():
    if d["storage_gb_month_usd"] is None: warn.add(f"{prov}: storage price missing")
    if not d["egress_tiers"]: warn.add(f"{prov}: egress tiers missing")
    if SUPPORT_MONTHLY_USD[prov] is None: warn.add(f"{prov}: support plan cost not set (counted as 0)")
    for wl, sp in WORKLOADS.items():
        od = d["compute_ondemand_monthly_usd"].get(wl)
        ri = d["compute_1yr_monthly_usd"].get(wl)
        storage = (d["storage_gb_month_usd"] or 0) * sp["storage_gb"]
        egress = egress_cost(d["egress_tiers"], sp["egress_gb"], FREE_EGRESS_GB[prov])
        support = SUPPORT_MONTHLY_USD[prov] or 0
        exit_cost = egress_cost(d["egress_tiers"], sp["storage_gb"], FREE_EGRESS_GB[prov])
        extras = storage + egress + support
        rows.append({
            "workload": wl, "provider": prov, "compute_od": od, "compute_1yr": ri,
            "storage": storage, "egress": egress, "support": support,
            "total_od": None if od is None else od + extras,
            "total_1yr": None if ri is None else ri + extras,
            "hidden_share_od": None if od is None else extras / (od + extras),
            "exit_cost": exit_cost,
        })

df = pd.DataFrame(rows)
for c in ["compute_od", "compute_1yr", "storage", "egress", "support", "total_od", "total_1yr", "exit_cost"]:
    df[c + "_inr"] = df[c] * USD_INR
df.to_csv("results.csv", index=False)

pd.set_option("display.width", 220)
for wl in WORKLOADS:
    sub = df[df["workload"] == wl].set_index("provider")
    print(f"\n=== {wl} (USD per month; INR at {USD_INR} on {FX_DATE}) ===")
    print(sub[["compute_od", "compute_1yr", "storage", "egress", "support", "total_od", "total_1yr",
               "hidden_share_od", "exit_cost"]].astype(float).round(2).to_string())
    for col in ["total_od", "total_1yr"]:
        v = sub[col].astype(float).dropna()
        if len(v):
            print(f"cheapest {col}: {v.idxmin()}  USD {v.min():.2f}  (INR {v.min() * USD_INR:,.0f})")

print("\nWARNINGS:" if warn else "\nNo warnings.")
for w in sorted(warn):
    print(" -", w)
print("\nsaved results.csv")