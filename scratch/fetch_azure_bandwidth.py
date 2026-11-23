import requests
import json
import pandas as pd

url = 'https://prices.azure.com/api/retail/prices'
params = {
    'api-version': '2023-01-01-preview',
    'currencyCode': 'USD',
    '$filter': "serviceName eq 'Bandwidth'"
}

rows = []
while url:
    r = requests.get(url, params=params, timeout=60).json()
    items = r.get('Items', [])
    for it in items:
        # Check if it matches Central India or Zone 2
        text = " ".join([str(it.get(k, '')) for k in ['productName', 'skuName', 'meterName', 'location', 'armRegionName']])
        if ('zone 2' in text.lower() or 'centralindia' in text.lower()) and ('data transfer out' in text.lower() or 'outbound' in text.lower()):
            rows.append(it)
    url = r.get('NextPageLink')
    params = None

df = pd.DataFrame(rows)
print(f"Total Bandwidth rows matched: {len(df)}")
df.to_csv('scratch/azure_bandwidth_full.csv', index=False)

# Let's inspect distinct productName and meterName
combos = df[['productName', 'skuName', 'meterName', 'type', 'unitOfMeasure']].drop_duplicates()
print("\nDistinct Product/SKU/Meter combinations:")
print(combos.to_string())
