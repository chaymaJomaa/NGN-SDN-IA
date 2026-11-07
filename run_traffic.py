
import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()

parser.add_argument(
    "--scenario",
    choices=["normal", "anomaly"],
    required=True
)

parser.add_argument(
    "--session",
    required=True
)

parser.add_argument(
    "--split",
    choices=["train", "test"],
    required=True
)

parser.add_argument(
    "--pid-h3",
    type=int,
    required=True
)

args = parser.parse_args()

if not args.session.replace("_", "").isalnum():
    parser.error("Le nom de session doit contenir uniquement lettres, chiffres ou _")

metadata_dir = Path("data/sessions/metadata")
metadata_dir.mkdir(parents=True, exist_ok=True)

output_file = metadata_dir / f"{args.split}_{args.session}.json"

if output_file.exists():
    parser.error(f"Fichier deja existant : {output_file}")

if args.scenario == "normal":
    interval = "0.5"
    count = "120"
else:
    interval = "0.02"
    count = "1500"

command = [
    "ping",
    "-c", count,
    "-i", interval,
    "10.0.0.2"
]

start = time.time()

# La commande sera executee dans le namespace de H3

result = subprocess.run(
    ["sudo", "mnexec", "-a", str(args.pid_h3)] + command,
    capture_output=True,
    text=True
)

end = time.time()

metadata = {
    "scenario": args.scenario,
    "session": args.session,
    "split": args.split,
    "start_timestamp": start,
    "end_timestamp": end,
    "start_utc": datetime.fromtimestamp(
        start, timezone.utc
    ).isoformat(),
    "end_utc": datetime.fromtimestamp(
        end, timezone.utc
    ).isoformat(),
    "interval": interval,
    "count": count,
    "return_code": result.returncode,
    "output": result.stdout,
    "errors": result.stderr
}

with open(output_file, "w") as f:
    json.dump(metadata, f, indent=4)

print("Session terminee")
print("Metadata :", output_file)
print(result.stdout[-500:])
