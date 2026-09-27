# Acceptance contract: greeting

Contract revision: v1
Source: [Specification](../spec.txt)

Intended outcome: Implement the supplied public behavior.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec.txt | greet.py prints hello followed by a newline and exits zero. | Incorrect output, return, or error handling fails. | python3 greet.py | exact stdout and exit status | Execute the public seam and retain assertions and observations. | planned |

## Unresolved gaps

None.
