import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from math import pi

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIRS = ['paper_figures', '../paper_figures']
for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

# Styling
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.color'] = '#222222'
plt.rcParams['ytick.color'] = '#222222'
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 8.5
plt.rcParams['figure.titlesize'] = 11

C_AWS = '#E67E22'     # Warm Amber / Orange
C_AZURE = '#1B6CA8'   # Azure Blue
C_GCP = '#2E8540'     # Forest Green

C_COMPUTE = '#1B6CA8'
C_STORAGE = '#E67E22'
C_EGRESS = '#8E44AD'
C_SUPPORT = '#C0392B'

def save_fig(fig, base_name):
    for d in OUTPUT_DIRS:
        fig.savefig(os.path.join(d, f"{base_name}.png"), dpi=300, bbox_inches='tight')
        fig.savefig(os.path.join(d, f"{base_name}.pdf"), bbox_inches='tight')
        fig.savefig(os.path.join(d, f"{base_name}.svg"), bbox_inches='tight')
    plt.close(fig)
    print(f"Generated {base_name} (.png, .pdf, .svg)")

# -------------------------------------------------------------
# FIGURE 1: Overall System Workflow
# -------------------------------------------------------------
def generate_fig01():
    fig = plt.figure(figsize=(7.2, 4.8), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_box(x, y, w, h, title, lines, bg_color='#F8F9FA', edge_color='#2C3E50', title_color='#2C3E50'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.5",
                                     facecolor=bg_color, edgecolor=edge_color, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 2.8, title, ha='center', va='top', fontsize=8.5, fontweight='bold', color=title_color)
        curr_y = y + h - 6.0
        for line in lines:
            ax.text(x + w/2, curr_y, line, ha='center', va='top', fontsize=7.0, color='#333333')
            curr_y -= 3.0

    def draw_arrow(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color='#2C3E50', lw=1.2, mutation_scale=10))
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.2, label, ha='center', va='bottom', fontsize=6.5, color='#555555',
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8))

    # Stage 1: Data Collection (Top Left)
    draw_box(2, 68, 28, 28, "1. Pricing Data Ingestion", [
        "AWS Price List API (ap-south-1)",
        "Azure Retail Prices API (centralindia)",
        "GCP Cloud Billing Catalog (asia-south1)",
        "RBI FX Reference: ₹92.97 / USD"
    ], bg_color='#EBF5FB', edge_color='#1B6CA8', title_color='#1B6CA8')

    # Stage 2: Data Normalization (Top Right)
    draw_box(36, 68, 28, 28, "2. Processing & Normalization", [
        "azure_extra.py: 14 Disk Tiers (P1-P80)",
        "Disentangle MGN vs Transit Egress",
        "aws_extra.py & gcp_extra.py",
        "Unified Format: pricing_manifest.json"
    ], bg_color='#FEF9E7', edge_color='#D4AC0D', title_color='#B7950B')

    # Workload Definitions (Right Top)
    draw_box(70, 68, 28, 28, "3. Workload Archetypes", [
        "Startup: 2 vCPU, 8 GB, 100 GB, 100 GB",
        "Midsize: 8 vCPU, 32 GB, 1 TB, 500 GB",
        "Data-Heavy: 16 vCPU, 64 GB, 5 TB, 2 TB",
        "Standard: 730 Hours / Month"
    ], bg_color='#EAFAF1', edge_color='#2E8540', title_color='#2E8540')

    # Stage 4: Calculation Engine (Middle Center)
    draw_box(22, 34, 56, 26, "4. Python Core Calculation Engine (calculator.py)", [
        "Compute: On-Demand & 1-Year Commitments (Savings Plans, RIs, CUDs)",
        "Storage: AWS gp3 (Linear) vs Azure Premium SSD (Provisioned) vs GCP Balanced PD",
        "Network Egress: Provider Free Allowances & Tiered Data Transfer Out Schedules",
        "Support: AWS max($29, 3%), Azure Flat $29, GCP max($29, 3%) [Dev Baseline]"
    ], bg_color='#F4ECF7', edge_color='#8E44AD', title_color='#8E44AD')

    # Stage 5: Analytical Models (Bottom Left & Center)
    draw_box(2, 2, 44, 25, "5. Lock-in Engine (lockin.py)", [
        "5 Criteria: Egress, PaaS, Commit, Bundle, Tooling",
        "Monte Carlo: 5,000 Dirichlet Weight Simulations",
        "Pareto Stability Analysis across Providers"
    ], bg_color='#FDEDEC', edge_color='#C0392B', title_color='#C0392B')

    # Stage 6: Outputs & Dashboards (Bottom Right)
    draw_box(54, 2, 44, 25, "6. Outputs & Interactive Dashboard", [
        "Empirical Results Matrix (results.csv)",
        "Interactive Cockpit (index.html / port 8080)",
        "Porter's Five Forces & Oligopoly Analysis",
        "IEEE Publication Figures & Verification"
    ], bg_color='#E8F8F5', edge_color='#16A085', title_color='#16A085')

    # Arrows
    draw_arrow(30, 82, 36, 82)
    draw_arrow(64, 82, 70, 82)
    draw_arrow(50, 68, 50, 60)
    draw_arrow(84, 68, 70, 60)
    draw_arrow(36, 34, 24, 27)
    draw_arrow(64, 34, 76, 27)
    draw_arrow(46, 14, 54, 14, "Integration")

    save_fig(fig, 'fig01_system_workflow')

