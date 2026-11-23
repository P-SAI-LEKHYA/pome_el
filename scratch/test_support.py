def calc_support(prov, usage, tier="developer"):
    if tier == "basic":
        return 0.0
    if tier == "developer":
        if prov == "AWS":
            return max(29.0, 0.03 * usage)  # Legacy Dev support (discontinuing Jan 1, 2027)
        elif prov == "Azure":
            return 29.0                     # Flat $29/mo
        elif prov == "GCP":
            return max(29.0, 0.03 * usage)  # max($29, 3%)
    elif tier == "business":
        if prov == "AWS":
            # Business Support+: max($100, 10% of first $10k)
            return max(100.0, 0.10 * min(usage, 10000.0))
        elif prov == "Azure":
            return 100.0                    # Standard Support flat $100/mo
        elif prov == "GCP":
            return 500.0 + 0.03 * usage     # Enhanced Support ($500 + 3%)
    return 0.0

print("=== SUPPORT PRICING TEST CASES ===")
usages = {"A_Startup": 85.0, "B_Midsize": 450.0, "C_DataHeavy": 1300.0}

print("\n--- Baseline Free Support ($0) ---")
for wl, u in usages.items():
    print(f"{wl} (Spend ${u}): AWS=$0.00, Azure=$0.00, GCP=$0.00")

print("\n--- Developer / Entry Support ---")
for wl, u in usages.items():
    s_aws = calc_support("AWS", u, "developer")
    s_az = calc_support("Azure", u, "developer")
    s_gcp = calc_support("GCP", u, "developer")
    print(f"{wl} (Spend ${u}): AWS=${s_aws:.2f}, Azure=${s_az:.2f}, GCP=${s_gcp:.2f}")

print("\n--- Business / Production Support ---")
for wl, u in usages.items():
    s_aws = calc_support("AWS", u, "business")
    s_az = calc_support("Azure", u, "business")
    s_gcp = calc_support("GCP", u, "business")
    print(f"{wl} (Spend ${u}): AWS=${s_aws:.2f}, Azure=${s_az:.2f}, GCP=${s_gcp:.2f}")
