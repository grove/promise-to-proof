#!/usr/bin/env python3
"""Explicitly retain a compact measurement from an active or blocked delivery."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "skills/productivity/deliver-issue/scripts"))
import p2p_delivery as delivery
from p2p_delivery_measurements import build, write_export


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        root = Path(delivery.fs.git(Path(args.repo), "rev-parse", "--show-toplevel").decode().strip()).resolve()
        local = delivery.local_directory(root, args.work)
        path = local / "delivery.json"
        if not path.is_file():
            raise ValueError("no active episode record; export before ordinary cleanup")
        state = json.loads(path.read_text())
        record = build(state, delivery.execution_runtime(root, args.work))
        output = write_export(args.output, record)
        print(json.dumps({"status": "EXPORTED", "path": str(output), "episode_id": record["episode_id"]}))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
