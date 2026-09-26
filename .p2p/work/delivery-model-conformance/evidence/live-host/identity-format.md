# Live-host product-entry hash format

The unchanged producer `checks/check_p2p_delivery_host.py:29` records SHA-256 of `p2p_filesystem.canonical(entry)`. A complete entry contains path, type, mode and base64 content (or symlink target). These are not hashes of decoded file bytes. `p2p_filesystem.py:22` defines sorted compact UTF-8 JSON with `ensure_ascii=False`.

The initial proof compared these entry hashes with decoded file-byte hashes. That compares different inputs and does not establish candidate drift. The original invocation and summary have not been edited or rerun. The companion independent stdlib check compares all 126 complete entries in both receipts and recomputes the full candidate key; it passes. Its output is retained in `product-identity-check.json`.

Run `python3 check-product-identity.py --candidate ../../candidate.json --live-host .` from this directory. Inspect the producer and canonical serializer independently before accepting the interpretation. This annotation establishes identity format only; host authenticity and requirement verdicts remain for the independent verifier.
