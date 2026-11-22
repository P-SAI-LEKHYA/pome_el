import os, json, requests, pandas as pd
from config import AWS_TYPES, HOURS_PER_MONTH

EC2_FILE = "aws_ec2_mumbai.csv"   # already downloaded earlier
DT_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/ap-south-1/index.csv"
DT_FILE = "aws_datatransfer_mumbai.csv"

def header_row(path):
    with open(path, encoding="utf-8") as f:
        return next(i for i, line in enumerate(f) if line.startswith('"SKU"'))

def download(url, path):
    if os.path.exists(path):
        return True
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for c in r.iter_content(1024 * 1024):
                    f.write(c)
        return True
    except Exception as e:
        print("Download failed:", e)
        if os.path.exists(path):
            os.remove(path)
        return False

inv = {v: k for k, v in AWS_TYPES.items()}
out = {"compute_ondemand_monthly_usd": {}, "compute_1yr_monthly_usd": {},
       "storage_gb_month_usd": None, "egress_tiers": []}

cols = ["Instance Type", "Operating System", "Tenancy", "Pre Installed S/W", "CapacityStatus",
        "License Model", "Product Family", "TermType", "PricePerUnit", "Unit", "LeaseContractLength",
        "PurchaseOption", "OfferingClass", "Volume API Name", "usageType", "EffectiveDate"]
parts = []
for ch in pd.read_csv(EC2_FILE, skiprows=header_row(EC2_FILE), usecols=cols, chunksize=200000,
                      dtype=str, keep_default_na=False):
    is_vm = ch["Instance Type"].isin(AWS_TYPES.values())
    is_gp3 = (ch["Product Family"] == "Storage") & (ch["Volume API Name"] == "gp3")
    parts.append(ch[is_vm | is_gp3])
df = pd.concat(parts)

# compute: Linux, shared, no licence, hourly
vm = df[(df["Product Family"] == "Compute Instance") & (df["Operating System"] == "Linux") &
        (df["Tenancy"] == "Shared") & (df["Pre Installed S/W"] == "NA") &
        (df["CapacityStatus"] == "Used") & (df["License Model"] == "No License required") &
        (df["Unit"] == "Hrs")]
od = vm[vm["TermType"] == "OnDemand"]
ri = vm[(vm["TermType"] == "Reserved") & (vm["LeaseContractLength"] == "1yr") &
        (vm["PurchaseOption"] == "No Upfront") & (vm["OfferingClass"] == "standard")]
print("on-demand rows:", len(od), "| 1-year reserved rows:", len(ri), "(expect 3 each)")
for _, r in od.iterrows():
    out["compute_ondemand_monthly_usd"][inv[r["Instance Type"]]] = float(r["PricePerUnit"]) * HOURS_PER_MONTH
for _, r in ri.iterrows():
    out["compute_1yr_monthly_usd"][inv[r["Instance Type"]]] = float(r["PricePerUnit"]) * HOURS_PER_MONTH

# storage: gp3 per GB-month
st = df[(df["Product Family"] == "Storage") & (df["Volume API Name"] == "gp3") &
        (df["TermType"] == "OnDemand") & (df["Unit"] == "GB-Mo")]
print(st[["usageType", "PricePerUnit", "Unit", "EffectiveDate"]].to_string())
if len(st) >= 1:
    out["storage_gb_month_usd"] = float(st.iloc[0]["PricePerUnit"])
    if len(st) > 1:
        print("WARNING: more than one gp3 row, check the printout above")

# outbound data transfer to internet from Mumbai (tiered)
if download(DT_URL, DT_FILE):
    hr = header_row(DT_FILE)
    dt = pd.read_csv(DT_FILE, skiprows=hr, dtype=str, keep_default_na=False)
    if "usageType" in dt.columns:
        t = dt[(dt["usageType"] == "APS3-DataTransfer-Out-Bytes") & (dt["TermType"] == "OnDemand")]
        t = t.assign(s=t["StartingRange"].astype(float)).sort_values("s")
        print(t[["usageType", "StartingRange", "EndingRange", "PricePerUnit", "Unit"]].to_string())
        for _, r in t.iterrows():
            end = None if r["EndingRange"] in ("Inf", "") else float(r["EndingRange"])
            out["egress_tiers"].append([float(r["StartingRange"]), end, float(r["PricePerUnit"])])
        if t.empty:
            print("No rows for APS3-DataTransfer-Out-Bytes. Usage types containing 'Out':")
            print(sorted(dt[dt["usageType"].str.contains("Out")]["usageType"].unique())[:40])
    else:
        print("usageType column not found. Columns:", list(dt.columns))

with open("aws_extra.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nsaved aws_extra.json")