# -------------------------------------------------------------
# FIGURE 2: Monthly Cloud Cost Comparison
# -------------------------------------------------------------
def generate_fig02():
    workloads = ['Startup\n(2 vCPU, 8 GB)', 'Midsize\n(8 vCPU, 32 GB)', 'Data-Heavy\n(16 vCPU, 64 GB)']
    aws_costs = [111.85, 458.84, 1291.12]
    azure_costs = [122.44, 507.09, 1792.92] # single P60
    azure_multi = [122.44, 507.09, 1477.58] # multi-disk note
    gcp_costs = [126.15, 522.60, 1523.58]

    x = np.arange(len(workloads))
    width = 0.24

    fig, ax = plt.subplots(figsize=(6.8, 4.0), dpi=300)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    rects1 = ax.bar(x - width, aws_costs, width, label='AWS (Mumbai ap-south-1)', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    rects2 = ax.bar(x, azure_costs, width, label='Azure (Central India)', color=C_AZURE, edgecolor='#333333', lw=0.7, zorder=3)
    rects3 = ax.bar(x + width, gcp_costs, width, label='GCP (Mumbai asia-south1)', color=C_GCP, edgecolor='#333333', lw=0.7, zorder=3)

    # Marker for Azure multi-disk in Workload C
    ax.scatter([x[2]], [azure_multi[2]], color='#D9E1F2', edgecolor=C_AZURE, s=55, zorder=4, marker='D')
    ax.annotate('Multi-Disk P50+P30:\n$1,477.58 (₹137.4k)', xy=(x[2], azure_multi[2]), xytext=(x[2]-0.32, 1380),
                arrowprops=dict(arrowstyle="->", color=C_AZURE, lw=0.8), fontsize=6.8, color=C_AZURE, fontweight='bold')

    ax.set_ylabel('Total Monthly On-Demand Cost (USD $)')
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontweight='bold')
    ax.set_ylim(0, 2050)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

    # Secondary axis for INR
    ax2 = ax.twinx()
    ax2.set_ylim(0, 2050 * 92.97)
    ax2.set_ylabel('Equivalent Monthly Expenditure (INR ₹, Rate: ₹92.97 / USD)')
    ax2.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda val, p: f"₹{int(val/1000):d}k"))

    # Add direct numerical labels
    def autolabel(rects, vals):
        for rect, val in zip(rects, vals):
            h = rect.get_height()
            inr = val * 92.97
            inr_str = f"₹{inr/1000:.1f}k" if inr >= 10000 else f"₹{int(inr)}"
            ax.annotate(f"${val:.2f}\n({inr_str})",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=6.8, color='#222222')

    autolabel(rects1, aws_costs)
    autolabel(rects2, azure_costs)
    autolabel(rects3, gcp_costs)

    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    save_fig(fig, 'fig02_monthly_cost_comparison')

