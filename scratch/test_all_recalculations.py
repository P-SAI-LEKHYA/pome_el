import json
import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Exchange rate and hours
USD_INR = 92.97
HOURS = 730

# Workload specs
WORKLOADS = {
    "A_Startup":   {"vcpu": 2,  "ram_gb": 8,  "storage_gb": 100,  "egress_gb": 100},
    "B_Midsize":   {"vcpu": 8,  "ram_gb": 32, "storage_gb": 1000, "egress_gb": 500},
    "C_DataHeavy": {"vcpu": 16, "ram_gb": 64, "storage_gb": 5000, "egress_gb": 2000},
}

# Azure disk tiers (Capacity in GiB, Price in USD/month)
AZURE_DISK_TIERS = [
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
    ("P70", 16384, 1802.06),
    ("P80", 32768, 3604.11),
]

def gb_to_gib(gb):
    return (gb * 1e9) / (2**30)

def azure_storage_single_disk(gb):
    gib = gb_to_gib(gb)
    for name, cap, price in AZURE_DISK_TIERS:
        if gib <= cap:
            return name, cap, price
    return "P80+", 32768, 3604.11

def azure_storage_multidisk(gb):
    gib = gb_to_gib(gb)
    for name, cap, price in AZURE_DISK_TIERS:
        if gib <= cap:
            return [(name, 1, price)], price
    disks = []
    tot = 0.0
    rem = gib
    p50_count = int(rem // 4096)
    if p50_count > 0:
        disks.append(("P50", p50_count, 495.5657 * p50_count))
        tot += 495.5657 * p50_count
        rem -= p50_count * 4096
    if rem > 0:
        for name, cap, price in AZURE_DISK_TIERS:
            if rem <= cap:
                disks.append((name, 1, price))
                tot += price
                break
    return disks, tot

# AWS Storage: EBS gp3 ($0.0912/GB-month)
def aws_storage_cost(gb):
    return gb * 0.0912

# GCP Storage: Balanced PD ($0.1200/GB-month)
def gcp_storage_cost(gb):
    return gb * 0.1200

# Egress calculation
def calc_tiered_egress(tiers, gb, free_gb=0):
    billable = max(0.0, gb - free_gb)
    cost = 0.0
    for start, end, price in tiers:
        if billable <= start:
            break
        upper = billable if end is None else min(billable, end)
        cost += (upper - start) * price
    return cost

AWS_EGRESS_TIERS = [
    [0.0, 10240.0, 0.1093],
    [10240.0, 51200.0, 0.085],
    [51200.0, 153600.0, 0.082],
    [153600.0, None, 0.08]
]
AWS_FREE_EGRESS = 100.0

AZURE_MGN_EGRESS_TIERS = [
    [0.0, 100.0, 0.000],
    [100.0, 10335.0, 0.120],
    [10335.0, 51295.0, 0.085],
    [51295.0, 153695.0, 0.082],
    [153695.0, 512095.0, 0.080],
    [512095.0, None, 0.080]
]
AZURE_FREE_EGRESS = 0.0

GCP_EGRESS_TIERS = [
    [0.0, 200.0, 0.000],
    [200.0, 10240.0, 0.110],
    [10240.0, 153600.0, 0.075],
    [153600.0, None, 0.070]
]
GCP_FREE_EGRESS = 0.0

# Compute costs (Verified from APIs)
COMPUTE = {
    "AWS": {
        "od": {"A_Startup": 73.73, "B_Midsize": 294.92, "C_DataHeavy": 589.84},
        "1yr": {"A_Startup": 46.72, "B_Midsize": 186.15, "C_DataHeavy": 371.57}
    },
    "Azure": {
        "od": {"A_Startup": 73.73, "B_Midsize": 294.92, "C_DataHeavy": 589.84},
        "1yr": {"A_Startup": 45.50, "B_Midsize": 182.00, "C_DataHeavy": 363.92}
    },
    "GCP": {
        "od": {"A_Startup": 85.15012, "B_Midsize": 340.60048, "C_DataHeavy": 681.20096},
        "1yr": {"A_Startup": 53.63748, "B_Midsize": 214.54992, "C_DataHeavy": 429.09984}
    }
}

# Support calculation function
def calc_support(prov, usage, tier="developer"):
    if tier == "basic":
        return 0.0
    if tier == "developer":
        if prov == "AWS":
            return max(29.0, 0.03 * usage)  # Legacy Dev support
        elif prov == "Azure":
            return 29.0                     # Flat $29
        elif prov == "GCP":
            return max(29.0, 0.03 * usage)  # max($29, 3%)
    elif tier == "business":
        if prov == "AWS":
            return max(100.0, 0.10 * min(usage, 10000.0))
        elif prov == "Azure":
            return 100.0
        elif prov == "GCP":
            return 500.0 + 0.03 * usage
    return 0.0

print("=== RECALCULATING ALL WORKLOADS (Single Disk Architecture) ===")
for support_tier in ["basic", "developer", "business"]:
    print(f"\n==================== SUPPORT TIER: {support_tier.upper()} ====================")
    for wl, sp in WORKLOADS.items():
        print(f"\n--- {wl} (Storage: {sp['storage_gb']} GB, Egress: {sp['egress_gb']} GB) ---")
        for prov in ["AWS", "Azure", "GCP"]:
            od_comp = COMPUTE[prov]["od"][wl]
            ri_comp = COMPUTE[prov]["1yr"][wl]
            
            # Storage
            if prov == "AWS":
                storage = aws_storage_cost(sp["storage_gb"])
                egress = calc_tiered_egress(AWS_EGRESS_TIERS, sp["egress_gb"], AWS_FREE_EGRESS)
                exit_toll_rep = calc_tiered_egress(AWS_EGRESS_TIERS, sp["storage_gb"], AWS_FREE_EGRESS)
            elif prov == "Azure":
                t_name, t_cap, storage = azure_storage_single_disk(sp["storage_gb"])
                egress = calc_tiered_egress(AZURE_MGN_EGRESS_TIERS, sp["egress_gb"], AZURE_FREE_EGRESS)
                exit_toll_rep = calc_tiered_egress(AZURE_MGN_EGRESS_TIERS, sp["storage_gb"], AZURE_FREE_EGRESS)
            elif prov == "GCP":
                storage = gcp_storage_cost(sp["storage_gb"])
                egress = calc_tiered_egress(GCP_EGRESS_TIERS, sp["egress_gb"], GCP_FREE_EGRESS)
                exit_toll_rep = calc_tiered_egress(GCP_EGRESS_TIERS, sp["storage_gb"], GCP_FREE_EGRESS)
            
            usage_od = od_comp + storage + egress
            usage_ri = ri_comp + storage + egress
            
            support = calc_support(prov, usage_od, support_tier)
            total_od = usage_od + support
            total_ri = usage_ri + support
            
            hidden_pct = ((storage + egress + support) / total_od) * 100
            
            print(f"{prov:<6}: OD_Comp=${od_comp:.2f} | Stor=${storage:.2f} | Egr=${egress:.2f} | Sup=${support:.2f} | TotOD=${total_od:.2f} (INR {total_od*USD_INR:,.0f}) | Tot1Yr=${total_ri:.2f} (INR {total_ri*USD_INR:,.0f}) | Hidden={hidden_pct:.1f}% | ExitToll=${exit_toll_rep:.2f}")

print("\n\n=== MULTI-DISK COMPARISON FOR WORKLOAD C (Azure P50+P30 = 5120 GiB = $630.74) ===")
for support_tier in ["basic", "developer"]:
    sp = WORKLOADS["C_DataHeavy"]
    od_comp = COMPUTE["Azure"]["od"]["C_DataHeavy"]
    ri_comp = COMPUTE["Azure"]["1yr"]["C_DataHeavy"]
    disks, storage = azure_storage_multidisk(sp["storage_gb"])
    egress = calc_tiered_egress(AZURE_MGN_EGRESS_TIERS, sp["egress_gb"], AZURE_FREE_EGRESS)
    usage_od = od_comp + storage + egress
    usage_ri = ri_comp + storage + egress
    support = calc_support("Azure", usage_od, support_tier)
    tot_od = usage_od + support
    tot_ri = usage_ri + support
    hidden_pct = ((storage + egress + support) / tot_od) * 100
    print(f"Azure Multi-disk ({support_tier}): Storage=${storage:.2f} | TotOD=${tot_od:.2f} (INR {tot_od*USD_INR:,.0f}) | Tot1Yr=${tot_ri:.2f} | Hidden={hidden_pct:.1f}%")
