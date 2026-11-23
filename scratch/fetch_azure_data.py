import requests
import json

# 1. Fetch Azure Storage Managed Disks in centralindia
url = 'https://prices.azure.com/api/retail/prices'
filter_query = "serviceName eq 'Storage' and armRegionName eq 'centralindia' and contains(productName, 'Premium SSD Managed Disks')"
params = {
    'api-version': '2023-01-01-preview',
    'currencyCode': 'USD',
    '$filter': filter_query
}

items = []
while url:
    r = requests.get(url, params=params, timeout=60).json()
    items.extend(r.get('Items', []))
    url = r.get('NextPageLink')
    params = None

print(f"Total Storage items fetched: {len(items)}")
lrs = [x for x in items if 'LRS' in x.get('skuName', '') and x.get('type') == 'Consumption' and 'Disks' in x.get('meterName', '')]
for x in sorted(lrs, key=lambda k: k.get('retailPrice', 0)):
    print(f"{x.get('productName')} | {x.get('skuName')} | {x.get('meterName')} | {x.get('unitOfMeasure')} | ${x.get('retailPrice')}")

# Save storage items to json for inspection
with open('scratch/azure_storage_raw.json', 'w') as f:
    json.dump(items, f, indent=2)
