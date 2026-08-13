import json
from pathlib import Path
from core.central_secrets_v067451 import env_vault_config,read_secret,redacted_status,SecretsError

cfg=json.loads(Path("config/secrets/v0.6.7.4.5.1_central_secrets.json").read_text(encoding="utf-8"))
v=env_vault_config()
print("M99 v0.6.7.4.5.1 - CENTRAL SECRETS STATUS")
print("Vault:",v.addr)
all_ok=True
for channel,spec in cfg["channels"].items():
    try:
        s=read_secret(spec["secret_path"],v)
        stat=redacted_status(s,spec["fields"])
        ok=all(x=="***REDACTED***" for x in stat.values())
    except Exception as e:
        stat={"error":str(e)};ok=False
    all_ok &= ok
    print(channel,"=>","READY" if ok else "NOT READY","|",stat)
print("CENTRAL_SECRETS_READY:","YES" if all_ok else "NO")
