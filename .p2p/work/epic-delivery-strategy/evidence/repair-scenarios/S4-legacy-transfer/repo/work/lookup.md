# Acceptance contract: lookup
Contract revision: v1
Source: [Parent contract](parent.md)
Parent: [Parent contract](parent.md) v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; exact text remains at the canonical parent path.
Decomposition: [.p2p/work/parent/slicing.md](../.p2p/work/parent/slicing.md)
Prerequisites: Capture outcome must exist in the actual candidate; issue 101 state alone is insufficient.
Inherited constraints: ASCII names; no persistence, network, or automatic merge.

| ID | Source | Requirement | Boundaries | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | work/parent.md v1:R2 | Lookup a captured name using any case of its key; a missing key returns None. | Parent constraints apply. | registry.lookup | Literal examples in check.py. | python3 check.py lookup | planned |

Parent R4 composition remains part of final parent verification.
