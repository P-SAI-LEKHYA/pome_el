import requests, pandas as pd

REGION = "centralindia"  # Azure's Mumbai region (West India) is restricted; Pune is the usual choice. State this in your report.
SKUS = {
    "A_Startup":   "Standard_D2s_v5",   # 2 vCPU, 8 GB
    "B_Midsize":   "Standard_D8s_v5",   # 8 vCPU, 32 GB
    "C_DataHeavy": "Standard_D16s_v5",  # 16 vCPU, 64 GB
}

rows = []
for workload, sku in SKUS.items():
    url = "https://prices.azure.com/api/retail/prices"
    params = {
        "api-version": "2023-01-01-preview",
        "currencyCode": "INR",
        "$filter": f"serviceName eq 'Virtual Machines' and armRegionName eq '{REGION}' and armSkuName eq '{sku}'",
    }
    while url:
        data = requests.get(url, params=params, timeout=60).json()
        for item in data.get("Items", []):
            rows.append({
                "workload": workload, "provider": "Azure", "sku": sku,
                "product": item["productName"], "sku_name": item["skuName"],
                "price_type": item["type"], "term": item.get("reservationTerm", ""),
                "unit": item["unitOfMeasure"], "price_inr": item["retailPrice"],
                "effective": item["effectiveStartDate"],
            })
        url, params = data.get("NextPageLink"), None

df = pd.DataFrame(rows)
# keep Linux only, drop Windows, Spot and Low Priority
df = df[~df["product"].str.contains("Windows", case=False)]
df = df[~df["sku_name"].str.contains("Spot|Low Priority", case=False)]
print("rows matched:", len(df))
print(df.to_string())
df.to_csv("azure_prices.csv", index=False)