# -------------------------------------------------------------
# FIGURE 3: Cost Composition Analysis (Stacked Bar)
# -------------------------------------------------------------
def generate_fig03():
    labels = [
        'AWS\nStartup', 'Azure\nStartup', 'GCP\nStartup',
        'AWS\nMidsize', 'Azure\nMidsize', 'GCP\nMidsize',
        'AWS\nDataHvy', 'Azure\nDataHvy', 'GCP\nDataHvy'
    ]

    compute = [73.73, 73.73, 85.15, 294.92, 294.92, 340.60, 589.84, 589.84, 681.20]
    storage = [9.12, 19.71, 12.00, 91.20, 135.17, 120.00, 456.00, 946.08, 600.00]
    egress =  [0.00, 0.00, 0.00, 43.72, 48.00, 33.00, 207.67, 228.00, 198.00]
    support = [29.00, 29.00, 29.00, 29.00, 29.00, 29.00, 37.61, 29.00, 44.38]

    x = np.arange(len(labels))
    width = 0.65

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=300)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    p1 = ax.bar(x, compute, width, label='Compute (On-Demand)', color=C_COMPUTE, edgecolor='#333333', lw=0.6, zorder=3)
    p2 = ax.bar(x, storage, width, bottom=compute, label='Storage (gp3 / Premium SSD / pd-bal)', color=C_STORAGE, edgecolor='#333333', lw=0.6, zorder=3)
    bot2 = [c + s for c, s in zip(compute, storage)]
    p3 = ax.bar(x, egress, width, bottom=bot2, label='Egress (Internet Data Transfer)', color=C_EGRESS, edgecolor='#333333', lw=0.6, zorder=3)
    bot3 = [b + e for b, e in zip(bot2, egress)]
    p4 = ax.bar(x, support, width, bottom=bot3, label='Developer Support (Baseline)', color=C_SUPPORT, edgecolor='#333333', lw=0.6, zorder=3)

    # Workload group separators
    ax.axvline(2.5, color='#888888', linestyle=':', lw=1.0)
    ax.axvline(5.5, color='#888888', linestyle=':', lw=1.0)

    ax.text(1.0, 1850, "Startup Workload", ha='center', fontsize=8.5, fontweight='bold', color='#444444')
    ax.text(4.0, 1850, "Midsize Workload", ha='center', fontsize=8.5, fontweight='bold', color='#444444')
    ax.text(7.0, 1850, "Data-Heavy Workload", ha='center', fontsize=8.5, fontweight='bold', color='#444444')

    ax.set_ylabel('Monthly Expenditure (USD $)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylim(0, 1950)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left', ncol=2)

    # Annotate total on top
    totals = [c + s + e + sup for c, s, e, sup in zip(compute, storage, egress, support)]
    for i, tot in enumerate(totals):
        ax.text(x[i], tot + 25, f"${tot:.1f}", ha='center', va='bottom', fontsize=6.8, fontweight='bold', color='#222222')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    save_fig(fig, 'fig03_cost_composition')

# -------------------------------------------------------------
# FIGURE 4: Hidden Cost Percentage
# -------------------------------------------------------------
def generate_fig04():
    workloads = ['Startup\n(100 GB Disk, 100 GB Egress)', 'Midsize\n(1 TB Disk, 500 GB Egress)', 'Data-Heavy\n(5 TB Disk, 2 TB Egress)']
    aws_hidden = [34.08, 35.72, 54.32]
    azure_hidden = [39.78, 41.84, 67.10]
    gcp_hidden = [32.50, 34.83, 55.29]

    x = np.arange(len(workloads))
    width = 0.24

    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=300)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    rects1 = ax.bar(x - width, aws_hidden, width, label='AWS (Mumbai)', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    rects2 = ax.bar(x, azure_hidden, width, label='Azure (Central India)', color=C_AZURE, edgecolor='#333333', lw=0.7, zorder=3)
    rects3 = ax.bar(x + width, gcp_hidden, width, label='GCP (Mumbai)', color=C_GCP, edgecolor='#333333', lw=0.7, zorder=3)

    ax.axhline(50.0, color='#C0392B', linestyle='--', lw=1.2, zorder=4, label='50% Cost Parity Threshold')
    ax.text(2.35, 51.5, "Non-Compute Exceeds Compute (>50%)", color='#C0392B', fontsize=7.2, fontweight='bold', ha='right')

    ax.set_ylabel('Non-Compute Hidden Cost Share (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontweight='bold')
    ax.set_ylim(0, 80)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

    def autolabel_pct(rects):
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=7.2, fontweight='bold')

    autolabel_pct(rects1)
    autolabel_pct(rects2)
    autolabel_pct(rects3)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    save_fig(fig, 'fig04_hidden_cost_share')

# -------------------------------------------------------------
# FIGURE 5: On-Demand versus One-Year Commitment
# -------------------------------------------------------------
def generate_fig05():
    workloads = ['Startup', 'Midsize', 'Data-Heavy']
    
    # Costs
    aws_od = [111.85, 458.84, 1291.12]
    aws_ri = [84.84, 350.07, 1072.85]
    
    az_od = [122.44, 507.09, 1792.92]
    az_ri = [94.21, 394.17, 1567.00]
    
    gcp_od = [126.15, 522.60, 1523.58]
    gcp_ri = [94.64, 396.55, 1271.48]

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.8), dpi=300, sharey=False)

    for i, (ax, wl) in enumerate(zip(axes, workloads)):
        x = np.arange(3)
        w = 0.35
        
        od_vals = [aws_od[i], az_od[i], gcp_od[i]]
        ri_vals = [aws_ri[i], az_ri[i], gcp_ri[i]]
        savings = [(1 - r/o)*100 for o, r in zip(od_vals, ri_vals)]
        
        ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
        
        bars1 = ax.bar(x - w/2, od_vals, w, label='On-Demand', color=['#F39C12', '#2980B9', '#27AE60'], edgecolor='#333333', lw=0.7, zorder=3)
        bars2 = ax.bar(x + w/2, ri_vals, w, label='1-Year Commit', color=['#FAD7A0', '#A9CCE3', '#A9DFBF'], edgecolor='#333333', lw=0.7, hatch='//', zorder=3)
        
        ax.set_title(f"{wl} Profile", fontsize=9.5, fontweight='bold', pad=8)
        ax.set_xticks(x)
        ax.set_xticklabels(['AWS', 'Azure', 'GCP'], fontsize=8.5, fontweight='bold')
        
        for idx, (b1, b2, s) in enumerate(zip(bars1, bars2, savings)):
            h2 = b2.get_height()
            ax.text(b2.get_x() + b2.get_width()/2, h2 + (od_vals[idx]*0.02), f"-{s:.1f}%",
                    ha='center', va='bottom', fontsize=6.8, color='#C0392B', fontweight='bold')
        
        if i == 0:
            ax.set_ylabel('Monthly Cost (USD $)')
            ax.legend(['On-Demand', '1-Yr Commit (RI/CUD)'], frameon=True, fontsize=7.5, loc='upper left')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.tight_layout()
    save_fig(fig, 'fig05_commitment_comparison')

