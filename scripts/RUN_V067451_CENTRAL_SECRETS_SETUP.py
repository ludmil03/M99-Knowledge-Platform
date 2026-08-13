import getpass, json
from pathlib import Path
from core.central_secrets_v067451 import write_secret,env_vault_config

cfg=json.loads(Path("config/secrets/v0.6.7.4.5.1_central_secrets.json").read_text(encoding="utf-8"))
vault=env_vault_config()

print("M99 v0.6.7.4.5.1 - CENTRAL SECRETS ONE-TIME SETUP")
print("Secrets are written to the central vault, not to Git or local config files.\n")

for channel,spec in cfg["channels"].items():
    print(f"[{channel}]")
    data={}
    for field in spec["fields"]:
        if field=="username":
            data[field]=input("  username: ").strip()
        else:
            data[field]=getpass.getpass(f"  {field}: ")
    write_secret(spec["secret_path"],data,vault)
    print("  stored: YES\n")
print("ALL CHANNEL SECRETS STORED IN CENTRAL VAULT.")
