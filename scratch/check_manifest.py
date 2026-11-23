import json

with open("pricing_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

print("Manifest loaded successfully. Providers:", list(manifest["providers"].keys()))
print("Azure tiers count:", len(manifest["providers"]["Azure"]["storage"]["tiers"]))
print("Azure egress tiers:", manifest["providers"]["Azure"]["egress_tiers"])
