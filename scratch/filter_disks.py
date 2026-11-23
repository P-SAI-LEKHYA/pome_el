import json

with open('scratch/azure_storage_raw.json') as f:
    items = json.load(f)

disks = []
for x in items:
    # We want standard Premium SSD LRS disks
    m = x.get('meterName', '')
    if x.get('type') == 'Consumption' and m.endswith(' LRS Disk') and 'Mount' not in m and 'Burst' not in m:
        disks.append(x)

# Sort by retailPrice
disks = sorted(disks, key=lambda k: k.get('retailPrice', 0))

print(f"{'SKU':<12} | {'Meter Name':<18} | {'Unit':<10} | {'Price USD':<10}")
print("-" * 55)
for x in disks:
    print(f"{x.get('skuName'):<12} | {x.get('meterName'):<18} | {x.get('unitOfMeasure'):<10} | ${x.get('retailPrice'):.4f}")
