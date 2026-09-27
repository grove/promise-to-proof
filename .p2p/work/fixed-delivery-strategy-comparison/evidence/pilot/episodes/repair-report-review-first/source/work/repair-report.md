# Acceptance contract: repair-report

Contract revision: v1
Source: [Specification](../spec.txt)

Intended outcome: Implement the supplied public behavior.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec.txt | report.py exports save_report(path, text), saving supplied text as UTF-8. | Incorrect output, return, or error handling fails. | save_report(path, text) | expected UTF-8 bytes | Execute the public seam and retain assertions and observations. | planned |
| R2 | spec.txt | Overwrite an existing report at the supplied path. | Incorrect output, return, or error handling fails. | save_report(path, text) | replacement contents | Execute the public seam and retain assertions and observations. | planned |
| R3 | spec.txt | Return None after success. | Incorrect output, return, or error handling fails. | save_report(path, text) | return identity is None | Execute the public seam and retain assertions and observations. | planned |
| R4 | spec.txt | Propagate I/O errors to the caller. | Incorrect output, return, or error handling fails. | save_report(path, text) | missing parent raises OSError | Execute the public seam and retain assertions and observations. | planned |

## Unresolved gaps

None.