# -------------------------------------------------------------
# FIGURE 6: Storage Pricing Comparison (Discrete vs Linear)
# -------------------------------------------------------------
def generate_fig06():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.6), dpi=300)

    # Panel A: Workloads storage costs
    wls = ['Startup\n(100 GB)', 'Midsize\n(1,000 GB)', 'Data-Heavy\n(5,000 GB)']
    x = np.arange(len(wls))
    w = 0.24

    aws_s = [9.12, 91.20, 456.00]
    az_s = [19.71, 135.17, 946.08] # single P60
    gcp_s = [12.00, 120.00, 600.00]

    ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax1.bar(x - w, aws_s, w, label='AWS gp3 ($0.0912/GB)', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    ax1.bar(x, az_s, w, label='Azure Premium SSD v1', color=C_AZURE, edgecolor='#333333', lw=0.7, zorder=3)
    ax1.bar(x + w, gcp_s, w, label='GCP Balanced PD ($0.12/GB)', color=C_GCP, edgecolor='#333333', lw=0.7, zorder=3)

    # Annotate Azure tiers
    ax1.text(x[0], az_s[0] + 15, "P10 (128 GiB)\n+37% Overhang", ha='center', va='bottom', fontsize=6.2, color=C_AZURE, fontweight='bold')
    ax1.text(x[1], az_s[1] + 25, "P30 (1,024 GiB)\n+10% Overhang", ha='center', va='bottom', fontsize=6.2, color=C_AZURE, fontweight='bold')
    ax1.text(x[2], az_s[2] + 25, "P60 (8,192 GiB)\n+43% Overhang", ha='center', va='bottom', fontsize=6.2, color=C_AZURE, fontweight='bold')

    ax1.set_title('(a) Workload Storage Costs', fontsize=9.0, fontweight='bold')
    ax1.set_ylabel('Monthly Storage Cost (USD $)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(wls, fontsize=7.5)
    ax1.set_ylim(0, 1150)
    ax1.legend(frameon=True, fontsize=6.8, loc='upper left')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Panel B: Stepped curve
    cap_gb = np.linspace(10, 5000, 500)
    aws_curve = cap_gb * 0.0912
    gcp_curve = cap_gb * 0.1200

    tiers = [
        (4, 0.84, 'P1'), (8, 1.68, 'P2'), (16, 3.36, 'P3'), (32, 5.28, 'P4'),
        (64, 10.21, 'P6'), (128, 19.71, 'P10'), (256, 38.01, 'P15'), (512, 73.22, 'P20'),
        (1024, 135.17, 'P30'), (2048, 259.05, 'P40'), (4096, 495.57, 'P50'), (8192, 946.08, 'P60')
    ]

    az_stepped = []
    for g in cap_gb:
        gib = g * 0.9313225746
        matched = next(t[1] for t in tiers if t[0] >= gib)
        az_stepped.append(matched)

    ax2.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax2.plot(cap_gb, aws_curve, label='AWS gp3 (Linear)', color=C_AWS, lw=1.5, zorder=3)
    ax2.plot(cap_gb, gcp_curve, label='GCP pd-balanced (Linear)', color=C_GCP, lw=1.5, linestyle='-.', zorder=3)
    ax2.step(cap_gb, az_stepped, label='Azure Premium SSD v1 (Stepped)', color=C_AZURE, lw=1.8, where='post', zorder=4)

    # Shaded overhang example at 5000 GB
    ax2.scatter([5000], [946.08], color=C_AZURE, s=35, zorder=5)
    ax2.scatter([5000], [456.00], color=C_AWS, s=35, zorder=5)

    ax2.set_title('(b) Stepped vs Linear Capacity Curve', fontsize=9.0, fontweight='bold')
    ax2.set_xlabel('Storage Capacity (GB)')
    ax2.set_ylabel('Monthly Cost (USD $)')
    ax2.set_xlim(0, 5200)
    ax2.set_ylim(0, 1050)
    ax2.legend(frameon=True, fontsize=6.8, loc='upper left')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    save_fig(fig, 'fig06_storage_comparison')

# -------------------------------------------------------------
# FIGURE 7: Egress Cost Comparison
# -------------------------------------------------------------
def generate_fig07():
    tiers = ['100 GB\n(Startup)', '500 GB\n(Midsize)', '2,000 GB\n(Data-Heavy)']
    x = np.arange(len(tiers))
    w = 0.24

    aws_egress = [0.00, 43.72, 207.67]
    az_egress = [0.00, 48.00, 228.00]
    gcp_egress = [0.00, 33.00, 198.00]

    fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=300)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    r1 = ax.bar(x - w, aws_egress, w, label='AWS (100 GB Free, then $0.1093/GB)', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    r2 = ax.bar(x, az_egress, w, label='Azure MGN (100 GB Free, then $0.1200/GB)', color=C_AZURE, edgecolor='#333333', lw=0.7, zorder=3)
    r3 = ax.bar(x + w, gcp_egress, w, label='GCP Standard (200 GB Free, then $0.1100/GB)', color=C_GCP, edgecolor='#333333', lw=0.7, zorder=3)

    # Annotate 100 GB as free
    ax.annotate('100% Free\nTier Allowance', xy=(x[0], 0), xytext=(x[0], 25),
                arrowprops=dict(arrowstyle="->", color='#555555', lw=0.8),
                ha='center', fontsize=7.2, fontweight='bold', color='#2E8540')

    ax.set_ylabel('Monthly Outbound Data Transfer Cost (USD $)')
    ax.set_xticks(x)
    ax.set_xticklabels(tiers, fontweight='bold')
    ax.set_ylim(0, 260)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

    for r in list(r1)[1:] + list(r2)[1:] + list(r3)[1:]:
        h = r.get_height()
        ax.annotate(f"${h:.2f}",
                    xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=7.2, fontweight='bold')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    save_fig(fig, 'fig07_egress_comparison')

# -------------------------------------------------------------
# FIGURE 8: Vendor Lock-in Comparison (Radar Chart)
# -------------------------------------------------------------
def generate_fig08():
    categories = [
        'Egress Tariffs\n(w=0.25)',
        'Proprietary PaaS\n(w=0.25)',
        'Commitment Terms\n(w=0.15)',
        'Commercial Bundling\n(w=0.20)',
        'Migration Tools\n(w=0.15)'
    ]
    N = len(categories)

    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Scores
    aws_scores = [4, 5, 4, 3, 3]
    aws_scores += aws_scores[:1]

    az_scores = [4, 5, 4, 5, 4]
    az_scores += az_scores[:1]

    gcp_scores = [3, 3, 2, 3, 2]
    gcp_scores += gcp_scores[:1]

    fig, ax = plt.subplots(figsize=(5.5, 4.5), subplot_kw=dict(polar=True), dpi=300)

    plt.xticks(angles[:-1], categories, fontsize=8.0, color='#222222')
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4, 5], ["1 (Low)", "2", "3", "4", "5 (High)"], color="#666666", size=7.0)
    plt.ylim(0, 5.2)

    # Plot each provider
    ax.plot(angles, az_scores, linewidth=1.8, linestyle='solid', label='Azure (Weighted: 4.45)', color=C_AZURE)
    ax.fill(angles, az_scores, color=C_AZURE, alpha=0.18)

    ax.plot(angles, aws_scores, linewidth=1.8, linestyle='solid', label='AWS (Weighted: 3.90)', color=C_AWS)
    ax.fill(angles, aws_scores, color=C_AWS, alpha=0.18)

    ax.plot(angles, gcp_scores, linewidth=1.8, linestyle='solid', label='GCP (Weighted: 2.70)', color=C_GCP)
    ax.fill(angles, gcp_scores, color=C_GCP, alpha=0.18)

    plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.15), frameon=True, fontsize=8.0)
    save_fig(fig, 'fig08_lockin_radar')

