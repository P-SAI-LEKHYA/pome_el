# Test Scenario: Azure Compute -10% with CORRECT P10 storage ($19.71)

# Baseline Developer Support ($29/mo)
aws_od = 73.73 + 9.12 + 0.0 + 29.0   # $111.85
az_od_baseline = 73.73 + 19.71 + 0.0 + 29.0 # $122.44

# Azure compute decreases by 10%:
az_comp_cut = 73.73 * 0.90 # $66.357
az_od_new = az_comp_cut + 19.71 + 0.0 + 29.0 # $115.067 -> $115.07!

print(f"AWS Workload A OD Total: ${aws_od:.2f}")
print(f"Azure Workload A OD Baseline (with P10): ${az_od_baseline:.2f}")
print(f"Azure Workload A OD with Compute -10%: ${az_od_new:.2f}")

if az_od_new < aws_od:
    print("RESULT: Azure BECOMES CHEAPER than AWS!")
else:
    print(f"RESULT: AWS REMAINS CHEAPER than Azure! AWS is ${aws_od:.2f} vs Azure ${az_od_new:.2f} (AWS wins by ${az_od_new - aws_od:.2f})")

# What percentage cut would Azure need to beat AWS in Workload A?
needed_az_comp = aws_od - (19.71 + 0.0 + 29.0)
needed_cut = (73.73 - needed_az_comp) / 73.73
print(f"To match AWS ($111.85), Azure compute must drop to ${needed_az_comp:.2f}, which is a {needed_cut*100:.1f}% reduction in compute price!")
