import pandas as pd
df = pd.read_csv('scratch/azure_bandwidth_full.csv')
cols = ['productName', 'skuName', 'meterName', 'tierMinimumUnits', 'retailPrice', 'unitOfMeasure', 'type', 'location', 'armRegionName']
print(df[cols].to_string())
