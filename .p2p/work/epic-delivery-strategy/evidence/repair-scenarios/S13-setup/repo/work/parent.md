# Acceptance contract: Name registry
Contract revision: v1
Source: [Registry specification](../specs/registry.md)
Parent: None
Prerequisites: None

| ID | Source | Requirement | Boundaries | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Registry specification | Capture maps a name to a lower-case dictionary key and its original value. | ASCII names; no persistence or network. | registry.capture | Ada becomes {ada: Ada}. | python3 check.py capture | planned |
| R2 | Registry specification | Lookup returns the original captured name for any case of its key. | Missing names return None. | registry.lookup | Captured Ada can be read as ADA. | python3 check.py lookup | planned |
| R3 | Registry specification | Summary prefixes a supplied name with Welcome and one space. | Plain text only. | registry.summary | Ada becomes Welcome Ada. | python3 check.py summary | planned |
| R4 | Registry specification | Capture then lookup then summary preserves Ada as Welcome Ada. | The same candidate supplies all functions. | public function composition | Literal Welcome Ada. | python3 check.py parent | planned |