# -------------------------------------------------------------
# FIGURE 9: Weighted Lock-in Scores
# -------------------------------------------------------------
def generate_fig09():
    providers = ['GCP\n(asia-south1)', 'AWS\n(ap-south-1)', 'Azure\n(centralindia)']
    weighted_scores = [2.70, 3.90, 4.45]
    equal_scores = [2.60, 3.80, 4.40]
    colors = [C_GCP, C_AWS, C_AZURE]

    y = np.arange(len(providers))
    height = 0.45

    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=300)
    ax.grid(axis='x', linestyle='--', alpha=0.5, zorder=0)

    bars = ax.barh(y, weighted_scores, height, color=colors, edgecolor='#333333', lw=0.8, zorder=3)
    ax.scatter(equal_scores, y, color='#2C3E50', s=45, marker='|', zorder=4, label='Equal-Weights Rubric (w=0.20)')

    ax.set_xlabel('Weighted Lock-in Index (Scale: 1.0 = Highly Portable, 5.0 = Severe Lock-in)')
    ax.set_yticks(y)
    ax.set_yticklabels(providers, fontweight='bold', fontsize=9.0)
    ax.set_xlim(0, 5.2)
    ax.legend(frameon=True, loc='lower right', fontsize=8.0)

    for bar, val, eq in zip(bars, weighted_scores, equal_scores):
        w = bar.get_width()
        ax.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f} / 5.00",
                ha='left', va='center', fontsize=8.5, fontweight='bold', color='#222222')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    save_fig(fig, 'fig09_weighted_lockin_scores')

