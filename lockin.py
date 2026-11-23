import random

# Score 1-5, where 5 = hardest to leave. YOU fill these in, each with evidence from provider documentation.
CRITERIA = {"egress_fees": 0.25, "proprietary_services": 0.25, "commitment_terms": 0.15,
            "bundling": 0.20, "migration_tools": 0.15}   # weights sum to 1; justify them in your report
PROVIDERS = ["AWS", "Azure", "GCP"]

SCORES = {
    "AWS": {
        "egress_fees": 4,          # High tier at $0.1093/GB beyond 100GB free tier; historically highest punitive exit toll
        "proprietary_services": 5, # Massive proprietary PaaS/DB lock-in (DynamoDB, Aurora, Lambda APIs, CloudFormation)
        "commitment_terms": 4,     # Rigid Standard RI family constraints and 1-3 yr contractual hourly spend in Savings Plans
        "bundling": 3,             # Strong startup Activate credits & Marketplace, but lacks enterprise desktop/productivity suite
        "migration_tools": 3,      # Frictionless inbound tools (DMS, Snowball) but limited automated outbound repatriation support
    },
    "Azure": {
        "egress_fees": 4,          # $0.12/GB standard MGN egress beyond 100GB; high egress penalty for non-Microsoft clouds
        "proprietary_services": 5, # Deep integration with Windows Server, Active Directory/Entra ID, Microsoft 365, Cosmos DB
        "commitment_terms": 4,     # 1-yr and 3-yr RIs with strict annual cancellation penalties (up to 12% fee cap)
        "bundling": 5,             # Unrivalled Enterprise Agreement (EA) bundling (M365 + Azure) & Azure Hybrid Benefit licensing
        "migration_tools": 4,      # Aggressive hypervisor-to-cloud migration (Azure Migrate), difficult cross-cloud schema export
    },
    "GCP": {
        "egress_fees": 3,          # Standard tier egress at $0.11/GB with 200GB free; first major CSP to waive exit fees for switching
        "proprietary_services": 3, # Emphasizes open-source standards (Kubernetes/GKE, ANSI SQL in BigQuery, TensorFlow, Postgres)
        "commitment_terms": 2,     # Flexible vCPU/RAM resource-based CUDs across machine types; automated Sustained Use Discounts
        "bundling": 3,             # Google Workspace integration, but significantly lower enterprise licensing leverage than Microsoft
        "migration_tools": 2,      # Multi-cloud oriented: Google Distributed Cloud/Anthos, BigQuery Omni querying AWS S3 & Azure Blob
    }
}

EVIDENCE = {
    ("AWS", "egress_fees"): "AWS charges $0.1093/GB beyond 100GB/mo free from Mumbai ap-south-1. Egress is waived only for full account terminations (voluntary policy in India; EU Data Act bans switching fees from Jan 12, 2027).",
    ("AWS", "proprietary_services"): "AWS DynamoDB API and IAM are tightly coupled to AWS runtime; non-standard API endpoints.",
    ("AWS", "commitment_terms"): "AWS 1-yr Standard Reserved Instances cannot be converted to other instance families without convertible penalty.",
    ("AWS", "bundling"): "AWS relies on AWS Activate credits ($100k) and partner network, but has no office productivity/OS bundling.",
    ("AWS", "migration_tools"): "AWS Database Migration Service (DMS) supports homogeneous/heterogeneous inbound migrations to AWS.",
    ("Azure", "egress_fees"): "Azure quotes $0.120/GB for Central India standard MGN egress after 100GB free tier. Offers $0 exit waiver for eligible account closures within 60 days.",
    ("Azure", "proprietary_services"): "Enterprise identity tightly tied to Microsoft Entra ID (formerly Azure AD) and Windows ecosystem.",
    ("Azure", "commitment_terms"): "Microsoft Azure reservation exchanges are subject to annual cancellation quotas and exchange restrictions.",
    ("Azure", "bundling"): "Azure Hybrid Benefit allows re-using Windows Server and SQL Server on-premise licenses to save up to 40-80%.",
    ("Azure", "migration_tools"): "Azure Migrate provides comprehensive discovery and lift-and-shift for VMware/Hyper-V into Azure.",
    ("GCP", "egress_fees"): "GCP Standard tier egress is $0.11/GB with 200GB/mo free; Google was first to eliminate exit fees for switching (requires full account termination ticket).",
    ("GCP", "proprietary_services"): "Kubernetes (GKE) and managed open-source engines allow easier application portability across clouds.",
    ("GCP", "commitment_terms"): "GCP Committed Use Discounts (CUDs) decouple vCPU and RAM commitments from specific machine instance types.",
    ("GCP", "bundling"): "Bundles with Google Workspace and BigQuery data analytics, but lacks dominant enterprise ERP/OS licensing.",
    ("GCP", "migration_tools"): "Anthos and BigQuery Omni enable cross-cloud data processing without moving data from AWS S3 or Azure Blob.",
}

missing = [(p, c) for p in PROVIDERS for c in CRITERIA if SCORES[p][c] is None]
if missing:
    print("Fill these scores first (1-5, 5 = hardest to leave):")
    for m in missing:
        print("  ", m)
    raise SystemExit

def index(p, w):
    return sum(SCORES[p][c] * w[c] for c in w) / sum(w.values())

print("Lock-in index (higher = harder to leave):")
for p in PROVIDERS:
    print(f"  {p}: {index(p, CRITERIA):.2f}")

equal = {c: 1 for c in CRITERIA}
print("\nEqual weights:", {p: round(index(p, equal), 2) for p in PROVIDERS})

print("\nDrop one criterion at a time:")
for drop in CRITERIA:
    w = {c: v for c, v in CRITERIA.items() if c != drop}
    print(f"  without {drop}:", {p: round(index(p, w), 2) for p in PROVIDERS})

wins = {p: 0 for p in PROVIDERS}
for _ in range(5000):
    w = {c: random.random() for c in CRITERIA}
    wins[max(PROVIDERS, key=lambda p: index(p, w))] += 1
print("\nShare of 5000 random weightings where each provider has the HIGHEST lock-in:")
for p in PROVIDERS:
    print(f"  {p}: {wins[p] / 50:.1f}%")