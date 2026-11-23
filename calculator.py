import json
import pandas as pd
from config import WORKLOADS, FREE_EGRESS_GB, USD_INR, FX_DATE, HOURS_PER_MONTH

def load(p):
    with open(f"{p}_extra.json") as f:
        return json.load(f)

DATA = {"AWS": load("aws"), "Azure": load("azure"), "GCP": load("gcp")}

def gb_to_gib(gb):
    return (gb * 1e9) / (2**30)

def egress_cost(tiers, gb, free_gb=0):
    billable = max(0.0, gb - free_gb)
    cost = 0.0
    for start, end, price in sorted(tiers, key=lambda t: t[0]):
        if billable <= start:
            break
        upper = billable if end is None else min(billable, end)
        cost += (upper - start) * price
    return cost

def azure_storage_cost(gb, tiers=None):
    if tiers is None:
        tiers = DATA["Azure"].get("storage_provisioned_tiers", [])
    gib = gb_to_gib(gb)
    for t in tiers:
        if gib <= t["gib"]:
            return t["tier"], t["gib"], t["price_usd"]
    # Fallback to last available tier
    if tiers:
        last = tiers[-1]
        return last["tier"], last["gib"], last["price_usd"]
    return "P30", 1024, 135.17

def compute_storage(prov, gb):
    if prov == "Azure":
        t_name, t_gib, price = azure_storage_cost(gb)
        return price, f"{t_name} ({t_gib} GiB)"
    elif prov == "AWS":
        rate = DATA["AWS"]["storage_gb_month_usd"] or 0.0912
        return gb * rate, f"gp3 ({gb} GB @ ${rate}/GB)"
    elif prov == "GCP":
        rate = DATA["GCP"]["storage_gb_month_usd"] or 0.12
        return gb * rate, f"Balanced PD ({gb} GB @ ${rate}/GB)"
    return 0.0, ""

def calc_support(prov, usage, tier="developer"):
    if tier == "basic":
        return 0.0
    elif tier == "developer":
        if prov == "AWS":
            return max(29.0, 0.03 * usage)  # Legacy Developer Support (discontinuing Jan 1, 2027)
        elif prov == "Azure":
            return 29.0                     # Flat $29/mo
        elif prov == "GCP":
            return max(29.0, 0.03 * usage)  # Standard Support: max($29, 3% of eligible spend)
    elif tier == "business":
        if prov == "AWS":
            return max(100.0, 0.10 * min(usage, 10000.0))  # Business Support+
        elif prov == "Azure":
            return 100.0                                    # Standard Support flat $100/mo
        elif prov == "GCP":
            return 500.0 + 0.03 * usage                     # Enhanced Support $500 + 3%
    return 0.0

# 1. Calculate Results across All Workloads and Support Tiers
rows = []
for sup_tier in ["developer", "basic", "business"]:
    for prov, d in DATA.items():
        for wl, sp in WORKLOADS.items():
            od = d["compute_ondemand_monthly_usd"].get(wl)
            ri = d["compute_1yr_monthly_usd"].get(wl)
            storage, storage_desc = compute_storage(prov, sp["storage_gb"])
            egress = egress_cost(d["egress_tiers"], sp["egress_gb"], FREE_EGRESS_GB[prov])
            
            usage_od = od + storage + egress
            usage_ri = ri + storage + egress
            support = calc_support(prov, usage_od, sup_tier)
            
            total_od = usage_od + support
            total_ri = usage_ri + support
            extras = storage + egress + support
            hidden_share = extras / total_od if total_od > 0 else 0
            
            exit_repatriation = egress_cost(d["egress_tiers"], sp["storage_gb"], FREE_EGRESS_GB[prov])
            exit_waiver = 0.0  # Eligible cloud-exit full account termination waiver
            
            rows.append({
                "support_tier": sup_tier,
                "workload": wl,
                "provider": prov,
                "compute_od": round(od, 2),
                "compute_1yr": round(ri, 2),
                "storage": round(storage, 2),
                "storage_desc": storage_desc,
                "egress": round(egress, 2),
                "support": round(support, 2),
                "total_od": round(total_od, 2),
                "total_1yr": round(total_ri, 2),
                "hidden_share_od": round(hidden_share, 4),
                "exit_repatriation": round(exit_repatriation, 2),
                "exit_waiver": round(exit_waiver, 2),
                "total_od_inr": round(total_od * USD_INR, 2),
                "total_1yr_inr": round(total_ri * USD_INR, 2),
                "exit_repatriation_inr": round(exit_repatriation * USD_INR, 2)
            })

