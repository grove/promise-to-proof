import argparse, hashlib, json
from pathlib import Path

parser = argparse.ArgumentParser(description="Check live-host canonical manifest-entry identities, not decoded file-byte hashes.")
parser.add_argument("--candidate", type=Path, required=True)
parser.add_argument("--live-host", type=Path, required=True)
a = parser.parse_args()
c = json.loads(a.candidate.read_text())
def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
key = "snapshot:sha256:" + digest(c["manifest"])
assert key == c["key"]
entries = {e["path"]: digest(e) for e in c["manifest"]}
for name in ("invocation.json", "summary.json"):
    receipt = json.loads((a.live_host / name).read_text())
    assert receipt["product_key"] == key, name
    assert receipt["product_entries_sha256"] == entries, name
summary = json.loads((a.live_host / "summary.json").read_text())
assert summary["passed"] and summary["code_unchanged"] and summary["source_preserved"]
print(json.dumps({"candidate": key, "entry_count": len(entries), "both_receipts_match": True, "source_and_code_preserved": True, "hash_format": "SHA256(canonical JSON manifest entry), including path, type, mode and encoded content or symlink target"}, indent=2))