# -------------------------------------------------------------
# FIGURE 10: Lock-in Weight Sensitivity Analysis (Monte Carlo)
# -------------------------------------------------------------
def generate_fig10():
    # 5,000 Dirichlet weight simulations
    np.random.seed(42)
    N_RUNS = 5000
    
    scores = {
        'AWS': np.array([4, 5, 4, 3, 3]),
        'Azure': np.array([4, 5, 4, 5, 4]),
        'GCP': np.array([3, 3, 2, 3, 2])
    }
    
    weights = np.random.dirichlet(np.ones(5), size=N_RUNS)
    
    aws_dist = weights @ scores['AWS']
    az_dist = weights @ scores['Azure']
    gcp_dist = weights @ scores['GCP']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.4), dpi=300, gridspec_kw={'width_ratios': [1.3, 1.0]})

    # Panel A: Boxplot distributions
    ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    box = ax1.boxplot([gcp_dist, aws_dist, az_dist], tick_labels=['GCP', 'AWS', 'Azure'],
                      patch_artist=True, medianprops=dict(color='black', lw=1.2), zorder=3)
    
    box_colors = [C_GCP, C_AWS, C_AZURE]
    for patch, c in zip(box['boxes'], box_colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
        patch.set_edgecolor('#333333')

    ax1.set_title('(a) Lock-in Score Distributions (N=5,000)', fontsize=8.5, fontweight='bold')
    ax1.set_ylabel('Simulated Lock-in Score')
    ax1.set_ylim(1.8, 5.2)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Panel B: Rank Dominance
    az_wins = np.sum((az_dist >= aws_dist) & (az_dist >= gcp_dist))
    aws_wins = np.sum((aws_dist > az_dist))
    gcp_wins = np.sum((gcp_dist > az_dist))

    ax2.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    bars = ax2.bar(['Azure\n#1 Rank', 'AWS\n#1 Rank', 'GCP\n#1 Rank'],
                   [az_wins/N_RUNS*100, aws_wins/N_RUNS*100, gcp_wins/N_RUNS*100],
                   color=[C_AZURE, C_AWS, C_GCP], edgecolor='#333333', lw=0.7, zorder=3)
    
    ax2.text(0, az_wins/N_RUNS*100 + 2, "100.0%\n(Pareto Dominance)", ha='center', va='bottom', fontsize=7.2, fontweight='bold', color=C_AZURE)
    ax2.text(1, 3, "0.0%", ha='center', va='bottom', fontsize=7.2, color='#555555')
    ax2.text(2, 3, "0.0%", ha='center', va='bottom', fontsize=7.2, color='#555555')

    ax2.set_title('(b) Provider Rank Stability', fontsize=8.5, fontweight='bold')
    ax2.set_ylabel('Highest Lock-in Share (%)')
    ax2.set_ylim(0, 115)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    save_fig(fig, 'fig10_lockin_sensitivity')

# -------------------------------------------------------------
# FIGURE 11: Sensitivity Analysis (Azure -10% & Support Tiers)
# -------------------------------------------------------------
def generate_fig11():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.6), dpi=300)

    # Panel A: Azure Compute -10% price reduction
    wls = ['Startup (A)', 'Midsize (B)', 'Data-Heavy (C)']
    x = np.arange(len(wls))
    w = 0.25

    aws_baseline = [111.85, 458.84, 1291.12]
    az_baseline = [122.44, 507.09, 1792.92]
    az_cut10 = [115.07, 477.60, 1733.94]

    ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax1.bar(x - w, aws_baseline, w, label='AWS Baseline Total', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    ax1.bar(x, az_baseline, w, label='Azure Baseline Total', color='#85C1E9', edgecolor='#333333', lw=0.7, zorder=3)
    r_cut = ax1.bar(x + w, az_cut10, w, label='Azure (Compute -10%)', color=C_AZURE, edgecolor='#333333', lw=0.7, hatch='//', zorder=3)

    # Highlight Startup result: AWS STILL CHEAPER
    ax1.annotate('AWS Cheaper by $3.22\n(Needs >= 14.4% Cut)', xy=(x[0]+w, az_cut10[0]), xytext=(x[0]+0.1, 280),
                arrowprops=dict(arrowstyle="->", color='#C0392B', lw=0.9),
                ha='center', fontsize=6.5, fontweight='bold', color='#C0392B')

    ax1.set_title('(a) Impact of -10% Azure Compute Cut', fontsize=8.5, fontweight='bold')
    ax1.set_ylabel('Total Monthly Cost (USD $)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(wls, fontsize=7.5)
    ax1.set_ylim(0, 2050)
    ax1.legend(frameon=True, fontsize=6.8, loc='upper left')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Panel B: Support Plan Sensitivity for Startup Workload
    support_tiers = ['Basic ($0)', 'Developer ($29)', 'Business ($100-$500)']
    x2 = np.arange(len(support_tiers))

    aws_sup = [82.85, 111.85, 182.85]
    az_sup = [93.44, 122.44, 193.44]
    gcp_sup = [97.15, 126.15, 600.06] # GCP $500 support floor!

    ax2.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax2.bar(x2 - w, aws_sup, w, label='AWS', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    ax2.bar(x2, az_sup, w, label='Azure', color=C_AZURE, edgecolor='#333333', lw=0.7, zorder=3)
    ax2.bar(x2 + w, gcp_sup, w, label='GCP', color=C_GCP, edgecolor='#333333', lw=0.7, zorder=3)

    ax2.annotate('GCP $500 Support Floor\nInflates Bill to $600.06', xy=(x2[2]+w, gcp_sup[2]), xytext=(x2[2]-0.3, 490),
                arrowprops=dict(arrowstyle="->", color='#C0392B', lw=0.9),
                ha='center', fontsize=6.5, fontweight='bold', color='#C0392B')

    ax2.set_title('(b) Startup Spend across Support Tiers', fontsize=8.5, fontweight='bold')
    ax2.set_ylabel('Monthly Cost (USD $)')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(support_tiers, fontsize=7.5)
    ax2.set_ylim(0, 700)
    ax2.legend(frameon=True, fontsize=6.8, loc='upper left')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    save_fig(fig, 'fig11_pricing_sensitivity')

# -------------------------------------------------------------
# FIGURE 12: Standard Repatriation versus Cloud Exit Waiver
# -------------------------------------------------------------
def generate_fig12():
    workloads = ['Workload A\n(100 GB Data)', 'Workload B\n(1,000 GB Data)', 'Workload C\n(5,000 GB Data)']
    x = np.arange(len(workloads))
    w = 0.22

    aws_toll = [0.00, 98.37, 535.57]
    az_toll = [0.00, 108.00, 588.00]
    gcp_toll = [0.00, 88.00, 528.00]

    fig, ax = plt.subplots(figsize=(6.8, 4.0), dpi=300)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

    r1 = ax.bar(x - w, aws_toll, w, label='AWS Standard Repatriation Toll', color=C_AWS, edgecolor='#333333', lw=0.7, zorder=3)
    r2 = ax.bar(x, az_toll, w, label='Azure Standard Repatriation Toll', color=C_AZURE, edgecolor='#333333', lw=0.7, zorder=3)
    r3 = ax.bar(x + w, gcp_toll, w, label='GCP Standard Repatriation Toll', color=C_GCP, edgecolor='#333333', lw=0.7, zorder=3)

    # Line showing $0 Exit Waiver
    ax.axhline(0.0, color='#27AE60', lw=2.0, zorder=4)
    ax.scatter(x, [0, 0, 0], color='#27AE60', s=90, marker='o', zorder=5, label='Conditional Cloud-Exit Waiver ($0.00, All Providers)')

    # Callout box for Waiver prerequisites
    callout_text = (
        "Conditional $0 Exit Waiver Prerequisites:\n"
        "• Mandatory permanent account termination\n"
        "• Strict 60-day migration cutover window\n"
        "• Formal advance support ticket approval\n"
        "• Note: Discretionary commercial policy in India\n"
        "  (EU Data Act Art 29 applies strictly to EU)"
    )
    ax.text(0.03, 0.95, callout_text, transform=ax.transAxes, fontsize=6.8,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#EAFAF1', edgecolor='#27AE60', lw=1.2))

    ax.set_ylabel('Egress Repatriation Cost (USD $)')
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontweight='bold')
    ax.set_ylim(-15, 680)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper center', bbox_to_anchor=(0.58, 0.98), fontsize=7.2)

    for r in list(r1)[1:] + list(r2)[1:] + list(r3)[1:]:
        h = r.get_height()
        ax.annotate(f"${h:.2f}",
                    xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=7.0, fontweight='bold')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    save_fig(fig, 'fig12_exit_cost_comparison')

# -------------------------------------------------------------
# FIGURE 13: Porter's Five Forces Diagram (Academic Architecture)
# -------------------------------------------------------------
def generate_fig13():
    fig = plt.figure(figsize=(7.2, 5.2), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_force_card(x, y, w, h, title, threat_level, bullets, bg_color='#F8F9FA', border_color='#2C3E50'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.5",
                                     facecolor=bg_color, edgecolor=border_color, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 2.8, title, ha='center', va='top', fontsize=8.5, fontweight='bold', color='#1A252F')
        
        # Threat badge
        badge_color = '#C0392B' if 'High' in threat_level else ('#27AE60' if 'Low' in threat_level else '#D4AC0D')
        ax.text(x + w/2, y + h - 6.0, f"Force Intensity: {threat_level}", ha='center', va='top',
                fontsize=7.0, fontweight='bold', color=badge_color)
        
        curr_y = y + h - 9.5
        for b in bullets:
            ax.text(x + 1.5, curr_y, f"• {b}", ha='left', va='top', fontsize=6.2, color='#333333')
            curr_y -= 3.0

    def draw_force_arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color='#7F8C8D', lw=1.5, mutation_scale=12))

    # Center: Competitive Rivalry
    draw_force_card(32, 34, 36, 32, "COMPETITIVE RIVALRY", "HIGH (ASYMMETRIC)", [
        "Oligopoly under Sweezy Kinked Demand",
        "Conscious compute parity ($73.73 vs $73.73)",
        "Lock-in rents extracted in storage/egress",
        "AWS (Scale) vs Azure (EA) vs GCP (AI)"
    ], bg_color='#FDEDEC', border_color='#C0392B')

    # Top: Threat of New Entrants
    draw_force_card(28, 72, 44, 26, "THREAT OF NEW ENTRANTS", "VERY LOW", [
        "Massive CAPEX: Sovereign DCs & Subsea Landing Stations",
        "Data Sovereignty compliance under Indian DPDP Act 2023",
        "Ecosystem scale economies & GPU allocation quotas",
        "Domestic providers (Yotta, Tata) lack PaaS breadth"
    ], bg_color='#EBF5FB', border_color='#2980B9')

    # Bottom: Threat of Substitutes
    draw_force_card(28, 2, 44, 26, "THREAT OF SUBSTITUTES", "LOW", [
        "On-premise private clouds require large upfront CAPEX",
        "High Indian customs duties on enterprise IT hardware",
        "Operational talent scarcity for on-prem distributed systems",
        "Viable only for hyper-predictable, legacy steady-state IT"
    ], bg_color='#EAFAF1', border_color='#27AE60')

    # Left: Bargaining Power of Suppliers
    draw_force_card(2, 36, 26, 28, "SUPPLIER POWER", "HIGH", [
        "Nvidia GPU monopoly limits capacity",
        "TSMC silicon foundry dependence",
        "Indian metro power & land costs",
        "Upstream costs pushed to users"
    ], bg_color='#FEF9E7', border_color='#F39C12')

    # Right: Bargaining Power of Buyers
    draw_force_card(72, 36, 26, 28, "BUYER POWER", "LOW TO MODERATE", [
        "High data gravity & exit toll friction",
        "Microsoft Entra ID / 365 entrenchment",
        "Asymmetric power: Startups are price-takers",
        "Volume discounts reserved for large EAs"
    ], bg_color='#F4ECF7', border_color='#8E44AD')

    # Connectors pointing into Center
    draw_force_arrow(50, 72, 50, 66) # Top to Center
    draw_force_arrow(50, 28, 50, 34) # Bottom to Center
    draw_force_arrow(28, 50, 32, 50) # Left to Center
    draw_force_arrow(72, 50, 68, 50) # Right to Center

    save_fig(fig, 'fig13_porters_five_forces')

if __name__ == '__main__':
    print("=== Generating IEEE Conference Figures (fig01 to fig13) ===")
    generate_fig01()
    generate_fig02()
    generate_fig03()
    generate_fig04()
    generate_fig05()
    generate_fig06()
    generate_fig07()
    generate_fig08()
    generate_fig09()
    generate_fig10()
    generate_fig11()
    generate_fig12()
    generate_fig13()
    print("=== All 13 Figures Generated Successfully! ===")