df = pd.DataFrame(rows)
df.to_csv("results.csv", index=False)

# 2. Build Single Source of Truth Manifest for Frontend
manifest = {
    "meta": {
        "title": "Cloud Computing Pricing and Competition Manifest",
        "usd_inr": USD_INR,
        "fx_date": FX_DATE,
        "hours_per_month": HOURS_PER_MONTH,
        "updated_at": "2026-11-22"
    },
    "workloads": WORKLOADS,
    "providers": {
        "AWS": {
            "name": "Amazon Web Services",
            "region": "ap-south-1 (Mumbai)",
            "sku": {"A_Startup": "m5.large", "B_Midsize": "m5.2xlarge", "C_DataHeavy": "m5.4xlarge"},
            "od": DATA["AWS"]["compute_ondemand_monthly_usd"],
            "ri": DATA["AWS"]["compute_1yr_monthly_usd"],
            "storage": {
                "model": "linear_gb",
                "rate": DATA["AWS"]["storage_gb_month_usd"],
                "name": "EBS General Purpose SSD (gp3)"
            },
            "egress_tiers": DATA["AWS"]["egress_tiers"],
            "free_egress": FREE_EGRESS_GB["AWS"]
        },
        "Azure": {
            "name": "Microsoft Azure",
            "region": "centralindia (Pune)",
            "sku": {"A_Startup": "Standard_D2s_v5", "B_Midsize": "Standard_D8s_v5", "C_DataHeavy": "Standard_D16s_v5"},
            "od": DATA["Azure"]["compute_ondemand_monthly_usd"],
            "ri": DATA["Azure"]["compute_1yr_monthly_usd"],
            "storage": {
                "model": "provisioned_tier",
                "tiers": DATA["Azure"].get("storage_provisioned_tiers", []),
                "name": "Premium SSD Managed Disks (LRS)"
            },
            "egress_tiers": DATA["Azure"]["egress_tiers"],
            "free_egress": FREE_EGRESS_GB["Azure"]
        },
        "GCP": {
            "name": "Google Cloud Platform",
            "region": "asia-south1 (Mumbai)",
            "sku": {"A_Startup": "N2-standard-2 equiv", "B_Midsize": "N2-standard-8 equiv", "C_DataHeavy": "N2-standard-16 equiv"},
            "od": DATA["GCP"]["compute_ondemand_monthly_usd"],
            "ri": DATA["GCP"]["compute_1yr_monthly_usd"],
            "storage": {
                "model": "linear_gb",
                "rate": DATA["GCP"]["storage_gb_month_usd"],
                "name": "Balanced Persistent Disk (pd-balanced)"
            },
            "egress_tiers": DATA["GCP"]["egress_tiers"],
            "free_egress": FREE_EGRESS_GB["GCP"]
        }
    },
    "support_rules": {
        "basic": {"name": "Basic Support (Free, $0)", "formula": "0"},
        "developer": {"name": "Developer / Standard Support", "aws": "max($29, 3%)", "azure": "flat $29", "gcp": "max($29, 3%)"},
        "business": {"name": "Business Support+ / Production", "aws": "max($100, 10% first $10k)", "azure": "flat $100", "gcp": "$500 + 3%"}
    },
    "exit_policy": {
        "repatriation_metric": "Standard tiered internet egress on 100% of stored data (routine multi-cloud friction)",
        "waiver_metric": "$0.00 waiver for eligible permanent account termination and migration (2024 policy)",
        "eu_data_act": "Switching charges completely banned from Jan 12, 2027 in EU; Indian accounts rely on voluntary CSP commercial waivers."
    }
}

with open("pricing_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

# 3. Print Tabular Output for Primary Developer Support Baseline
pd.set_option("display.width", 220)
sub_dev = df[df["support_tier"] == "developer"]
for wl in WORKLOADS:
    sub = sub_dev[sub_dev["workload"] == wl].set_index("provider")
    print(f"\n=== {wl} [Developer Support Baseline] (USD/mo; INR @ {USD_INR} on {FX_DATE}) ===")
    print(sub[["compute_od", "compute_1yr", "storage", "storage_desc", "egress", "support", "total_od", "total_1yr",
               "hidden_share_od", "exit_repatriation", "exit_waiver"]].to_string())
    for col in ["total_od", "total_1yr"]:
        v = sub[col].astype(float)
        print(f"cheapest {col}: {v.idxmin()}  USD {v.min():.2f}  (INR {v.min() * USD_INR:,.0f})")

print("\nsaved results.csv")
print("saved pricing_manifest.json (Single Source of Truth)")