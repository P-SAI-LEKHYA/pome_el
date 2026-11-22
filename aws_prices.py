import pandas as pd

FILE = "aws_ec2_mumbai.csv"  # already downloaded, no need to download again
TYPES = {"A_Startup": "m5.large", "B_Midsize": "m5.2xlarge", "C_DataHeavy": "m5.4xlarge"}
USD_INR = 83.0  # CHANGE to the current RBI reference rate and note the date

with open(FILE, encoding="utf-8") as f:
    header_row = next(i for i, line in enumerate(f) if line.startswith('"SKU"'))

cols = ["Instance Type", "vCPU", "Memory", "Operating System", "Tenancy", "Pre Installed S/W",
        "CapacityStatus", "License Model", "Product Family", "TermType",
        "PricePerUnit", "Unit", "Currency", "EffectiveDate"]

parts = []
for chunk in pd.read_csv(FILE, skiprows=header_row, usecols=cols, chunksize=200000,
                         dtype=str, keep_default_na=False):
    parts.append(chunk[chunk["Instance Type"].isin(TYPES.values())])

df = pd.concat(parts)
print("rows for the 3 instance types (all terms):", len(df))

steps = [
    ("TermType", "OnDemand"),
    ("Product Family", "Compute Instance"),
    ("Operating System", "Linux"),
    ("Tenancy", "Shared"),
    ("Pre Installed S/W", "NA"),
    ("CapacityStatus", "Used"),
    ("License Model", "No License required"),
]
for col, val in steps:
    df = df[df[col] == val]
    print(f"after {col} == {val!r}: {len(df)} rows")

df = df.copy()
inv = {v: k for k, v in TYPES.items()}
df["workload"] = df["Instance Type"].map(inv)
df["price_usd"] = df["PricePerUnit"].astype(float)
df["price_inr"] = df["price_usd"] * USD_INR
df["monthly_inr"] = df["price_inr"] * 730

print()
print(df[["workload", "Instance Type", "vCPU", "Memory", "price_usd", "Unit",
          "price_inr", "monthly_inr", "EffectiveDate"]].to_string())
df.to_csv("aws_prices.csv", index=False)