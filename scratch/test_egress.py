def calc_egress(tiers, gb):
    cost = 0.0
    for start, end, price in tiers:
        if gb <= start:
            break
        upper = gb if end is None else min(gb, end)
        cost += (upper - start) * price
    return cost

mgn_tiers = [
    [0.0, 100.0, 0.000],
    [100.0, 10335.0, 0.120],
    [10335.0, 51295.0, 0.085],
    [51295.0, 153695.0, 0.082],
    [153695.0, 512095.0, 0.080],
    [512095.0, None, 0.080]
]

internet_tiers = [
    [0.0, 100.0, 0.000],
    [100.0, 10100.0, 0.110],
    [10100.0, 50100.0, 0.075],
    [50100.0, 150100.0, 0.070],
    [150100.0, None, 0.060]
]

print("=== AZURE EGRESS TEST CASES ===")
for gb in [100, 500, 2000]:
    c_mgn = calc_egress(mgn_tiers, gb)
    c_int = calc_egress(internet_tiers, gb)
    print(f"Egress {gb} GB:")
    print(f"  MGN (Microsoft Global Network - Default): ${c_mgn:.2f}")
    print(f"  Internet (Routing Preference Transit ISP): ${c_int:.2f}")
