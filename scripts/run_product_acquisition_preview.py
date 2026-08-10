from pathlib import Path
import argparse, json
from core.acquisition_preview import build_preview_from_file

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source_json")
    p.add_argument("--channels",default="config/channels/channel_rules_v0.6.0.json")
    p.add_argument("--output",default="output/acquisition_preview.json")
    a=p.parse_args()
    preview=build_preview_from_file(a.source_json,a.channels)
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(preview,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("M99 Product Acquisition Preview v0.6.1")
    print("======================================")
    print("Mode:",preview["mode"])
    print("M99 ID:",preview["productgroup"]["m99_id"])
    print("Lifecycle:",preview["productgroup"]["lifecycle"])
    print("Variants:",len(preview["variants"]))
    print("Eligible channels:",len(preview["channel_preview"]))
    for x in preview["channel_preview"]:
        print(" -",x["channel"],"=>",x["status"])
    print("Writes to Dolibarr: NO")
    print("Writes to channels: NO")
    print("Operator approval required: YES")
    print("Preview written to:",out)

if __name__=="__main__":
    main()
