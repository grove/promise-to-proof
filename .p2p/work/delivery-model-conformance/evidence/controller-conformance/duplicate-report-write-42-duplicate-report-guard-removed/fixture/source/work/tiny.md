# Acceptance contract: tiny

Contract revision: v1
Source: [Specification](../spec.txt)

Intended outcome: greet.py prints hello.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec.txt | greet.py prints hello and exits zero. | Wrong text or failure is rejected. | python3 greet.py | hello plus newline and exit zero | Run python3 greet.py and assert exact output and status. | planned |

## Unresolved gaps

None.
