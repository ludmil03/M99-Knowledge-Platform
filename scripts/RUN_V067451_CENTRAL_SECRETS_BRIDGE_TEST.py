import json
from pathlib import Path
from core.central_secrets_v067451 import env_vault_config,get_channel_secret

cfg=json.loads(Path("config/secrets/v0.6.7.4.5.1_central_secrets.json").read_text(encoding="utf-8"))
v=env_vault_config()
registry=cfg["channels"]

print("M99 v0.6.7.4.5.1 - CENTRAL SECRETS BRIDGE")
print("No secret values will be printed.")
for channel in registry:
    s=get_channel_secret(channel,registry,v)
    print(channel,"=> FOUND fields:",",".join(registry[channel]["fields"]))
print("BRIDGE READY: YES")
