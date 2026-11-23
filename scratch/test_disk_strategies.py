# Inspect disk selection strategies

AZURE_TIERS = [
    # (tier_name, capacity_gib, price_usd)
    ("P1", 4, 0.84),
    ("P2", 8, 1.68),
    ("P3", 16, 3.36),
    ("P4", 32, 5.2795),
    ("P6", 64, 10.207),
    ("P10", 128, 19.71),
    ("P15", 256, 38.0121),
    ("P20", 512, 73.22),
    ("P30", 1024, 135.17),
    ("P40", 2048, 259.0457),
    ("P50", 4096, 495.5657),
    ("P60", 8192, 946.08),
]

def gb_to_gib(gb):
    # 1 GB = 10^9 bytes; 1 GiB = 2^30 bytes = 1,073,741,824 bytes
    return (gb * 1e9) / (2**30)

print(f"100 GB = {gb_to_gib(100):.2f} GiB")
print(f"1000 GB = {gb_to_gib(1000):.2f} GiB")
print(f"5000 GB = {gb_to_gib(5000):.2f} GiB")

# Strategy A: Single disk next-fit up to P60
def single_disk_cost(gb):
    gib = gb_to_gib(gb)
    for name, cap, price in AZURE_TIERS:
        if gib <= cap:
            return name, cap, price
    return "P60+", 8192, 946.08

# Strategy B: Greedy multi-disk combination (e.g. 1x P50 + 1x P30 = 5120 GiB)
def composite_disk_cost(gb):
    gib = gb_to_gib(gb)
    # If it fits in a single tier <= P50:
    for name, cap, price in AZURE_TIERS:
        if gib <= cap:
            return [(name, 1, price)], price
    # If above 4096 GiB (P50), compose using largest available disks
    # e.g., for 4656 GiB: 1x P50 (4096) + remaining (560 GiB -> 1x P30 1024 GiB)
    rem = gib
    disks = []
    total_price = 0
    # Can use P50s for each 4096 chunk
    p50_count = int(rem // 4096)
    if p50_count > 0:
        disks.append(("P50", p50_count, 495.5657 * p50_count))
        total_price += 495.5657 * p50_count
        rem -= p50_count * 4096
    
    if rem > 0:
        for name, cap, price in AZURE_TIERS:
            if rem <= cap:
                disks.append((name, 1, price))
                total_price += price
                break
    return disks, total_price

print("\n--- Strategy A (Single Disk) ---")
for gb in [100, 1000, 5000]:
    d = single_disk_cost(gb)
    print(f"{gb} GB: {d[0]} ({d[1]} GiB) = ${d[2]:.2f}")

print("\n--- Strategy B (Composite Disk above 4 TiB) ---")
for gb in [100, 1000, 5000]:
    disks, p = composite_disk_cost(gb)
    disk_str = " + ".join([f"{c}x {n}" for n, c, _ in disks])
    print(f"{gb} GB: {disk_str} = ${p:.2f}")
