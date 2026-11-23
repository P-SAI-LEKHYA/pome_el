# ---------- shared settings: edit only this file ----------
USD_INR = 92.97           # Current FBIL/RBI reference rate (92.9699)
FX_DATE = "20-11-2026"    # Date of that rate (DD-MM-2026)
HOURS_PER_MONTH = 730

WORKLOADS = {
    "A_Startup":   {"vcpu": 2,  "ram_gb": 8,  "storage_gb": 100,  "egress_gb": 100},
    "B_Midsize":   {"vcpu": 8,  "ram_gb": 32, "storage_gb": 1000, "egress_gb": 500},
    "C_DataHeavy": {"vcpu": 16, "ram_gb": 64, "storage_gb": 5000, "egress_gb": 2000},
}

AWS_TYPES = {"A_Startup": "m5.large", "B_Midsize": "m5.2xlarge", "C_DataHeavy": "m5.4xlarge"}
AZURE_SKUS = {"A_Startup": "Standard_D2s_v5", "B_Midsize": "Standard_D8s_v5", "C_DataHeavy": "Standard_D16s_v5"}
AZURE_REGION = "centralindia"
GCP_SERVICE_ID = "6F81-5844-456A"   # Compute Engine

# Overrides: fill ONLY if a script tells you it could not decide
AZURE_EGRESS_METER = "Standard Data Transfer Out"        # exact meterName from azure_bandwidth_candidates.csv
GCP_EGRESS_DESCRIPTION = None                            # exact description from gcp_egress_candidates.csv (default uses Standard tier)

# Support plan scenarios: "basic" (Free, $0/mo), "developer" (AWS max($29, 3%), Azure $29, GCP max($29, 3%)),
# or "business" (AWS Business Support+ max($100, 10%), Azure Standard $100, GCP Enhanced $500 + 3%).
# Note: AWS legacy Developer Support sunsets on January 1, 2027.
DEFAULT_SUPPORT_TIER = "developer"

# Baseline monthly support fees in USD (overridden by dynamic formulas in calculator.py)
SUPPORT_MONTHLY_USD = {"AWS": 29.0, "Azure": 29.0, "GCP": 29.0}

# Free monthly egress in GB.
# AWS provides 100 GB/mo free (not reflected in CSV starting at 0 GB). 
# Azure MGN & GCP already include 100 GB and 200 GB @ $0 in their rate tiers.
FREE_EGRESS_GB = {"AWS": 100, "Azure": 0, "GCP": 0}

# Cloud Exit Waiver Conditions (2024 Policy Updates):
# AWS, Azure, and GCP waive data egress fees when a customer permanently terminates their account 
# and migrates 100% of data within 60 days (advance support ticket required).
# Under EU Data Act (Regulation 2023/2854), all switching charges are prohibited from Jan 12, 2027.
# For Indian accounts, waivers operate under voluntary global commercial policies, not statutory mandate.